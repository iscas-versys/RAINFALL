import os
from pathlib import Path
import sys
import clang
from clang.cindex import Index, CursorKind
def parse_file(filename):
    """解析C文件，返回翻译单元的游标"""
    index = Index.create()

    tu = index.parse(filename, args=["-std=c99"])  # 可根据需要调整标准
    if not tu:
        raise RuntimeError(f"Failed to parse {filename}")
    # 打印诊断信息（可选）
    for diag in tu.diagnostics:
        print(diag)
    return tu.cursor
def get_cursor_signature(cursor):
    """
    获取游标的签名，用于比较节点的关键属性。
    对 TRANSLATION_UNIT 节点忽略文件名（spelling）和类型。
    """
    parts = [str(cursor.kind)]

    if cursor.kind != CursorKind.TRANSLATION_UNIT:
        # 对整型常量，使用 token 方式获取数值
        if cursor.kind == CursorKind.INTEGER_LITERAL:
            tokens = list(cursor.get_tokens())
            if tokens:
                value = tokens[0].spelling  # 通常是 "2" 或 "1"
            else:
                value = cursor.displayname or cursor.spelling or "?"
            parts.append(f"value:{value}")
        else:
            if cursor.spelling:
                parts.append(f"spelling:{cursor.spelling}")
        
        if cursor.type and cursor.type.kind != 'INVALID':
            parts.append(f"type:{cursor.type.spelling}")

    return "|".join(parts)
def compare_cursors(c1, c2):
    if c1.kind != c2.kind:
        return False, f"Kind mismatch: {c1.kind} vs {c2.kind}"

    # ------------------------------------------------------------
    # 特殊处理：COMPOUND_STMT（函数体）允许一方末尾多一个 return 0;
    # ------------------------------------------------------------
    if c1.kind == CursorKind.COMPOUND_STMT and c2.kind == CursorKind.COMPOUND_STMT:
        children1 = list(c1.get_children())
        children2 = list(c2.get_children())

        # 辅助函数：判断一个游标是不是 return 0;
        def is_return_zero(cursor):
            if cursor.kind != CursorKind.RETURN_STMT:
                return False
            ret_children = list(cursor.get_children())
            if len(ret_children) != 1:
                return False
            val = ret_children[0]
            if val.kind != CursorKind.INTEGER_LITERAL:
                return False
            tokens = list(val.get_tokens())
            if not tokens:
                return False
            return tokens[0].spelling == '0'

        # 若 children1 末尾不是 return 0，而 children2 末尾是 return 0，则从 children2 中去掉它
        if children1 and children2:
            if not is_return_zero(children1[-1]) and is_return_zero(children2[-1]):
                children2 = children2[:-1]
            elif is_return_zero(children1[-1]) and not is_return_zero(children2[-1]):
                children1 = children1[:-1]

        # 比较调整后的子节点
        if len(children1) != len(children2):
            return False, f"Children count mismatch after return adjustment: {len(children1)} vs {len(children2)}"

        for i, (ch1, ch2) in enumerate(zip(children1, children2)):
            ok, msg = compare_cursors(ch1, ch2)
            if not ok:
                return False, f"Child {i} mismatch: {msg}"
        return True, "ASTs are identical (adjusted for return 0)"

    # ------------------------------------------------------------
    # 原有逻辑：非 COMPOUND_STMT 节点继续使用签名比较
    # ------------------------------------------------------------
    sig1 = get_cursor_signature(c1)
    sig2 = get_cursor_signature(c2)
    if sig1 != sig2:
        return False, f"Signature mismatch: '{sig1}' vs '{sig2}'"

    children1 = list(c1.get_children())
    children2 = list(c2.get_children())
    if len(children1) != len(children2):
        return False, f"Children count mismatch: {len(children1)} vs {len(children2)}"

    for i, (child1, child2) in enumerate(zip(children1, children2)):
        ok, msg = compare_cursors(child1, child2)
        if not ok:
            return False, f"Child {i} mismatch: {msg}"

    return True, "ASTs are identical"
def check_AST(file1,file2):
    with open("./"+file2, "r") as f:
        file_open = f.read()
    file_save =open(file2.replace(".c","_delLLMGen.c"),"w")
    lines = file_open.splitlines()
    skip_rank_stmt = False

    for i, line in enumerate(lines):
        if skip_rank_stmt:
            if ";" in line:
                skip_rank_stmt = False
            continue

        if "include" in line:
            continue

        if "rank" in line:
            if ";" not in line:
                skip_rank_stmt = True
            continue

        if "assert" in line:
            continue

        file_save.write(line + "\n")
    file_save.close()
    file2 = file2.replace(".c","_delLLMGen.c")
    try:
        cursor1 = parse_file(file1)
        cursor2 = parse_file(file2)
    except Exception as e:
        print(f"Error parsing files: {e}")
        sys.exit(1)

    ok, msg = compare_cursors(cursor1, cursor2)
    if ok:
        print("✅ ASTs are structurally identical.")
        return True,msg
    else:
        print(f"❌ ASTs differ: {msg}")
        return False,msg

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

    # 收集第一个文件夹中所有 .c 文件
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
            # 注意：check_AST 内部会对 file2 进行过滤处理，这里直接调用
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

    # 输出统计
    print("\n" + "="*50)
    print(f"📊 Summary: Total={total}, Passed={passed}, Failed={failed}, Skipped={skipped}")
    print("="*50)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        # 单对文件比较模式
        file1, file2 = sys.argv[1], sys.argv[2]
        ok, msg = check_AST(file1, file2)
        sys.exit(0 if ok else 1)
    elif len(sys.argv) == 4 and sys.argv[1] == "--batch":
        # 批量文件夹模式
        _, _, folder1, folder2 = sys.argv
        batch_compare_folders(folder1, folder2)
    else:
        print("Usage:")
        print("  Single pair: python ast_compare.py <file1.c> <file2.c>")
        print("  Batch mode:  python ast_compare.py --batch <folder1> <folder2>")
        sys.exit(1)