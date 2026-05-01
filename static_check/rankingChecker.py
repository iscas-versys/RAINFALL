
#!/usr/bin/env python3
"""
Rank Function Assertion Validator (SV-COMP Standard Final Version)
 Fixed lexicographic/two-phase assertion structure validation
 Strict phase-switch condition validation: new_rank1<0 && old_rank1<0
 Full support for while and for loops
 All error messages and reports in professional English
 Removed ParenExpr references (pycparser compatibility)
 Precise || sub-node extraction for structural validation
"""
import os
import sys
import re
import argparse
from pycparser import c_parser, c_ast

# ==================== Preprocessing Core ====================
def remove_c_comments(text):
    """Safely remove all C comments"""
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    return text

def preprocess_for_pycparser(c_code):
    """Preprocessing pipeline optimized for pycparser"""
    # Convert assert comments to parseable function calls
    c_code = re.sub(
        r'//\s*@?\s*assert\s*\(([^;]+?)\)\s*;|/\*\s*@assert\s*\(([^;]+?)\)\s*\*/',
        lambda m: f'__RANK_ASSERT({m.group(1) if m.group(1) else m.group(2)});',
        c_code
    )
    
    # Remove all comments
    c_code = remove_c_comments(c_code)
    
    # Remove all preprocessor directives
    c_code = re.sub(r'^\s*#.*$', '', c_code, flags=re.MULTILINE)
    
    # Rewrite extern declarations to standard function declarations
    c_code = re.sub(
        r'extern\s+\w+\s+(__VERIFIER_\w+)\s*\([^)]*\)\s*;',
        r'int \1(void);',
        c_code
    )
    
    # Clean whitespace
    c_code = re.sub(r'\n\s*\n', '\n\n', c_code)
    c_code = re.sub(r'[ \t]+$', '', c_code, flags=re.MULTILINE)
    c_code = c_code.strip()
    
    # Inject required base declarations
    header = """typedef unsigned int size_t;
typedef long __builtin_va_list;
void __RANK_ASSERT(int);"""
    return header + "\n\n" + c_code

# ==================== AST Helper Tools ====================
class GuardExtractor(c_ast.NodeVisitor):
    """Extract loop guard expression (supports while and for loops)"""
    def __init__(self): 
        self.expr = None
        self.found = False
    
    def visit_While(self, node):
        if not self.found and self.expr is None:
            self.expr = node.cond
            self.found = True
        return
    
    def visit_For(self, node):
        if not self.found and self.expr is None and node.cond is not None:
            self.expr = node.cond
            self.found = True
        return

class RankCounter(c_ast.NodeVisitor):
    """Count old_rank variable declarations"""
    def __init__(self): 
        self.count = 0
        self.names = []          # 新增：记录变量名
    def visit_Decl(self, node):
        if (isinstance(node.type, c_ast.TypeDecl) and 
            hasattr(node.type.type, 'names') and
            node.name and node.name.startswith('old_rank')):
            self.count += 1
            self.names.append(node.name)   # 新增：收集变量名
        self.generic_visit(node)

class AssertExtractor(c_ast.NodeVisitor):
    """Extract __RANK_ASSERT call conditions"""
    def __init__(self): self.asserts = []
    def visit_FuncCall(self, node):
        if isinstance(node.name, c_ast.ID) and node.name.name == '__RANK_ASSERT':
            if node.args and node.args.exprs:
                self.asserts.append(node.args.exprs[0])
        self.generic_visit(node)

# ==================== Expression Normalization ====================
def normalize_expr(node):
    """Normalize expression for comparison (remove spacing differences)"""
    if node is None: return ""
    class Normalizer(c_ast.NodeVisitor):
        def __init__(self): self.res = []
        def visit_ID(self, n): self.res.append(n.name)
        def visit_Constant(self, n): self.res.append(n.value)
        def visit_BinaryOp(self, n):
            self.visit(n.left); self.res.append(n.op); self.visit(n.right)
        def visit_UnaryOp(self, n):
            self.res.append(n.op); self.visit(n.expr)
        def generic_visit(self, n): super().generic_visit(n)
    norm = Normalizer()
    norm.visit(node)
    return ''.join(norm.res).replace(' ', '')

# ==================== Condition Checker ====================
def _has_condition(node, target_var, target_op, target_val):
    """
    Recursively check if AST node contains specified condition
    target_val: '0' for constant zero, otherwise variable name (e.g., 'new_rank1')
    """
    if node is None:
        return False
    if isinstance(node, c_ast.BinaryOp):
        if node.op == target_op:
            if isinstance(node.left, c_ast.ID) and node.left.name == target_var:
                if target_val == '0':
                    if isinstance(node.right, c_ast.Constant) and node.right.value == '0':
                        return True
                else:
                    if isinstance(node.right, c_ast.ID) and node.right.name == target_val:
                        return True
        return (_has_condition(node.left, target_var, target_op, target_val) or
                _has_condition(node.right, target_var, target_op, target_val))
    if isinstance(node, c_ast.UnaryOp):
        return _has_condition(node.expr, target_var, target_op, target_val)
    return False

