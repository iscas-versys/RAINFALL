"""Non-interference check between the original program and an LLM candidate.

Only exactly-recognized ghost statements and assert comments are removed from
the candidate.  The remaining program is parsed with libclang and compared
against the original as a cursor tree, so any inserted side effect is rejected
regardless of where it is hidden.
"""
import os
import re
from pathlib import Path
import sys

from clang.cindex import Config, Diagnostic, Index, CursorKind, TokenKind


HARNESS_FRAGMENTS = (
    "externvoid__VERIFIER_assert(bool);",
    "void__VERIFIER_assert(intcond){if(!(cond)){ERROR:__VERIFIER_error();}}",
    "typedefenum{false,true}bool;",
)

INCLUDE_RE = re.compile(r'^\s*#\s*include\b')
DIRECTIVE_RE = re.compile(r'^\s*#')
ASSERT_COMMENT_RE = re.compile(r'^\s*//\s*@\s*assert\s*\(.*\)\s*;\s*$')
GHOST_DECL_RE = re.compile(
    r'^(?:int|long|long\s+long)\s+'
    r'(?:old_rank\d+(?:\s*,\s*old_rank\d+)*'
    r'|new_rank\d+\s*=\s*[^;]+(?:\s*,\s*new_rank\d+\s*=\s*[^;]+)*)\s*;$'
)
GHOST_SNAPSHOT_RE = re.compile(r'^old_rank\d+\s*=\s*new_rank\d+\s*;$')
GHOST_UPDATE_RE = re.compile(r'^new_rank\d+\s*=\s*[^;]+;$')
GHOST_START_RE = re.compile(
    r'^(?:int|long|long\s+long)\s+(?:old_rank\d+|new_rank\d+\s*=)'
    r'|^old_rank\d+\s*=\s*new_rank\d+'
    r'|^new_rank\d+\s*='
)
RESIDUAL_GHOST_RE = re.compile(r'\b(?:old_rank|new_rank)\w*')


def _ensure_libclang():
    """Point pyclang at a compatible libclang before the first Index.create()."""
    if getattr(Config, "loaded", False):
        return
    root = Path(__file__).resolve().parent.parent
    files = [
        os.environ.get("LIBCLANG_FILE"),
        str(root / "clang+llvm" / "lib" / "libclang.so"),
        str(root / "clang+llvm" / "bin" / "libclang.dll"),
        str(root / "llvm" / "lib" / "libclang.so"),
    ]
    for path in files:
        if path and os.path.exists(path):
            Config.set_library_file(path)
            return
    dirs = [
        os.environ.get("LIBCLANG_PATH"),
        str(root / "clang+llvm" / "lib"),
        str(root / "llvm" / "lib"),
        "/usr/lib/llvm-18/lib",
        "/usr/lib/llvm-17/lib",
        "/usr/lib/llvm-16/lib",
        "/usr/lib/llvm-15/lib",
        "/usr/lib/llvm-14/lib",
        "/usr/lib/llvm-13/lib",
        "/usr/lib/llvm-12/lib",
        "/usr/lib/x86_64-linux-gnu",
        "/usr/local/lib",
    ]
    for directory in dirs:
        if not directory or not os.path.isdir(directory):
            continue
        for pattern in ("libclang.so", "libclang-*.so", "libclang.so.*", "libclang*.dll"):
            for path in sorted(Path(directory).glob(pattern)):
                if "-cpp" in path.name:
                    continue
                if path.is_file() or path.is_symlink():
                    Config.set_library_file(str(path))
                    return


def _strip_harness(line):
    compact = line.replace(" ", "")
    return any(fragment in compact for fragment in HARNESS_FRAGMENTS)


def _squash(text):
    return re.sub(r'\s+', ' ', text).strip()


def _is_ghost_statement(statement):
    return bool(GHOST_DECL_RE.match(statement)
                or GHOST_SNAPSHOT_RE.match(statement)
                or GHOST_UPDATE_RE.match(statement))


