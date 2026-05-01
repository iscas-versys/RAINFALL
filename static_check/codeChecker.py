
#!/usr/bin/env python3
"""
Rank Function Consistency Checker (AST-based) - Single-Loop Optimized Version
[Core improvement] Completely remove guard matching logic, directly locate the only while loop in the program
"""
import sys
import re
import os
import argparse
from pycparser import c_parser, c_ast
from pycparser.c_generator import CGenerator

# ==================== AST Helper Tools ====================
class ExpressionNormalizer(c_ast.NodeVisitor):
    def __init__(self):
        self.result = []
    
    def normalize(self, node):
        if node is None:
            return ""
        self.result = []
        self.visit(node)
        return ''.join(self.result)
    
    def visit_Constant(self, node): self.result.append(node.value)
    def visit_ID(self, node): self.result.append(node.name)
    def visit_BinaryOp(self, node):
        self.result.append('('); self.visit(node.left); self.result.append(node.op); self.visit(node.right); self.result.append(')')
    def visit_TernaryOp(self, node):
        self.result.append('('); self.visit(node.cond); self.result.append('?'); self.visit(node.iftrue); self.result.append(':'); self.visit(node.iffalse); self.result.append(')')
    def visit_UnaryOp(self, node):
        self.result.append(node.op); self.visit(node.expr)
    def generic_visit(self, node): super().generic_visit(node)
def is_integer_rank_type(decl_type):
    """
    判断声明类型是否是整数类型。
    支持 int / long / long long / unsigned long long 等。
    """
    if not isinstance(decl_type, c_ast.TypeDecl):
        return False

    if not isinstance(decl_type.type, c_ast.IdentifierType):
        return False

    names = decl_type.type.names

    if 'int' in names:
        return True

    if 'long' in names:
        return True

    return False
class RankExtractor(c_ast.NodeVisitor):
    def __init__(self):
        self.old_ranks = []
        self.new_ranks_init = {}      # 最终存储初始化表达式
        self.new_ranks_declared = set()  # 记录已声明但未初始化的 new_rank 变量
        self.assignments = []
        self.in_loop = False          # 辅助标记是否已进入循环

    def visit_Decl(self, node):
        if is_integer_rank_type(node.type):
            var_name = node.name
            if var_name and var_name.startswith('old_rank'):
                self.old_ranks.append((var_name, node))
            elif var_name and var_name.startswith('new_rank'):
                if node.init:
                    norm_expr = ExpressionNormalizer().normalize(node.init)
                    self.new_ranks_init[var_name] = norm_expr
                else:
                    self.new_ranks_declared.add(var_name)   # 记录待匹配
        self.generic_visit(node)

    def visit_While(self, node):
        self.in_loop = True
        self.generic_visit(node)
        self.in_loop = False

    def visit_Assignment(self, node):
        if isinstance(node.lvalue, c_ast.ID):
            lhs = node.lvalue.name
            # 在循环体之前，若遇到对 new_rank 的赋值且尚未记录初始化表达式，则捕获
            if not self.in_loop and lhs in self.new_ranks_declared:
                if lhs not in self.new_ranks_init:
                    norm_expr = ExpressionNormalizer().normalize(node.rvalue)
                    self.new_ranks_init[lhs] = norm_expr
                    print(f"[DEBUG] Found new_rank variable (via assignment): {lhs} = {norm_expr}")
            # 原有逻辑：记录所有 rank 相关赋值（用于后续检查）
            if lhs and (lhs.startswith('old_rank') or lhs.startswith('new_rank')):
                self.assignments.append((lhs, node.rvalue, node))
        self.generic_visit(node)

class LoopLocator(c_ast.NodeVisitor):
    """Locate the first while loop in the program (the problem guarantees a single loop)"""
    def __init__(self):
        self.target_loop = None
    
    def visit_While(self, node):
        # Capture the first while encountered (the problem guarantees a single loop)
        if self.target_loop is None:
            self.target_loop = node
            print("[DEBUG] ✅ Captured the first while loop node (program contains only a single loop)")
        # Regardless of capture, skip traversing the loop body (saves overhead and avoids nested interference)
        return  # do not call generic_visit
    def visit_For(self, node):
        if self.target_loop is None:
            self.target_loop = node
        return
    def get_loop(self):
        return self.target_loop