# ==================== Structure Validation ====================
def validate_two_phase_decrease(or_node):
    """Validate || node for two-phase rank structure"""
    if not (isinstance(or_node, c_ast.BinaryOp) and or_node.op == '||'):
        return False, "Not a logical OR (||) node"
    
    left, right = or_node.left, or_node.right
    
    if not _has_condition(left, 'old_rank1', '>=', '0'):
        return False, "Left branch missing: old_rank1 >= 0"
    if not _has_condition(left, 'old_rank1', '>', 'new_rank1'):
        return False, "Left branch missing: old_rank1 > new_rank1"
    
    checks = [
        ('new_rank1', '<', '0', "new_rank1 < 0 (phase switch trigger condition)"),
        ('old_rank1', '<', '0', "old_rank1 < 0 (previous iteration already negative)"),
        ('old_rank2', '>=', '0', "old_rank2 >= 0 (current component non-negative)"),
        ('old_rank2', '>', 'new_rank2', "old_rank2 > new_rank2 (current component strictly decreasing)")
    ]
    
    for var, op, val, desc in checks:
        if not _has_condition(right, var, op, val):
            return False, f"Right branch missing: {desc}"
    
    return True, "Two-phase structure complete"

def validate_lexicographic_decrease(or_node):
    """Validate || node for lexicographic rank structure"""
    if not (isinstance(or_node, c_ast.BinaryOp) and or_node.op == '||'):
        return False, "Not a logical OR (||) node"
    
    left, right = or_node.left, or_node.right
    
    if not _has_condition(left, 'old_rank1', '>', 'new_rank1'):
        return False, "Left branch missing: old_rank1 > new_rank1"
    if not _has_condition(right, 'old_rank1', '==', 'new_rank1'):
        return False, "Right branch missing: old_rank1 == new_rank1"
    if not _has_condition(right, 'old_rank2', '>', 'new_rank2'):
        return False, "Right branch missing: old_rank2 > new_rank2"
    
    return True, "Lexicographic structure complete"

def validate_decrease_logic(assert_nodes, rank_cnt, old_rank_names=None):
    """
    Validate decrement logic:
    - For rank_cnt=2 with single assertion: extract || sub-node and validate structure
    - Verify all old_rank >= 0 conditions exist in full assertion
    """
    if rank_cnt == 2 and len(assert_nodes) == 1:
        node = assert_nodes[0]
        
        # Step 1: Extract || sub-node (core decrement comparison)
        or_node = None
        def find_or_node(n):
            nonlocal or_node
            if isinstance(n, c_ast.BinaryOp) and n.op == '||' and or_node is None:
                or_node = n
            if hasattr(n, 'children'):
                for _, child in n.children():
                    if or_node is None:
                        find_or_node(child)
        
        find_or_node(node)
        if or_node is None:
            return False, "Decrement comparison part (||) not found in assertion"
        
        # Step 2: Detect structure type (two-phase vs lexicographic)
        has_less_zero = False
        def detect_less_zero(n):
            nonlocal has_less_zero
            if isinstance(n, c_ast.BinaryOp) and n.op == '<':
                if isinstance(n.right, c_ast.Constant) and n.right.value == '0':
                    has_less_zero = True
            elif isinstance(n, c_ast.BinaryOp):
                detect_less_zero(n.left)
                detect_less_zero(n.right)
            elif isinstance(n, c_ast.UnaryOp):
                detect_less_zero(n.expr)
        
        detect_less_zero(or_node)
        
        # Step 3: Validate || node structure
        if has_less_zero:
            is_valid, msg = validate_two_phase_decrease(or_node)
            if not is_valid:
                return False, f"Two-phase structure error: {msg}"
            struct_type = "Two-phase"
        else:
            is_valid, msg = validate_lexicographic_decrease(or_node)
            if not is_valid:
                return False, f"Lexicographic structure error: {msg}"
            struct_type = "Lexicographic"
        
        # Step 4: Verify all old_rank >= 0 conditions exist in full assertion
        ge0_vars = set()
        def collect_ge0(n):
            if isinstance(n, c_ast.BinaryOp):
                if (n.op == '>=' and 
                    isinstance(n.right, c_ast.Constant) and n.right.value == '0' and
                    isinstance(n.left, c_ast.ID) and n.left.name.startswith('old_rank')):
                    ge0_vars.add(n.left.name)
                collect_ge0(n.left)
                collect_ge0(n.right)
            elif isinstance(n, c_ast.UnaryOp):
                collect_ge0(n.expr)
        
        collect_ge0(node)
        
        expected_old = {f'old_rank{i+1}' for i in range(rank_cnt)}
        missing_ge0 = expected_old - ge0_vars
        if missing_ge0:
            return False, f"Missing non-negative conditions for old_rank: {sorted(missing_ge0)}"
        
        return True, f"{struct_type} structure validated (with non-negative conditions)"
    
    # Fallback validation for other cases
    return _fallback_loose_check(assert_nodes, rank_cnt, old_rank_names)