def filter_candidate(lines):
    """Remove only complete, exactly-recognized ghost statements and assert comments."""
    output = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if ASSERT_COMMENT_RE.match(stripped):
            index += 1
            continue
        if GHOST_START_RE.match(stripped):
            chunk = [stripped]
            while ';' not in chunk[-1] and index + 1 < len(lines):
                index += 1
                chunk.append(lines[index].strip())
            statement = _squash(" ".join(chunk))
            if _is_ghost_statement(statement):
                index += 1
                continue
            output.extend(chunk)
            index += 1
            continue
        output.append(lines[index])
        index += 1
    return output


def _strip_common(lines):
    result = []
    directives = []
    for line in lines:
        if INCLUDE_RE.match(line) or _strip_harness(line):
            continue
        if DIRECTIVE_RE.match(line):
            directives.append(_squash(line))
        result.append(line)
    return result, directives


def parse_file(filename):
    """Parse a C file and return the translation-unit cursor."""
    _ensure_libclang()
    index = Index.create()
    tu = index.parse(filename, args=["-std=c99"])
    if tu is None:
        raise RuntimeError("libclang failed to parse %s" % filename)
    errors = [d for d in tu.diagnostics if d.severity >= Diagnostic.Error]
    if errors:
        raise RuntimeError("; ".join(str(d) for d in errors))
    return tu.cursor


_OPERATOR_KINDS = {
    CursorKind.BINARY_OPERATOR,
    CursorKind.UNARY_OPERATOR,
    CursorKind.COMPOUND_ASSIGNMENT_OPERATOR,
    CursorKind.MEMBER_REF_EXPR,
}


def _operator_spellings(cursor):
    """Punctuation tokens owned by this node, with their position in its token list.

    For operator cursors (e.g. BINARY_OPERATOR) libclang reports no spelling, so
    `a + b` and `a - b` produce identical signatures and a candidate can rewrite
    the program inside an otherwise unchanged tree.  Subtracting the tokens of
    the child subtrees leaves exactly the operator token(s); the position index
    also distinguishes prefix from postfix forms.
    """
    child_spans = set()
    for child in cursor.get_children():
        for tok in child.get_tokens():
            child_spans.add((tok.extent.start.offset, tok.extent.end.offset))

    tokens = list(cursor.get_tokens())
    ops = []
    for idx, tok in enumerate(tokens):
        if tok.kind != TokenKind.PUNCTUATION:
            continue
        if (tok.extent.start.offset, tok.extent.end.offset) in child_spans:
            continue
        ops.append("%s@%d/%d" % (tok.spelling, idx, len(tokens)))
    return ",".join(ops)


def get_cursor_signature(cursor):
    """Signature of a cursor's relevant attributes, ignoring source locations."""
    parts = [str(cursor.kind)]

    if cursor.kind != CursorKind.TRANSLATION_UNIT:
        if cursor.kind == CursorKind.INTEGER_LITERAL:
            tokens = list(cursor.get_tokens())
            if tokens:
                value = tokens[0].spelling
            else:
                value = cursor.displayname or cursor.spelling or "?"
            parts.append("value:%s" % value)
        elif cursor.spelling:
            parts.append("spelling:%s" % cursor.spelling)

        if cursor.kind in _OPERATOR_KINDS:
            ops = _operator_spellings(cursor)
            if ops:
                parts.append("op:%s" % ops)

        if cursor.type and cursor.type.kind != 'INVALID':
            parts.append("type:%s" % cursor.type.spelling)

    return "|".join(parts)


def _is_return_zero(cursor):
    if cursor.kind != CursorKind.RETURN_STMT:
        return False
    children = list(cursor.get_children())
    if len(children) != 1 or children[0].kind != CursorKind.INTEGER_LITERAL:
        return False
    tokens = list(children[0].get_tokens())
    return bool(tokens) and tokens[0].spelling == '0'


def compare_cursors(c1, c2):
    if c1.kind != c2.kind:
        return False, "Kind mismatch: %s vs %s" % (c1.kind, c2.kind)

    children1 = list(c1.get_children())
    children2 = list(c2.get_children())

    if c1.kind == CursorKind.COMPOUND_STMT:
        if children1 and children2:
            if not _is_return_zero(children1[-1]) and _is_return_zero(children2[-1]):
                children2 = children2[:-1]
            elif _is_return_zero(children1[-1]) and not _is_return_zero(children2[-1]):
                children1 = children1[:-1]

    sig1 = get_cursor_signature(c1)
    sig2 = get_cursor_signature(c2)
    if sig1 != sig2:
        return False, "Signature mismatch: '%s' vs '%s'" % (sig1, sig2)

    if len(children1) != len(children2):
        return False, "Children count mismatch: %d vs %d" % (len(children1), len(children2))

    for i, (child1, child2) in enumerate(zip(children1, children2)):
        ok, msg = compare_cursors(child1, child2)
        if not ok:
            return False, "Child %d mismatch: %s" % (i, msg)

    return True, "ASTs are identical"


