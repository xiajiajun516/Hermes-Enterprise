#!/usr/bin/env python3
"""
Kanban Validator Script for Hermes Enterprise Profile
Validates whether kanban/kanban.md conforms to allowed states and formats.
"""

import sys
import os

VALID_STATES = ["Backlog", "Planning", "Implementation", "In Review", "Done", "Blocked"]
# Kanban 表头列名（用于表格格式检测）
KANBAN_COLUMNS = ["Backlog", "Planning", "Implementation", "In Review", "Done", "Blocked"]


def check_kanban_table(content):
    """检测标准 Markdown 看板表格（列名 + 分隔符），缺失时仅打印 WARNING。"""
    lines = content.split("\n")
    table_found = False
    separator_found = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            # 检查表头是否包含看板列名
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            matches = sum(1 for col in KANBAN_COLUMNS if col in cells)
            if matches >= 3:
                # 找到了表头，检查下一行是否是分隔符
                table_found = True
                if i + 1 < len(lines):
                    sep_line = lines[i + 1].strip()
                    if "|" in sep_line and all(c in "| -:" for c in sep_line):
                        separator_found = True
                break

    if not table_found:
        print("⚠️  WARNING: 未检测到标准 Kanban Markdown 表格（期望列名: Backlog, Planning, Implementation, In Review, Done, Blocked）")
        print("    建议添加 Markdown 表格以增强看板可视化。")
    elif not separator_found:
        print("⚠️  WARNING: 检测到 Kanban 表头但缺少分隔符行（| --- | --- |），表格可能渲染异常。")
    else:
        print("✅  Kanban 表格格式检测通过。")

    # 始终返回 True（仅警告，向后兼容）
    return True

def validate_kanban(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' does not exist.")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"🔍 Validating {file_path}...")
    errors = []

    # 表格格式检测（仅警告，不影响退出码）
    check_kanban_table(content)

    for state in VALID_STATES:
        if f"**{state}**" not in content and f"- {state}:" not in content:
            errors.append(f"Missing expected status section: '{state}'")

    if errors:
        for err in errors:
            print(f"❌ {err}")
        return False

    print("✅ Kanban validation passed successfully!")
    return True

if __name__ == "__main__":
    kanban_path = sys.argv[1] if len(sys.argv) > 1 else "kanban/kanban.md"
    success = validate_kanban(kanban_path)
    sys.exit(0 if success else 1)