def _fallback_loose_check(assert_nodes, rank_cnt, old_rank_names=None):
    """Fallback validation for non-two-phase/non-lexicographic cases"""
    has_gt = False
    ge0_vars = set()
    
    def traverse(n):
        nonlocal has_gt
        if isinstance(n, c_ast.BinaryOp):
            if n.op == '>':
                if (isinstance(n.left, c_ast.ID) and n.left.name.startswith('old_rank') and
                    isinstance(n.right, c_ast.ID) and n.right.name.startswith('new_rank')):
                    has_gt = True
            elif (n.op == '>=' and 
                  isinstance(n.right, c_ast.Constant) and n.right.value == '0' and
                  isinstance(n.left, c_ast.ID) and n.left.name.startswith('old_rank')):
                ge0_vars.add(n.left.name)
            traverse(n.left)
            traverse(n.right)
        elif isinstance(n, c_ast.UnaryOp):
            traverse(n.expr)
    
    for node in assert_nodes:
        traverse(node)
    
    if not has_gt:
        return False, "Missing old_rank > new_rank comparison"
    
    # 🔧 关键修改：优先使用实际收集到的变量名，回退到数字后缀推断
    if old_rank_names is not None:
        expected_old = set(old_rank_names)
    else:
        expected_old = {f'old_rank{i+1}' for i in range(rank_cnt)}
    
    missing_ge0 = expected_old - ge0_vars
    if missing_ge0:
        return False, f"Missing non-negative conditions for old_rank: {sorted(missing_ge0)}"
    
    return True, ""
# ==================== Assertion Validation ====================
def is_termination_assert(node, guard_norm):
    """Identify termination assertion: (...) || !(guard)"""
    if not (isinstance(node, c_ast.BinaryOp) and node.op == '||'):
        return False
    if not (isinstance(node.right, c_ast.UnaryOp) and node.right.op == '!'):
        return False
    return guard_norm in normalize_expr(node.right.expr)

def validate_termination_assert(node, rank_cnt, guard_norm):
    """Validate termination assertion: (at least one new_rankX >= 0) || !(guard)"""
    if not (isinstance(node, c_ast.BinaryOp) and node.op == '||'):
        return False
    if not (isinstance(node.right, c_ast.UnaryOp) and node.right.op == '!'):
        return False
    if guard_norm not in normalize_expr(node.right.expr):
        return False
    
    has_ge0 = False
    def check_ge0(n):
        nonlocal has_ge0
        if isinstance(n, c_ast.BinaryOp):
            if (n.op == '>=' and 
                isinstance(n.right, c_ast.Constant) and n.right.value == '0' and
                isinstance(n.left, c_ast.ID) and n.left.name.startswith('new_rank')):
                has_ge0 = True
            check_ge0(n.left)
            check_ge0(n.right)
        elif isinstance(n, c_ast.UnaryOp):
            check_ge0(n.expr)
    
    check_ge0(node.left)
    return has_ge0

