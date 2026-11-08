
#!/usr/bin/env python3
"""Ranking-function assertion validator.

The assertions attached to the loop are compared with the canonical decrease
and termination assertions of the ranking class by logical equivalence over
atomic predicates. Presence-based checks are deliberately not used: a
tautology such as ``P || 1`` must not pass.
"""
import os
import sys
import re
import argparse
from pycparser import c_parser, c_ast
from pycparser.c_generator import CGenerator

MAX_ATOMS = 18

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


def is_integer_rank_type(decl_type):
    if not isinstance(decl_type, c_ast.TypeDecl):
        return False
    if not isinstance(decl_type.type, c_ast.IdentifierType):
        return False
    names = decl_type.type.names
    return 'int' in names or 'long' in names


class GhostDeclCollector(c_ast.NodeVisitor):
    def __init__(self):
        self.old = {}
        self.new = {}

    def visit_Decl(self, node):
        name = node.name or ''
        if re.match(r'^old_rank\d+$', name):
            self.old[name] = node
        elif re.match(r'^new_rank\d+$', name):
            self.new[name] = node
        self.generic_visit(node)


# ==================== Boolean formulas over atomic predicates ====================
def _text(node):
    try:
        return re.sub(r'\s+', '', CGenerator().visit(node))
    except Exception:
        return '<unparseable>'


def _cmp_key(op, left, right):
    lt, rt = _text(left), _text(right)
    if op == '==':
        return min(lt + '==' + rt, rt + '==' + lt)
    if op == '>':
        return min(lt + '>' + rt, rt + '<' + lt)
    if op == '<':
        return min(lt + '<' + rt, rt + '>' + lt)
    return _text(c_ast.BinaryOp(op=op, left=left, right=right))


def formula(node):
    """Translate an expression into ('atom', key) / ('not', f) / ('and'/'or', [f])."""
    if node is None:
        return ('atom', '<none>')
    if isinstance(node, c_ast.UnaryOp) and node.op == '!':
        return ('not', formula(node.expr))
    if isinstance(node, c_ast.BinaryOp) and node.op in ('&&', '||'):
        kind = 'and' if node.op == '&&' else 'or'
        return (kind, [formula(node.left), formula(node.right)])
    if isinstance(node, c_ast.BinaryOp) and node.op in ('<', '>', '==', '<=', '>=', '!='):
        op = node.op
        if op == '<=':
            return ('not', ('atom', _cmp_key('>', node.left, node.right)))
        if op == '>=':
            return ('not', ('atom', _cmp_key('<', node.left, node.right)))
        if op == '!=':
            return ('not', ('atom', _cmp_key('==', node.left, node.right)))
        return ('atom', _cmp_key(op, node.left, node.right))
    return ('atom', _text(node))


def _collect_atoms(f, acc):
    if f[0] == 'atom':
        acc.add(f[1])
    elif f[0] == 'not':
        _collect_atoms(f[1], acc)
    else:
        for child in f[1]:
            _collect_atoms(child, acc)


def _eval(f, env):
    if f[0] == 'atom':
        return env[f[1]]
    if f[0] == 'not':
        return not _eval(f[1], env)
    if f[0] == 'and':
        return all(_eval(child, env) for child in f[1])
    return any(_eval(child, env) for child in f[1])


def equivalent(f, g):
    """Exhaustive truth-table equivalence; fail closed when there are too many atoms."""
    atoms = set()
    _collect_atoms(f, atoms)
    _collect_atoms(g, atoms)
    atoms = sorted(atoms)
    if len(atoms) > MAX_ATOMS:
        return False
    for mask in range(1 << len(atoms)):
        env = {atom: bool((mask >> i) & 1) for i, atom in enumerate(atoms)}
        if _eval(f, env) != _eval(g, env):
            return False
    return True


def conjunction(formulas):
    if not formulas:
        return ('atom', '<true>')
    result = formulas[0]
    for item in formulas[1:]:
        result = ('and', [result, item])
    return result


# ==================== Canonical assertion construction ====================
def _id(name):
    return c_ast.ID(name=name)


def _zero():
    return c_ast.Constant(type='int', value='0')


