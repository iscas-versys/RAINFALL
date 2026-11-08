
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
# ==================== Ranking-Expression Purity Check ====================
# Expressions assigned to the ghost ranking variables in the first and third
# slots must be pure expressions built from program variables and constants.
# Function calls, assignments to program variables, and increment/decrement
# expressions on program variables are rejected. Other C expression forms are
# left to the subsequent checks and to the verifier.

def expr_to_text(node):
    try:
        return CGenerator().visit(node)
    except Exception:
        return '<unparseable expression>'

class RankingExpressionGrammarChecker(c_ast.NodeVisitor):
    def __init__(self, scopes, text):
        self.scopes = scopes
        self.text = text
        self.errors = []

    def reject(self, reason):
        self.errors.append(
            f"Ranking expression '{self.text}' contains disallowed construct: {reason}.")

    def resolve(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def visit_Assignment(self, node):
        self.reject('assignment expression')

    def visit_FuncCall(self, node):
        try:
            name = node.name.name
        except AttributeError:
            name = '<call>'
        self.reject(f"function call '{name}(...)'")

    def visit_UnaryOp(self, node):
        if node.op in ('p++', 'p--', '++', '--'):
            self.reject('increment/decrement')
            return
        if node.expr is not None:
            self.visit(node.expr)

    def visit_StructRef(self, node):
        if node.name is not None:
            self.visit(node.name)

    def visit_ID(self, node):
        name = node.name
        if name.startswith('old_rank') or name.startswith('new_rank'):
            self.reject(f"reference to ghost variable '{name}'; only original program variables are allowed")
            return
        if self.resolve(name) is None:
            self.reject(f"undeclared or macro identifier '{name}'")


class RankingExpressionCollector(c_ast.NodeVisitor):
    """Collect new_rank expressions with lexical scope information and check them."""

    def __init__(self):
        self.scopes = [{}]
        self.errors = []

    def declare(self, name, node):
        if not name or isinstance(node.type, c_ast.FuncDecl):
            return
        self.scopes[-1][name] = node

    def check_expr(self, node):
        text = expr_to_text(node)
        checker = RankingExpressionGrammarChecker(self.scopes, text)
        checker.visit(node)
        for error in checker.errors:
            if error not in self.errors:
                self.errors.append(error)

    def visit_FileAST(self, node):
        for ext in node.ext:
            self.visit(ext)

    def visit_FuncDef(self, node):
        self.scopes.append({})
        args = node.decl.type.args
        if args is not None:
            for param in args.params:
                self.declare(param.name, param)
        self.visit(node.body)
        self.scopes.pop()

    def visit_Compound(self, node):
        self.scopes.append({})
        for item in node.block_items or []:
            self.visit(item)
        self.scopes.pop()

    def visit_Decl(self, node):
        if node.name and node.name.startswith('new_rank') and node.init is not None:
            self.check_expr(node.init)
        self.declare(node.name, node)

    def visit_Assignment(self, node):
        if isinstance(node.lvalue, c_ast.ID) and node.lvalue.name.startswith('new_rank'):
            self.check_expr(node.rvalue)
        self.generic_visit(node)


GHOST_NAME_RE = re.compile(r'^(old_rank|new_rank)(\d+)$')


class RankDeclScanner(c_ast.NodeVisitor):
    """Collect ghost declarations together with whether they sit inside the loop body."""

    def __init__(self, loop_node):
        self.loop_node = loop_node
        self.in_loop = 0
        self.decls = []

    def _visit_loop(self, node):
        if node is self.loop_node:
            self.in_loop += 1
            body = node.stmt
            if isinstance(body, c_ast.Compound):
                for item in body.block_items or []:
                    self.visit(item)
            elif body is not None:
                self.visit(body)
            self.in_loop -= 1
        else:
            self.generic_visit(node)

    def visit_While(self, node):
        self._visit_loop(node)

    def visit_For(self, node):
        self._visit_loop(node)

    def visit_DoWhile(self, node):
        self._visit_loop(node)

    def visit_Decl(self, node):
        if node.name and node.name.startswith(('old_rank', 'new_rank')):
            self.decls.append((node.name, node, self.in_loop > 0))
        self.generic_visit(node)


def _unsupported(msg):
    return 8, {'errors': [msg], 'inf': msg}


class GuardPurityChecker(c_ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_Assignment(self, node):
        self.errors.append('loop guard contains an assignment')

    def visit_FuncCall(self, node):
        name = node.name.name if isinstance(node.name, c_ast.ID) else '<call>'
        self.errors.append("loop guard calls '%s'; guards must be pure expressions" % name)

    def visit_UnaryOp(self, node):
        if node.op in ('p++', 'p--', '++', '--'):
            self.errors.append('loop guard contains increment/decrement')
            return
        if node.expr is not None:
            self.visit(node.expr)

    def visit_BinaryOp(self, node):
        if node.op == ',':
            self.errors.append('loop guard contains a comma expression')
        self.generic_visit(node)


class LoopControlFlowChecker(c_ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_While(self, node):
        self.errors.append('nested while loop inside the loop body')
        self.generic_visit(node)

    def visit_For(self, node):
        self.errors.append('nested for loop inside the loop body')
        self.generic_visit(node)

    def visit_DoWhile(self, node):
        self.errors.append('nested do-while loop inside the loop body')
        self.generic_visit(node)

    def visit_Goto(self, node):
        self.errors.append('goto statement inside the loop body')

    def visit_Label(self, node):
        self.errors.append('label inside the loop body')


class BodyDeclNameCollector(c_ast.NodeVisitor):
    def __init__(self):
        self.names = []

    def visit_Decl(self, node):
        if node.name and not node.name.startswith(('old_rank', 'new_rank')):
            self.names.append(node.name)
        self.generic_visit(node)


def _contains_node(node, target):
    if node is target:
        return True
    for _, child in node.children():
        if _contains_node(child, target):
            return True
    return False


def collect_outer_names(ast, loop_node):
    """Names visible from outside the loop (globals, params, enclosing blocks)."""
    names = set()

    class Visitor(c_ast.NodeVisitor):
        def _maybe_descend(self, node):
            if node is loop_node:
                return
            self.generic_visit(node)

        def visit_While(self, node):
            self._maybe_descend(node)

        def visit_For(self, node):
            self._maybe_descend(node)

        def visit_DoWhile(self, node):
            self._maybe_descend(node)

        def visit_Decl(self, node):
            if node.name and not node.name.startswith(('old_rank', 'new_rank')):
                names.add(node.name)
            self.generic_visit(node)

        def visit_FuncDef(self, node):
            if not _contains_node(node, loop_node):
                return
            args = node.decl.type.args
            if args is not None:
                for param in args.params:
                    if param.name:
                        names.add(param.name)
            self.generic_visit(node)

    Visitor().visit(ast)
    return names


class OutsideNewRankAssignments(c_ast.NodeVisitor):
    def __init__(self, loop_node):
        self.loop_node = loop_node
        self.errors = []

    def _maybe_descend(self, node):
        if node is self.loop_node:
            return
        self.generic_visit(node)

    def visit_While(self, node):
        self._maybe_descend(node)

    def visit_For(self, node):
        self._maybe_descend(node)

    def visit_DoWhile(self, node):
        self._maybe_descend(node)

    def visit_Assignment(self, node):
        if isinstance(node.lvalue, c_ast.ID) and node.lvalue.name.startswith('new_rank'):
            self.errors.append(
                'new_rank must be assigned only by the updates at the end of the loop body'
            )
        self.generic_visit(node)


def _contiguous_indices(names, prefix):
    indices = []
    for name in names:
        match = re.match(r'^%s(\d+)$' % prefix, name)
        if match is None:
            return None
        indices.append(int(match.group(1)))
    if not indices or sorted(indices) != list(range(1, len(indices) + 1)):
        return None
    return len(indices)


def check_rank_layout(ast, loop_node):
    """Check ghost declaration/update layout. Returns (status, info) or (None, None)."""
    body = loop_node.stmt
    if not isinstance(body, c_ast.Compound):
        return _unsupported('the loop body must be a braced compound statement')
    items = body.block_items or []

    scanner = RankDeclScanner(loop_node)
    scanner.visit(ast)
    in_body = [name for name, _, inside in scanner.decls if inside]
    if in_body:
        return 4, {'errors': [
            'ghost declarations must appear before the loop; found inside the loop body: %s'
            % ', '.join(sorted(set(in_body)))], 'inf': 'ghost declaration inside loop body'}

    old_decls = [(name, node) for name, node, _ in scanner.decls if name.startswith('old_rank')]
    new_decls = [(name, node) for name, node, _ in scanner.decls if name.startswith('new_rank')]
    old_names = [name for name, _ in old_decls]
    new_names = [name for name, _ in new_decls]

    if not old_names and not new_names:
        return 2, {'inf': "Missing required rank variable declarations. "
                           "Expected old_rank1..n and new_rank1..n."}
    n_old = _contiguous_indices(old_names, 'old_rank')
    n_new = _contiguous_indices(new_names, 'new_rank')
    if n_old is None or n_new is None or n_old != n_new:
        return 2, {'old_count': len(old_names), 'new_count': len(new_names),
                   'count': len(old_names), 'old_vars': old_names, 'new_vars': new_names,
                   'inf': 'Rank variables must be declared exactly as old_rank1..n and new_rank1..n'}
    n = n_old

    for name, node in old_decls + new_decls:
        if not is_integer_rank_type(node.type):
            return 4, {'errors': [
                "rank variable '%s' must have an integer scalar type (int/long)" % name],
                'inf': 'non-integer ghost declaration'}
    for name, node in new_decls:
        if node.init is None:
            return 4, {'errors': [
                "new_rank variable '%s' must be initialized in its declaration" % name],
                'inf': 'uninitialized new_rank declaration'}

    snapshot_errors = []
    for i in range(n):
        expected_old = 'old_rank%d' % (i + 1)
        expected_new = 'new_rank%d' % (i + 1)
        stmt = items[i] if i < len(items) else None
        if not (isinstance(stmt, c_ast.Assignment)
                and isinstance(stmt.lvalue, c_ast.ID)
                and stmt.lvalue.name == expected_old
                and isinstance(stmt.rvalue, c_ast.ID)
                and stmt.rvalue.name == expected_new):
            snapshot_errors.append(
                'the loop body must start with %s = %s; (snapshots in order, one per rank)'
                % (expected_old, expected_new))
    for index, stmt in enumerate(items):
        if (isinstance(stmt, c_ast.Assignment) and isinstance(stmt.lvalue, c_ast.ID)
                and stmt.lvalue.name.startswith('old_rank') and index >= n):
            snapshot_errors.append(
                'old_rank variables may only be assigned by the leading snapshots')
    if snapshot_errors:
        return 3, {'errors': snapshot_errors, 'count': n, 'inf': snapshot_errors[0]}

    outside = OutsideNewRankAssignments(loop_node)
    outside.visit(ast)
    if outside.errors:
        return 4, {'errors': outside.errors, 'inf': outside.errors[0]}

    init_expr = {name: ExpressionNormalizer().normalize(node.init) for name, node in new_decls}

    update_errors = []
    if len(items) < n:
        update_errors.append('the loop body is too short to contain %d new_rank updates' % n)
    else:
        for i in range(n):
            expected = 'new_rank%d' % (i + 1)
            stmt = items[len(items) - n + i]
            if not (isinstance(stmt, c_ast.Assignment)
                    and isinstance(stmt.lvalue, c_ast.ID)
                    and stmt.lvalue.name == expected):
                update_errors.append(
                    'the last %d statements of the loop body must be new_rank1 = e1; ... '
                    'new_rank%d = e%d; (missing or out-of-order %s)' % (n, n, n, expected))
                continue
            actual = ExpressionNormalizer().normalize(stmt.rvalue)
            if actual != init_expr.get(expected):
                update_errors.append(
                    "%s update expression mismatch: initialization='%s', loop='%s'"
                    % (expected, init_expr.get(expected), actual))
    for index, stmt in enumerate(items):
        if (isinstance(stmt, c_ast.Assignment) and isinstance(stmt.lvalue, c_ast.ID)
                and stmt.lvalue.name.startswith('new_rank') and index < len(items) - n):
            update_errors.append(
                'new_rank updates must be the last %d statements of the loop body' % n)
    if update_errors:
        return 4, {'errors': update_errors, 'count': n, 'inf': update_errors[0]}

    return None, None

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
def preprocess_c_code(c_code, verbose=True):
    if verbose:
        print("\n[Step] Preprocessing C code: remove preprocessor directives + all comments")
        print(f"  Original code lines: {len(c_code.splitlines())}")

    # 1. Remove all preprocessor directives (#include, #define, etc.)
    c_code = re.sub(r'^\s*#.*$', '', c_code, flags=re.MULTILINE)

    # 2. Thoroughly remove all C comments (block comments + line comments)
    def remove_c_comments(text):
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
        return text

    c_code = remove_c_comments(c_code)

    # 3. Clean up leftover whitespace and blank lines
    c_code = re.sub(r'[ \t]+$', '', c_code, flags=re.MULTILINE)
    c_code = re.sub(r'\n\s*\n', '\n\n', c_code)
    c_code = c_code.strip() + '\n'

    if verbose:
        print(f"  → Lines after preprocessing: {len(c_code.splitlines())}")
        print("  → Preprocessing done, ready for AST parsing")
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
    
    # Check 0: Ranking-expression purity
    print("\n[Step] Checking ranking-expression purity...")
    grammar_collector = RankingExpressionCollector()
    grammar_collector.visit(ast)
    if grammar_collector.errors:
        print(f"\n[✗] Ranking-expression purity check failed ({len(grammar_collector.errors)} errors)")
        for error in grammar_collector.errors:
            print(f"  - {error}")
        return 7, {'errors': grammar_collector.errors,
            'inf': f"Ranking-expression purity check failed ({len(grammar_collector.errors)} errors)"}
    print("[✓] Ranking-expression purity check passed")

    # Check 1: supported fragment (pure guard, no nested loops / goto / labels, braced body)
    print("\n[Step] Checking supported program fragment...")
    unsupported_errors = []
    if loop_node.cond is not None:
        guard_checker = GuardPurityChecker()
        guard_checker.visit(loop_node.cond)
        unsupported_errors.extend(guard_checker.errors)
    if not isinstance(loop_node.stmt, c_ast.Compound):
        unsupported_errors.append('the loop body must be a braced compound statement')
    else:
        control_checker = LoopControlFlowChecker()
        for item in loop_node.stmt.block_items or []:
            control_checker.visit(item)
        unsupported_errors.extend(control_checker.errors)
    if unsupported_errors:
        print(f"\n[✗] Unsupported program feature ({len(unsupported_errors)} errors)")
        for error in unsupported_errors:
            print(f"  - {error}")
        return 8, {'errors': unsupported_errors, 'inf': unsupported_errors[0]}

    # Check 2: local declarations inside the loop body must not shadow outer variables
    if isinstance(loop_node.stmt, c_ast.Compound):
        outer_names = collect_outer_names(ast, loop_node)
        decl_collector = BodyDeclNameCollector()
        for item in loop_node.stmt.block_items or []:
            decl_collector.visit(item)
        shadow_errors = ['loop body redeclares outer variable \'%s\'' % name
                         for name in decl_collector.names if name in outer_names]
        if shadow_errors:
            print(f"\n[✗] Shadowing inside loop body ({len(shadow_errors)} errors)")
            for error in shadow_errors:
                print(f"  - {error}")
            return 8, {'errors': shadow_errors, 'inf': shadow_errors[0]}
    print("[✓] Supported program fragment check passed")

    # Check 3: ghost layout (declarations, snapshots, final updates, expression consistency)
    print("\n[Step] Checking ghost declaration and update layout...")
    layout_status, layout_info = check_rank_layout(ast, loop_node)
    if layout_status is not None:
        print(f"\n[✗] Ghost layout check failed (status {layout_status})")
        for error in layout_info.get('errors', [layout_info.get('inf', '')]):
            print(f"  - {error}")
        return layout_status, layout_info
    print("[✓] Ghost layout check passed")

    count = len(RankDeclScanner(loop_node).decls) // 2
    print("\n" + "="*60)
    print("✅ All checks passed! Rank update logic conforms to verification specification")
    print("="*60)
    return 1, {'count': count}

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
        7: ("❌ Ranking-expression purity violation", "Ranking expression contains a disallowed construct"),
        8: ("❌ Unsupported program feature", "Guard/control-flow construct outside the supported fragment"),
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