# ==================== Core Checking Logic ====================
def split_loop_body(loop_node):
    # 1. 提取循环体中的语句列表
    if isinstance(loop_node.stmt, c_ast.Compound):
        body_stmts = loop_node.stmt.block_items or []
    else:
        # 循环体可能是单条语句（极少见，但处理更健壮）
        body_stmts = [loop_node.stmt] if loop_node.stmt else []

    begin_part, end_part = [], []
    in_begin = True

    for stmt in body_stmts:
        # 判断是否为 old_rank = ... 的赋值
        is_old_rank_assign = (
            isinstance(stmt, c_ast.Assignment) and 
            isinstance(stmt.lvalue, c_ast.ID) and
            stmt.lvalue.name.startswith('old_rank')
        )
        if in_begin and is_old_rank_assign:
            begin_part.append(stmt)
        else:
            in_begin = False
            end_part.append(stmt)

    # 2. 若为 for 循环，将迭代表达式追加到 end_part（作为循环体末尾的更新语句）
    if isinstance(loop_node, c_ast.For) and loop_node.next:
        end_part.append(loop_node.next)

    return begin_part, end_part

def check_old_rank_assignments(begin_part, old_ranks, new_ranks):
    assign_map = {}
    gen = CGenerator()
    for stmt in begin_part:
        if isinstance(stmt, c_ast.Assignment) and isinstance(stmt.rvalue, c_ast.ID):
            assign_map[stmt.lvalue.name] = stmt.rvalue.name
            print(f"[DEBUG] Loop start assignment: {stmt.lvalue.name} = {stmt.rvalue.name}")
    
    errors = []
    print(f"\n[Check] Verifying loop start assignments (total {len(old_ranks)} old_rank variables):")
    for i, (old_var, _) in enumerate(old_ranks):
        if i >= len(new_ranks):
            break
        expected_new = new_ranks[i][0]
        actual = assign_map.get(old_var)
        status = "✓" if actual == expected_new else "✗"
        print(f"  {status} {old_var}: expected = {expected_new}, actual = {actual if actual else 'not assigned'}")
        if actual != expected_new:
            errors.append(f"Expected {old_var} = {expected_new}, got {old_var} = {actual or '?'}")
    return errors

def check_new_rank_updates(end_part, new_ranks_init):
    updates = {}
    gen = CGenerator()
    for stmt in end_part:
        if (isinstance(stmt, c_ast.Assignment) and 
            isinstance(stmt.lvalue, c_ast.ID) and
            stmt.lvalue.name in new_ranks_init):
            var = stmt.lvalue.name
            expr_norm = ExpressionNormalizer().normalize(stmt.rvalue)
            updates.setdefault(var, []).append(expr_norm)
            print(f"[DEBUG] Update inside loop: {var} = {expr_norm}")
    
    errors = []
    print(f"\n[Check] Verifying new_rank update expression consistency (total {len(new_ranks_init)} variables):")
    for var, init_expr in new_ranks_init.items():
        print(f"\n  Variable: {var}")
        print(f"    Initialization expression: {init_expr}")
        if var not in updates:
            print(f"    ✗ No update found inside loop body!")
            errors.append(f"{var} is not updated inside the loop body")
        elif len(updates[var]) > 1:
            print(f"    ✗ Updated {len(updates[var])} times (should be exactly 1)")
            errors.append(f"{var} is updated multiple times")
        else:
            update_expr = updates[var][0]
            match = "✓" if update_expr == init_expr else "✗"
            print(f"    Loop update expression: {update_expr} {match}")
            if update_expr != init_expr:
                errors.append(f"{var} update expression mismatch: initialization='{init_expr}', loop='{update_expr}'")
    return errors

def preprocess_c_code(c_code):
    print("\n[Step] Preprocessing C code: remove preprocessor directives + all comments")
    print(f"  Original code lines: {len(c_code.splitlines())}")
    
    # 1. Remove all preprocessor directives (#include, #define, etc.)
    c_code = re.sub(r'^\s*#.*$', '', c_code, flags=re.MULTILINE)
    print(f"  → Lines after removing preprocessor directives: {len(c_code.splitlines())}")
    
    # 2. Thoroughly remove all C comments (block comments + line comments)
    def remove_c_comments(text):
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
        return text
    
    c_code = remove_c_comments(c_code)
    print(f"  → Lines after removing all comments: {len(c_code.splitlines())}")
    
    # 3. Clean up leftover whitespace and blank lines
    c_code = re.sub(r'[ \t]+$', '', c_code, flags=re.MULTILINE)
    c_code = re.sub(r'\n\s*\n', '\n\n', c_code)
    c_code = c_code.strip() + '\n'
    print(f"  → Lines after cleaning whitespace/blank lines: {len(c_code.splitlines())}")
    
    # 4. Print key snippet after preprocessing (verify comments are cleaned)
    snippet_lines = c_code.strip().split('\n')[:15]
    print("\n[DEBUG] First 15 lines after preprocessing (verify no # or //):")
    for i, line in enumerate(snippet_lines, 1):
        if '#' in line or '//' in line or '/*' in line:
            print(f"  {i:2d}. [!] {line[:70]}")
        else:
            print(f"  {i:2d}.     {line[:70]}")
    print(f"\n[DEBUG] Preprocessing done, ready for AST parsing")
    return c_code