def check_AST(file1, file2):
    """Check that the candidate (file2) differs from the original (file1) only by ghost code."""
    try:
        with open(file2, "r", encoding="utf-8", errors="replace") as f:
            candidate_lines = f.read().splitlines()
        with open(file1, "r", encoding="utf-8", errors="replace") as f:
            original_lines = f.read().splitlines()
    except Exception as exc:
        return False, "Cannot read input file: %s" % exc

    filtered = filter_candidate(candidate_lines)
    base, ext = os.path.splitext(file2)
    filtered_path = base + "_delLLMGen" + ext

    residual = [line.strip() for line in filtered if RESIDUAL_GHOST_RE.search(line)]
    if residual:
        return False, ("Ghost instrumentation was not removed by the recognized layout; "
                       "unexpected line: %s" % residual[0][:120])

    original_body, original_directives = _strip_common(original_lines)
    candidate_body, candidate_directives = _strip_common(filtered)
    if original_directives != candidate_directives:
        return False, ("Preprocessor directives differ from the original program: %r vs %r"
                       % (candidate_directives, original_directives))

    with open(filtered_path, "w", encoding="utf-8") as f:
        f.write("\n".join(candidate_body) + "\n")

    original_path = base + "_original" + ext
    with open(original_path, "w", encoding="utf-8") as f:
        f.write("\n".join(original_body) + "\n")

    try:
        cursor1 = parse_file(original_path)
        cursor2 = parse_file(filtered_path)
    except Exception as exc:
        return False, "Cannot parse program: %s" % exc

    ok, msg = compare_cursors(cursor1, cursor2)
    if ok:
        print("✅ ASTs are structurally identical.")
        return True, msg
    print("❌ ASTs differ: %s" % msg)
    return False, msg


def batch_compare_folders(folder1: str, folder2: str, pattern="*.c"):
    """
    遍历 folder1 中的所有 .c 文件，在 folder2 中查找同名文件并比较 AST。
    """
    folder1_path = Path(folder1)
    folder2_path = Path(folder2)

    if not folder1_path.exists():
        print(f"❌ Folder not found: {folder1}")
        return
    if not folder2_path.exists():
        print(f"❌ Folder not found: {folder2}")
        return

    c_files = list(folder1_path.glob(pattern))
    if not c_files:
        print(f"⚠️ No {pattern} files found in {folder1}")
        return

    total = len(c_files)
    passed = 0
    failed = 0
    skipped = 0

    print(f"\n🔍 Comparing {total} files from '{folder1}' with corresponding files in '{folder2}'\n")

    for file1 in sorted(c_files):
        file2 = folder2_path / file1.name
        if not file2.exists():
            print(f"⚠️ Skipped: {file1.name} (not found in {folder2})")
            skipped += 1
            continue

        print(f"→ {file1.name}: ", end="")
        try:
            ok, msg = check_AST(str(file1), str(file2))
            if ok:
                print("✅ identical")
                passed += 1
            else:
                print(f"❌ differs - {msg}")
                failed += 1
        except Exception as e:
            print(f"💥 error - {e}")
            failed += 1

    print("\n" + "="*50)
    print(f"📊 Summary: Total={total}, Passed={passed}, Failed={failed}, Skipped={skipped}")
    print("="*50)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        ok, msg = check_AST(sys.argv[1], sys.argv[2])
        sys.exit(0 if ok else 1)
    elif len(sys.argv) == 4 and sys.argv[1] == "--batch":
        batch_compare_folders(sys.argv[2], sys.argv[3])
    else:
        print("Usage:")
        print("  Single pair: python astChecker.py <file1.c> <file2.c>")
        print("  Batch mode:  python astChecker.py --batch <folder1> <folder2>")
        sys.exit(1)