def _bin(op, left, right):
    return c_ast.BinaryOp(op=op, left=left, right=right)


def _not(node):
    return c_ast.UnaryOp(op='!', expr=node)


def _and(nodes):
    result = nodes[0]
    for node in nodes[1:]:
        result = _bin('&&', result, node)
    return result


def _or(nodes):
    result = nodes[0]
    for node in nodes[1:]:
        result = _bin('||', result, node)
    return result


def _old(i):
    return _id('old_rank%d' % i)


def _new(i):
    return _id('new_rank%d' % i)


def _ge0(node):
    return _bin('>=', node, _zero())


def _lt0(node):
    return _bin('<', node, _zero())


def canonical_assertions(cls, n, guard):
    """Return (decrease_formula, termination_formula) for a ranking class."""
    if cls == 'single':
        decrease = _and([_bin('>', _old(1), _new(1)), _ge0(_old(1))])
        termination = _or([_ge0(_new(1)), _not(guard)])
    elif cls == 'lexicographic':
        branches = []
        for i in range(1, n + 1):
            parts = [_bin('==', _old(j), _new(j)) for j in range(1, i)]
            parts.append(_bin('>', _old(i), _new(i)))
            branches.append(_and(parts))
        decrease = _and([_or(branches)] + [_ge0(_old(j)) for j in range(1, n + 1)])
        termination = _or([_and([_ge0(_new(j)) for j in range(1, n + 1)]), _not(guard)])
    else:  # multiphase
        branches = []
        for i in range(1, n + 1):
            parts = []
            for j in range(1, i):
                parts.extend([_lt0(_old(j)), _lt0(_new(j))])
            parts.extend([_ge0(_old(i)), _bin('>', _old(i), _new(i))])
            branches.append(_and(parts))
        decrease = _or(branches)
        termination = _or([_ge0(_new(n)), _not(guard)])
    return formula(decrease), formula(termination)