def check_rank_consistency(c_code, guard_input = "", verbose=False):
    # ============ [Core change] Completely ignore guard_input, directly locate the only loop ============
    print("="*60)
    print("🔍 Starting rank consistency check | Strategy: locate the first while loop in the program (single loop)")
    print(f"[INFO] ℹ️  Ignoring guard parameter: '{guard_input}' (program contains only one while loop)")
    print("="*60)
    
    # Preprocess
    clean_code = preprocess_c_code(c_code)
    
    # AST parsing
    print("\n[Step] Parsing C code into AST...")
    try:
        parser = c_parser.CParser()
        ast = parser.parse(clean_code, filename='<input>')
        print("[DEBUG] AST parsing successful ✓")
    except Exception as e:
        print(f"[ERROR] AST parsing failed: {e}")
        return 6, f"AST parsing failed: {str(e)}"
    
    # Locate loop (directly capture the first while)
    print("\n[Step] Locating the first while loop in the program (single loop)...")
    locator = LoopLocator()
    locator.visit(ast)
    loop_node = locator.get_loop()
    
    if loop_node is None:
        print("[ERROR] ❌ No while loop node found")
        return 5, "No while loop exists in AST (please confirm the code contains a loop structure)"
    print("[DEBUG] ✓ Successfully located target loop node")
    # ======================================================================
    
    # Extract variables
    print("\n[Step] Extracting rank-related variables...")
    extractor = RankExtractor()
    extractor.visit(ast)
    old_ranks = extractor.old_ranks
    new_ranks = [(name, None) for name in extractor.new_ranks_init.keys()]
    
    print(f"\n[Statistics] Extraction results:")
    print(f"  old_rank variables ({len(old_ranks)}): {[n for n,_ in old_ranks]}")
    print(f"  new_rank variables ({len(new_ranks)}): {list(extractor.new_ranks_init.keys())}")
    if len(old_ranks) == 0 and len(new_ranks) == 0:
        print("[ERROR] ❌ No rank variables (old_rank / new_rank) found in the program.")
        return 2, {
            'inf': "Missing required rank variable declarations. Expected at least one old_rank and one new_rank variable."
        }
    if len(old_ranks) != len(new_ranks):
        print(f"[ERROR] Variable count mismatch! old={len(old_ranks)}, new={len(new_ranks)}")
        return 2, {
            'old_count': len(old_ranks),
            'new_count': len(new_ranks),
            'count': len(old_ranks),
            'old_vars': [n for n, _ in old_ranks],
            'new_vars': [n for n, _ in new_ranks],
            'inf': f"[ERROR] Variable count mismatch! old={len(old_ranks)}, new={len(new_ranks)}"
        }
    
    # Split loop body
    print("\n[Step] Splitting loop body statements...")
    begin_part, end_part = split_loop_body(loop_node)
    
    # Check 1: Loop start assignments
    print("\n[Step] Checking loop start assignments (old_rank = new_rank)...")
    errors_start = check_old_rank_assignments(begin_part, old_ranks, new_ranks)
    if errors_start:
        print(f"\n[✗] Loop start assignment check failed ({len(errors_start)} errors)")
        return 3, {'errors': errors_start, 'count': len(old_ranks),
            'inf': f"Loop start assignment check failed ({len(errors_start)} errors)"}
    else:
        print("[✓] Loop start assignment check passed")
    
    # Check 2: Update expression consistency
    print("\n[Step] Checking new_rank update expression consistency...")
    errors_update = check_new_rank_updates(end_part, extractor.new_ranks_init)
    if errors_update:
        print(f"\n[✗] Update expression check failed ({len(errors_update)} errors)")
        return 4, {'errors': errors_update, 'count': len(old_ranks),
            'inf': f"Update expression check failed ({len(errors_update)} errors)"}
    else:
        print("[✓] Update expression consistency check passed")
    
    print("\n" + "="*60)
    print("✅ All checks passed! Rank update logic conforms to verification specification")
    print("="*60)
    return 1, {'count': len(old_ranks)}

# ==================== CLI Entry ====================
def get_c_files(directory):
    """Safely get all .c files in a directory (ignore hidden files, skip non-file entries)"""
    if not os.path.isdir(directory):
        raise ValueError(f"Path '{directory}' is not a valid directory")
    
    c_files = []
    for entry in os.listdir(directory):
        # Skip hidden files/directories (starting with .) and non-file items
        if entry.startswith('.') or not os.path.isfile(os.path.join(directory, entry)):
            continue
        if entry.lower().endswith('.c'):
            c_files.append(entry)
    return sorted(c_files)