def validate_c_file(c_code, filename="", verbose=False):
    """Validate single C file"""
    try:
        processed = preprocess_for_pycparser(c_code)
    except Exception as e:
        return False, f"Preprocessing exception: {str(e)[:100]}"
    
    try:
        parser = c_parser.CParser()
        ast = parser.parse(processed, filename='<input>')
    except Exception as e:
        err_msg = str(e).split('\n')[0][:150]
        return False, f"AST parsing failed: {err_msg}"
    
    # Extract loop guard
    guard_ext = GuardExtractor()
    guard_ext.visit(ast)
    if guard_ext.expr is None:
        return False, "No loop (while or for) detected with guard condition"
    guard_norm = normalize_expr(guard_ext.expr)
    
    # Count rank variables
    rank_counter = RankCounter()
    rank_counter.visit(ast)
    rank_cnt = rank_counter.count
    if rank_cnt == 0:
        return False, "No old_rank variables detected"
    
    # Locate loop node
    class LoopLocator(c_ast.NodeVisitor):
        def __init__(self): 
            self.loop = None
            self.found = False
        
        def visit_While(self, node):
            if not self.found and self.loop is None:
                self.loop = node
                self.found = True
            return
        
        def visit_For(self, node):
            if not self.found and self.loop is None:
                self.loop = node
                self.found = True
            return
    
    locator = LoopLocator()
    locator.visit(ast)
    if locator.loop is None:
        return False, "No loop node (while or for) found"
    
    # Process loop body
    loop_body = locator.loop.stmt
    if not isinstance(loop_body, c_ast.Compound):
        if loop_body is not None:
            loop_body = c_ast.Compound(block_items=[loop_body])
        else:
            return False, "Loop body is empty"
    
    # Extract assertions in loop body
    assert_ext = AssertExtractor()
    assert_ext.visit(loop_body)
    assert_nodes = assert_ext.asserts
    
    if len(assert_nodes) not in [2, 3, 4]:
        return False, f"Loop requires 2 or 3 assertions (SV-COMP standard), found {len(assert_nodes)}"
    
    # Classify assertions
    term_assert = None
    decr_asserts = []
    for expr in assert_nodes:
        if is_termination_assert(expr, guard_norm):
            if term_assert is not None:
                return False, "Multiple termination assertions detected"
            term_assert = expr
        else:
            decr_asserts.append(expr)
    
    if term_assert is None:
        return False, "Termination assertion not found (should contain || !(guard) structure)"
    if not (1 <= len(decr_asserts) <= 3):
        return False, f"Decrement logic assertions count error: {len(decr_asserts)} (expected 1 to 3)"
    
    # Validate termination assertion
    if not validate_termination_assert(term_assert, rank_cnt, guard_norm):
        return False, f"Termination assertion invalid | guard='{guard_norm}'"
    
    # Validate decrement logic
    old_rank_names = rank_counter.names
    decr_valid, decr_msg = validate_decrease_logic(decr_asserts, rank_cnt, old_rank_names)
    if not decr_valid:
        return False, f"Decrement logic invalid: {decr_msg}"
    
    return True, f"Validation passed | rank_cnt={rank_cnt} | assert_cnt={len(assert_nodes)}"

# ==================== Batch Processing ====================
def get_c_files(directory):
    """Safely get all .c files from directory"""
    files = []
    for entry in os.listdir(directory):
        if entry.startswith('.') or not os.path.isfile(os.path.join(directory, entry)):
            continue
        if entry.lower().endswith('.c'):
            files.append(entry)
    return sorted(files)

def main():
    parser = argparse.ArgumentParser(
        description="Rank Function Assertion Validator (SV-COMP Standard)",
        epilog="Example: %(prog)s ./sv-benchmarks/c/termination-crafted -v"
    )
    parser.add_argument('dir_path', help='Directory path containing C programs')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed validation process')
    args = parser.parse_args()
    
    if not os.path.isdir(args.dir_path):
        print(f" Error: '{args.dir_path}' is not a valid directory", file=sys.stderr)
        sys.exit(11)
    
    c_files = get_c_files(args.dir_path)
    if not c_files:
        print(f"  Warning: No .c files found in directory '{args.dir_path}'")
        sys.exit(0)
    
    print(f" Validation directory: {os.path.abspath(args.dir_path)}")
    print(f" Found {len(c_files)} C source files, starting validation...\n")
    
    results = []
    for idx, fname in enumerate(c_files, 1):
        fpath = os.path.join(args.dir_path, fname)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
        except Exception as e:
            results.append((fname, False, f"File read failed: {e}"))
            continue
        
        if args.verbose:
            print(f"\n{'='*65}")
            print(f"🔍 [{idx}/{len(c_files)}] {fname}")
            print(f"{'='*65}")
        
        try:
            success, msg = validate_c_file(code, fname, args.verbose)
        
            results.append((fname, success, msg))
        except Exception as e:
            results.append((fname, False, f"Validation exception: {str(e)[:150]}"))
    
    # Generate summary report
    print("\n" + "="*65)
    print(" Validation Summary Report")
    print("="*65)
    
    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]
    
    print(f"\n Passed: {len(passed)}")
    for f, _, m in passed:
        print(f"   • {f} ({m})")
    
    print(f"\n Failed: {len(failed)}")
    for f, _, m in failed:
        if "No loop" in m or "requires 2 or 3 assertions" in m:
            print(f"   • {f}")
            print(f"      └─ {m}")
        else:
            print(f"   • {f} | {m}")
    
    print("\n" + "="*65)
    print(f" Total: {len(results)} | Passed: {len(passed)} | Failed: {len(failed)}")
    print("="*65)
    
    # Exit code: 0 if no critical failures, 1 otherwise
    critical_failures = [r for r in failed if "No loop" not in r[2] and "requires 2 or 3 assertions" not in r[2]]
    sys.exit(0 if len(critical_failures) == 0 else 1)

if __name__ == '__main__':
    try:
        import pycparser
    except ImportError:
        print(" Dependency missing: Please install pycparser", file=sys.stderr)
        print("   Run: pip install pycparser", file=sys.stderr)
        sys.exit(1)
    
    main()