# ==================== Assertion purity and placement ====================
class SideEffectChecker(c_ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_Assignment(self, node):
        self.errors.append('assignment expression inside an assertion')

    def visit_FuncCall(self, node):
        name = node.name.name if isinstance(node.name, c_ast.ID) else '<call>'
        self.errors.append("function call '%s(...)' inside an assertion" % name)

    def visit_UnaryOp(self, node):
        if node.op in ('p++', 'p--', '++', '--'):
            self.errors.append('increment/decrement inside an assertion')
            return
        self.visit(node.expr)


class AssertCounter(c_ast.NodeVisitor):
    def __init__(self):
        self.count = 0

    def visit_FuncCall(self, node):
        if isinstance(node.name, c_ast.ID) and node.name.name == '__RANK_ASSERT':
            self.count += 1
        self.generic_visit(node)


def _assert_statement(stmt):
    if isinstance(stmt, c_ast.FuncCall):
        if isinstance(stmt.name, c_ast.ID) and stmt.name.name == '__RANK_ASSERT':
            if stmt.args and stmt.args.exprs:
                return stmt.args.exprs[0]
    return None


def _contiguous(names, prefix):
    pattern = re.compile(r'^%s(\d+)$' % prefix)
    indices = []
    for name in names:
        match = pattern.match(name)
        if not match:
            return None
        indices.append(int(match.group(1)))
    if not indices:
        return None
    if sorted(indices) != list(range(1, len(indices) + 1)):
        return None
    return len(indices)


def validate_c_file(c_code, filename="", verbose=False):
    """Validate the ghost instrumentation and assertions of a candidate."""
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

    guard_ext = GuardExtractor()
    guard_ext.visit(ast)
    if guard_ext.expr is None:
        return False, "No loop (while or for) detected with guard condition"
    guard = guard_ext.expr

    decls = GhostDeclCollector()
    decls.visit(ast)
    n_old = _contiguous(decls.old.keys(), 'old_rank')
    n_new = _contiguous(decls.new.keys(), 'new_rank')
    if n_old is None or n_new is None:
        return False, "Rank variables must be declared exactly as old_rank1..n and new_rank1..n"
    if n_old != n_new:
        return False, f"Rank variable count mismatch: {n_old} old_rank vs {n_new} new_rank"
    for group in (decls.old, decls.new):
        for name, decl in group.items():
            if not is_integer_rank_type(decl.type):
                return False, f"Rank variable '{name}' must have an integer scalar type"
    n = n_old

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
    loop_body = locator.loop.stmt
    if not isinstance(loop_body, c_ast.Compound):
        return False, "Loop body is not a compound statement"
    items = loop_body.block_items or []

    top_level = []
    for index, stmt in enumerate(items):
        expr = _assert_statement(stmt)
        if expr is not None:
            top_level.append((index, expr))
    counter = AssertCounter()
    counter.visit(loop_body)
    if counter.count != len(top_level):
        return False, "Assertions must be unconditional statements at the top level of the loop body"

    assert_exprs = [expr for _, expr in top_level]
    if len(assert_exprs) not in (2, 3, 4):
        return False, f"Loop requires 2 to 4 assertions, found {len(assert_exprs)}"

    update_indices = []
    for index, stmt in enumerate(items):
        if isinstance(stmt, c_ast.Assignment) and isinstance(stmt.lvalue, c_ast.ID):
            if re.match(r'^new_rank\d+$', stmt.lvalue.name):
                update_indices.append(index)
    if not update_indices:
        return False, "No new_rank update statement found in the loop body"
    last_update = max(update_indices)
    if any(index <= last_update for index, _ in top_level):
        return False, "Assertions must appear after the last new_rank update"

    for expr in assert_exprs:
        checker = SideEffectChecker()
        checker.visit(expr)
        if checker.errors:
            return False, checker.errors[0]

    classes = ['single'] if n == 1 else ['lexicographic', 'multiphase']
    formulas = [formula(expr) for expr in assert_exprs]

    failures = []
    for cls in classes:
        decr_formula, term_formula = canonical_assertions(cls, n, guard)
        term_matches = [i for i, f in enumerate(formulas) if equivalent(f, term_formula)]
        if len(term_matches) != 1:
            failures.append(
                f"{cls}: expected exactly one termination assertion, found {len(term_matches)}")
            continue
        term_index = term_matches[0]
        decr_others = [f for i, f in enumerate(formulas) if i != term_index]
        if not decr_others:
            failures.append(f"{cls}: missing decrement assertion")
            continue
        if not equivalent(conjunction(decr_others), decr_formula):
            failures.append(f"{cls}: decrement assertions are not equivalent to the canonical claim")
            continue
        return True, f"Validation passed | class={cls} | rank_cnt={n} | assert_cnt={len(assert_exprs)}"

    return False, "Assertion mismatch: " + "; ".join(failures)


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
        description="Rank Function Assertion Validator (exact logical equivalence)",
        epilog="Example: %(prog)s ./sv-benchmarks/c/termination-crafted -v"
    )
    parser.add_argument('dir_path', help='Directory path containing C programs')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed validation process')
    args = parser.parse_args()

    if not os.path.isdir(args.dir_path):
        print(f"❌ Error: '{args.dir_path}' is not a valid directory", file=sys.stderr)
        sys.exit(11)

    c_files = get_c_files(args.dir_path)
    if not c_files:
        print(f"⚠️  Warning: No .c files found in directory '{args.dir_path}'")
        sys.exit(0)

    print(f"📁 Validation directory: {os.path.abspath(args.dir_path)}")
    print(f"📋 Found {len(c_files)} C source files, starting validation...\n")

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

    print("\n" + "="*65)
    print("📊 Validation Summary Report")
    print("="*65)

    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]

    print(f"\n✅ Passed: {len(passed)}")
    for f, _, m in passed:
        print(f"   • {f} ({m})")

    print(f"\n❌ Failed: {len(failed)}")
    for f, _, m in failed:
        print(f"   • {f} | {m}")

    print("\n" + "="*65)
    print(f"📈 Total: {len(results)} | Passed: {len(passed)} | Failed: {len(failed)}")
    print("="*65)

    sys.exit(0 if len(failed) == 0 else 1)

if __name__ == '__main__':
    try:
        import pycparser
    except ImportError:
        print("❌ Dependency missing: Please install pycparser", file=sys.stderr)
        print("   Run: pip install pycparser", file=sys.stderr)
        sys.exit(1)

    main()