def main():
    print(11111)
    parser = argparse.ArgumentParser(
        description="Rank consistency batch checker - analyze all C programs in a folder (ignores guard parameter automatically)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s ./test_cases "x>0"   # analyze all .c files in test_cases directory (guard parameter ignored)
  %(prog)s ./code -v             # enable verbose logging (guard parameter still required but ignored)
Note: The guard parameter is completely ignored in batch mode because the program only handles single-loop structures.
        """
    )
    parser.add_argument('dir_path', help='Path to the folder containing C programs')
    parser.add_argument('guard', help='(placeholder parameter) Loop guard condition (ignored in batch mode)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed debug logs')
    
    args = parser.parse_args()
    
    # Validate directory existence
    if not os.path.exists(args.dir_path):
        print(f"❌ Error: Path '{args.dir_path}' does not exist", file=sys.stderr)
        sys.exit(11)
    if not os.path.isdir(args.dir_path):
        print(f"❌ Error: '{args.dir_path}' is not a directory", file=sys.stderr)
        sys.exit(12)
    
    # Get list of C files
    try:
        c_files = get_c_files(args.dir_path)
    except Exception as e:
        print(f"❌ Directory scan failed: {e}", file=sys.stderr)
        sys.exit(13)
    
    if not c_files:
        print(f"⚠️  Warning: No .c files found in directory '{args.dir_path}'")
        sys.exit(0)
    
    print(f"📁 Scanning directory: {os.path.abspath(args.dir_path)}")
    print(f"📋 Found {len(c_files)} C source files, starting batch analysis...\n")
    
    # Result storage: [(filename, status, details)]
    results = []
    STATUS_MSG = {
        1: ("✅ PASS", "All rank variable update logic conforms to specification"),
        2: ("❌ Variable count mismatch", "old_rank and new_rank counts are inconsistent"),
        3: ("❌ Loop start assignment error", "old_rank did not correctly preserve previous new_rank value"),
        4: ("❌ Update expression inconsistency", "new_rank update logic inside loop does not match initialization"),
        5: ("❌ Target loop not found", "No while loop exists in AST"),
        6: ("❌ AST parsing failed", "C code syntax error or contains unsupported syntax"),
        10: ("❌ File read failure", "Cannot read source file")
    }
    
    # Analyze each file
    for idx, filename in enumerate(c_files, 1):
        filepath = os.path.join(args.dir_path, filename)
        print(f"\n{'='*70}")
        print(f"🔍 [{idx}/{len(c_files)}] Analyzing: {filename}")
        print(f"{'='*70}")
        
        # Read file content
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                c_code = f.read()
            print(f"📄 File size: {len(c_code)} characters")
        except Exception as e:
            err_msg = f"File read exception: {str(e)}"
            print(f"❌ {err_msg}")
            results.append((filename, 10, err_msg))
            continue
        
        # Run check (guard parameter is ignored internally)
        try:
            status, details = check_rank_consistency(c_code, args.guard, verbose=args.verbose)
        except Exception as e:
            status, details = 7, f"Check process exception: {str(e)}"
            print(f"⚠️  Unexpected error during check: {e}")
        
        results.append((filename, status, details))
    
    # ===== Generate summary report =====
    print("\n" + "="*70)
    print("📊 Batch Check Summary Report")
    print("="*70)
    
    # Group by status
    stats = {k: [] for k in STATUS_MSG.keys()}
    for filename, status, _ in results:
        stats[status].append(filename)
    
    # Print file lists per status
    total = len(results)
    passed = len(stats[1])
    failed = total - passed
    
    print(f"\n✅ PASS: {passed} files")
    if stats[1]:
        for f in stats[1]:
            print(f"   • {f}")
    
    print(f"\n❌ FAIL: {failed} files")
    for status_code in sorted(stats.keys()):
        if status_code == 1 or not stats[status_code]:  # skip PASS and empty entries
            continue
        symbol, desc = STATUS_MSG.get(status_code, ("⚠️", "Unknown error"))
        print(f"\n{symbol} {desc} ({len(stats[status_code])} files):")
        for f in stats[status_code]:
            print(f"   • {f}")
    
    # Final statistics
    print("\n" + "="*70)
    print(f"📈 Total: {total} files | PASS: {passed} | FAIL: {failed}")
    print("="*70)
    
    # Exit code: 0 if all passed, 1 if any failed
    sys.exit(0 if failed == 0 else 1)

if __name__ == '__main__':
    print(2222)
    try:
        import pycparser
    except ImportError:
        print("❌ Missing dependency: please install pycparser", file=sys.stderr)
        print("   Run: pip install pycparser", file=sys.stderr)
        sys.exit(1)
    main()
