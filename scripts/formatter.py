#!/usr/bin/env python3
"""
中文排版格式检查和修正工具
基于《中文写作排版风格指南》

用法:
    python formatter.py [选项] <file.md> [file2.md ...]

选项:
    --check          只检查不修正（默认）
    --fix            检查并自动修正格式问题
    --skip-tables    跳过 Markdown 表格行
    --output <path>  指定输出文件（默认覆盖原文件）
    --dry-run        模拟修正，不实际写入文件

退出码:
    0 - 无错误（或已修正）
    1 - 发现格式错误（仅 --check 模式）
"""

import re
import sys
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass
class Issue:
    """格式问题"""
    line_num: int
    column: int
    rule: str
    message: str
    context: str
    suggestion: str = ""
    level: str = "error"  # error 或 warning


class MarkdownParser:
    """Markdown 解析器，用于跳过代码块和表格"""

    def __init__(self, content: str, skip_tables: bool = False):
        self.lines = content.splitlines()
        self.in_code_block = False
        self.skip_tables = skip_tables

    def iter_lines(self) -> Iterator[tuple[int, str, bool]]:
        """迭代每一行，返回 (行号, 内容, 是否应跳过)"""
        for i, line in enumerate(self.lines, 1):
            # 检测围栏代码块 ```
            if line.strip().startswith("```"):
                self.in_code_block = not self.in_code_block
                yield (i, line, True)
                continue

            # 跳过表格行
            if self.skip_tables and line.strip().startswith("|"):
                yield (i, line, True)
                continue

            yield (i, line, self.in_code_block)


class StyleFormatter:
    """排版格式检查和修正器"""

    # 中文字符范围
    CJK = r"\u4e00-\u9fff"

    # 标点映射表
    PUNCTUATION_MAP = {
        ',': '，',
        '.': '。',
        '!': '！',
        '?': '？',
        ':': '：',
        ';': '；',
    }

    def __init__(self, skip_tables: bool = False):
        self.issues: list[Issue] = []
        self.skip_tables = skip_tables
        self.fixed_lines = []

    def format_file(self, filepath: Path, dry_run: bool = False) -> tuple[list[Issue], str]:
        """检查并修正文件"""
        self.issues = []
        content = filepath.read_text(encoding="utf-8")

        # 保留原始内容用于比较
        original_content = content
        lines = content.splitlines()
        formatted_lines = []

        parser = MarkdownParser(content, skip_tables=self.skip_tables)

        for line_num, line, in_code_block in parser.iter_lines():
            if in_code_block:
                # 代码块保持原样
                formatted_lines.append(line)
                continue

            # 移除行内代码进行检查
            line_to_check = self._remove_inline_code(line)

            # 检查问题
            self._check_space_cn_en(line_num, line, line_to_check)
            self._check_space_cn_num(line_num, line, line_to_check)
            self._check_halfwidth_punctuation(line_num, line, line_to_check)
            self._check_straight_quotes(line_num, line, line_to_check)
            self._check_ellipsis(line_num, line, line_to_check)
            self._check_dash(line_num, line, line_to_check)
            self._check_bracket_spaces(line_num, line, line_to_check)
            self._check_repeated_punctuation(line_num, line, line_to_check)
            self._check_atx_heading(line_num, line)
            self._check_list_items(line_num, line)
            self._check_hyperlinks(line_num, line)

            # 修正格式
            formatted_line = self._fix_line(line, line_to_check)
            formatted_lines.append(formatted_line)

        # 如果没有问题，直接返回原内容
        if not self.issues:
            return [], original_content

        formatted_content = '\n'.join(formatted_lines)
        return self.issues, formatted_content

    def _remove_inline_code(self, line: str) -> str:
        """移除行内代码块，用空格替代"""
        line = re.sub(r"``[^`]+``", lambda m: " " * len(m.group()), line)
        line = re.sub(r"`[^`]+`", lambda m: " " * len(m.group()), line)
        return line

    def _fix_line(self, line: str, line_to_check: str) -> str:
        """修正单行格式"""
        result = line

        # 1. 修正中外之间缺少空格
        result = self._fix_space_cn_en(result)

        # 2. 修正中文与数字之间缺少空格
        result = self._fix_space_cn_num(result)

        # 3. 修正半角标点为全角标点
        result = self._fix_halfwidth_punctuation(result)

        # 4. 修正直引号为弯引号
        result = self._fix_straight_quotes(result)

        # 5. 修正省略号
        result = self._fix_ellipsis(result)

        # 6. 修正破折号
        result = self._fix_dash(result)

        # 7. 修正括号内多余空格
        result = self._fix_bracket_spaces(result)

        # 8. 修正重复标点
        result = self._fix_repeated_punctuation(result)

        # 9. 修正 Markdown 标题格式
        result = self._fix_atx_heading(result)

        # 10. 修正 Markdown 列表格式
        result = self._fix_list_items(result)

        # 11. 修正超链接格式
        result = self._fix_hyperlinks(result)

        return result

    def _fix_space_cn_en(self, line: str) -> str:
"""修正中外之间缺少空格"""
# 中文后紧跟外文：添加空格
# 外文后紧跟中文：添加空格
        line = re.sub(f"([A-Za-z])([{self.CJK}])", r"\1 \2", line)
        return line

    def _fix_space_cn_num(self, line: str) -> str:
        """修正中文与数字之间缺少空格"""
        # 中文后紧跟数字：添加空格
        line = re.sub(f"([{self.CJK}])([0-9])", r"\1 \2", line)
        # 数字后紧跟中文（排除单位）：添加空格
        line = re.sub(f"([0-9])([{self.CJK}])", r"\1 \2", line)
        return line

    def _fix_halfwidth_punctuation(self, line: str) -> str:
        """修正半角标点为全角标点"""
        for half, full in self.PUNCTUATION_MAP.items():
            # 排除小数点和文件扩展名
            if half == '.':
                line = re.sub(rf"(?<=[^{self.CJK}0-9])\.(?![0-9a-zA-Z])", full, line)
            elif half == ':':
                # 排除 URL 中的冒号 (http:, https:, ftp:)
                # 和时间格式 (9:05)
                line = re.sub(r"(?<!http)(?<!https)(?<!ftp):(?![0-9/])", full, line)
            else:
                line = line.replace(half, full)
        return line

    def _fix_straight_quotes(self, line: str) -> str:
        """修正直引号为弯引号（简体中文）"""
        # 排除 Markdown 链接中的引号
        def replace_quotes(match):
            text = match.group(0)
            # 替换文本中的引号
            text = text.replace('"', '「').replace('"', '」')
            return text

        # 只替换不在链接中的直引号
        result = []
        i = 0
        in_link = False
        while i < len(line):
            if line[i:i+3] == '][':
                in_link = True
            elif line[i:i+1] == ')':
                in_link = False

            if not in_link and line[i] == '"':
                # 检查是开引号还是闭引号
                # 简单处理：偶数个引号为开，奇数为闭
                count_before = line[:i].count('"')
                if count_before % 2 == 0:
                    result.append('「')
                else:
                    result.append('」')
            else:
                result.append(line[i])
            i += 1

        return ''.join(result)

    def _fix_ellipsis(self, line: str) -> str:
        """修正省略号"""
        # 中文上下文中将 ... 替换为 ……
        result = []
        i = 0
        while i < len(line):
            if line[i:i+3] == '...':
                # 检查前后是否有中文
                before = line[:i]
                after = line[i+3:]
                if re.search(f"[{self.CJK}]", before) or re.search(f"[{self.CJK}]", after):
                    result.append('……')
                    i += 3
                else:
                    result.append(line[i])
                    i += 1
            else:
                result.append(line[i])
                i += 1
        return ''.join(result)

    def _fix_dash(self, line: str) -> str:
        """修正破折号"""
        # 中文上下文中将 -- 替换为 ——
        result = []
        i = 0
        while i < len(line) - 1:
            if line[i:i+2] == '--':
                # 检查前后是否有中文
                before = line[:i]
                after = line[i+2:]
                if re.search(f"[{self.CJK}]", before) or re.search(f"[{self.CJK}]", after):
                    result.append('——')
                    i += 2
                else:
                    result.append(line[i])
                    i += 1
            else:
                result.append(line[i])
                i += 1
        if i < len(line):
            result.append(line[i])
        return ''.join(result)

    def _fix_bracket_spaces(self, line: str) -> str:
        """修正括号内多余空格"""
        line = re.sub(r'《\s+', '《', line)
        line = re.sub(r'\s+》', '》', line)
        line = re.sub(r'（\s+', '（', line)
        line = re.sub(r'\s+）', '）', line)
        return line

    def _fix_repeated_punctuation(self, line: str) -> str:
        """修正重复标点"""
        # 多个感叹号合并为一个
        line = re.sub(r'！+', '！', line)
        # 多个问号合并为一个
        line = re.sub(r'？+', '？', line)
        # 多个句号合并为一个
        line = re.sub(r'。+', '。', line)
        return line

    def _fix_atx_heading(self, line: str) -> str:
        """修正 Markdown ATX 标题格式"""
        # #标题 -> # 标题
        line = re.sub(r'^(#{1,6})([^ ])', r'\1 \2', line)
        return line

    def _fix_list_items(self, line: str) -> str:
        """修正 Markdown 列表格式"""
        # -项目 -> - 项目
        line = re.sub(r'^(\s*[-*+])([^ ])', r'\1 \2', line)
        return line

    def _fix_hyperlinks(self, line: str) -> str:
        """修正超链接格式"""
        # [Google](url) -> [Google](url) 保持原样，但检查中外之间
        return line

    # ==================== 检查方法 ====================

    def _check_space_cn_en(self, line_num: int, orig_line: str, line: str):
"""检查中外之间是否有空格"""
    if re.search(r'[\u4e00-\u9fff][a-zA-Z]', text) or re.search(r'[a-zA-Z][\u4e00-\u9fff]', text):
        return True
    return False

def _fix_chinese_foreign_spacing(text: str) -> tuple[str, list[Issue]]:
    """修正中外之间的空格"""
    issues = []
    result = text
    # 中文后紧跟外文：添加空格
    result = re.sub(r'([\u4e00-\u9fff])([a-zA-Z])', r'\1 \2', result)
    # 外文后紧跟中文：添加空格
    result = re.sub(r'([a-zA-Z])([\u4e00-\u9fff])', r'\1 \2', result)

    if result != text:
        issues.append(Issue(
            line_num=0, column=0,
            rule="chinese_foreign_spacing",
            message="中文与外文之间缺少空格",
            context=text[:50],
            suggestion="在中文与外文之间添加空格",
            level="warning"
        ))
        issues.append(Issue(
            line_num=0, column=0,
            rule="chinese_foreign_spacing",
            message="外文与中文之间缺少空格",
            context=text[:50],
            suggestion="在外文与中文之间添加空格",
            level="warning"
        ))

        pattern2 = re.compile(f"([A-Za-z])([{self.CJK}])")
        for m in pattern2.finditer(line):
            self.issues.append(Issue(
                line_num=line_num,
                column=m.start() + 1,
                rule="missing-space-cn-en",
                message="外文与中文之间缺少空格",
                context=orig_line.strip(),
                suggestion=f"在 '{m.group(1)}' 和 '{m.group(2)}' 之间添加空格"
            ))

    def _check_space_cn_num(self, line_num: int, orig_line: str, line: str):
        """检查中文与数字之间是否有空格"""
        pattern1 = re.compile(f"([{self.CJK}])([0-9])")
        for m in pattern1.finditer(line):
            self.issues.append(Issue(
                line_num=line_num,
                column=m.start() + 1,
                rule="missing-space-cn-num",
                message="中文与数字之间缺少空格",
                context=orig_line.strip(),
                suggestion=f"在 '{m.group(1)}' 和 '{m.group(2)}' 之间添加空格"
            ))

        pattern2 = re.compile(f"([0-9])([{self.CJK}])")
        for m in pattern2.finditer(line):
            if m.group(2) in "万亿年月日时分秒点个百千":
                continue
            self.issues.append(Issue(
                line_num=line_num,
                column=m.start() + 1,
                rule="missing-space-cn-num",
                message="数字与中文之间缺少空格",
                context=orig_line.strip(),
                suggestion=f"在 '{m.group(1)}' 和 '{m.group(2)}' 之间添加空格"
            ))

    def _check_halfwidth_punctuation(self, line_num: int, orig_line: str, line: str):
        """检查中文句子中是否使用了半角标点"""
        for punct, full_punct in self.PUNCTUATION_MAP.items():
            if punct == '.':
                pattern = re.compile(f"([{self.CJK}])\\.(?![0-9a-zA-Z])")
            elif punct == ':':
                pattern = re.compile(f"([{self.CJK}]):(?![0-9])")
            else:
                pattern = re.compile(f"([{self.CJK}]){re.escape(punct)}")

            for m in pattern.finditer(line):
                self.issues.append(Issue(
                    line_num=line_num,
                    column=m.start() + 2,
                    rule="halfwidth-punctuation",
                    message=f"中文句子中使用了半角{punct}",
                    context=orig_line.strip(),
                    suggestion=f"使用全角{full_punct}"
                ))

    def _check_straight_quotes(self, line_num: int, orig_line: str, line: str):
        """检查是否使用了直引号"""
        if '"' in line:
            line_no_links = re.sub(r'\[([^\]]*)\]\([^)]*\)', '', line)
            if '"' in line_no_links:
                col = line.find('"') + 1
                self.issues.append(Issue(
                    line_num=line_num,
                    column=col,
                    rule="straight-quotes",
                    message="使用了直引号",
                    context=orig_line.strip(),
                    suggestion="使用直角引号「」"
                ))

    def _check_ellipsis(self, line_num: int, orig_line: str, line: str):
        """检查省略号格式"""
        pattern = re.compile(r"\.{3}")
        for m in pattern.finditer(line):
            before = line[:m.start()]
            after = line[m.end():]
            if re.search(f"[{self.CJK}]", before) or re.search(f"[{self.CJK}]", after):
                self.issues.append(Issue(
                    line_num=line_num,
                    column=m.start() + 1,
                    rule="wrong-ellipsis",
                    message="中文上下文中使用了 '...' 作为省略号",
                    context=orig_line.strip(),
                    suggestion="使用中文省略号 '……'"
                ))

    def _check_dash(self, line_num: int, orig_line: str, line: str):
        """检查破折号格式"""
        pattern = re.compile(r"(?<!-)--(?!-)")
        for m in pattern.finditer(line):
            before = line[:m.start()]
            after = line[m.end():]
            if re.search(f"[{self.CJK}]", before) or re.search(f"[{self.CJK}]", after):
                self.issues.append(Issue(
                    line_num=line_num,
                    column=m.start() + 1,
                    rule="wrong-dash",
                    message="中文上下文中使用了 '--' 作为破折号",
                    context=orig_line.strip(),
                    suggestion="使用中文破折号 '——'"
                ))

    def _check_bracket_spaces(self, line_num: int, orig_line: str, line: str):
        """检查书名号和括号内的多余空格"""
        for bracket in [('《', '》'), ('（', '）')]:
            open_bracket, close_bracket = bracket
            if re.search(rf"{re.escape(open_bracket)}\s", line):
                self.issues.append(Issue(
                    line_num=line_num,
                    column=line.find(open_bracket) + 1,
                    rule="extra-space-in-brackets",
                    message=f"{open_bracket}开头有多余空格",
                    context=orig_line.strip(),
                    suggestion=f"删除 '{open_bracket}' 后的空格"
                ))
            if re.search(rf"\s{re.escape(close_bracket)}", line):
                self.issues.append(Issue(
                    line_num=line_num,
                    column=line.find(close_bracket) + 1,
                    rule="extra-space-in-brackets",
                    message=f"{close_bracket}结尾有多余空格",
                    context=orig_line.strip(),
                    suggestion=f"删除 '{close_bracket}' 前的空格"
                ))

    def _check_repeated_punctuation(self, line_num: int, orig_line: str, line: str):
        """检查重复标点"""
        # 检查重复感叹号
        if re.search(r'！{2,}', line):
            self.issues.append(Issue(
                line_num=line_num,
                column=re.search(r'！+', line).start() + 1,
                rule="repeated-punctuation",
                message="使用了连续的感叹号",
                context=orig_line.strip(),
                suggestion="只使用一个感叹号"
            ))
        # 检查重复问号
        if re.search(r'？{2,}', line):
            self.issues.append(Issue(
                line_num=line_num,
                column=re.search(r'？+', line).start() + 1,
                rule="repeated-punctuation",
                message="使用了连续的问号",
                context=orig_line.strip(),
                suggestion="只使用一个问号"
            ))

    def _check_atx_heading(self, line_num: int, line: str):
        """检查 Markdown ATX 标题格式"""
        if re.match(r'^#{1,6}[^ ]', line):
            self.issues.append(Issue(
                line_num=line_num,
                column=1,
                rule="atx-heading-format",
                message="ATX 标题格式错误",
                context=line.strip(),
                suggestion="在 '#' 后添加空格"
            ))

    def _check_list_items(self, line_num: int, line: str):
        """检查 Markdown 列表格式"""
        if re.match(r'^(\s*[-*+])([^ ])', line):
            self.issues.append(Issue(
                line_num=line_num,
                column=len(re.match(r'^(\s*[-*+])', line).group()) + 1,
                rule="list-item-format",
                message="列表项格式错误",
                context=line.strip(),
                suggestion="在 '-' 后添加空格"
            ))

    def _check_hyperlinks(self, line_num: int, line: str):
        """检查超链接格式"""
# 检查 [text](url) 格式中中外之间是否有空格
def _check_markdown_link_spacing(line: str, line_num: int) -> list[Issue]:
    """检查 Markdown 超链接中的中外空格"""
    issues = []
    # 检查链接文本中中文与外文之间是否缺少空格
            if re.search(f"([{self.CJK}])([A-Za-z])", link_text) or re.search(f"([A-Za-z])([{self.CJK}])", link_text):
                self.issues.append(Issue(
                    line_num=line_num,
                    column=m.start() + 1,
                    rule="hyperlink-format",
                    message="超链接文本中中文与外文之间缺少空格",
                    context=line.strip(),
                    suggestion="在超链接文本的中外之间添加空格"
                ))


def print_report(filepath: Path, issues: list[Issue]):
    """打印检查报告"""
    print(f"\n{'=' * 60}")
    print(f"文件: {filepath}")
    print(f"{'=' * 60}\n")

    if not issues:
        print("  未发现格式问题")
        return

    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]

    for issue in issues:
        level_mark = "错误" if issue.level == "error" else "警告"
        print(f"[{level_mark}] 第 {issue.line_num} 行, 列 {issue.column}: {issue.message}")
        print(f"  > {issue.context}")
        if issue.suggestion:
            print(f"  建议: {issue.suggestion}")
        print()

    print(f"总计: {len(errors)} 个错误, {len(warnings)} 个警告")


def main():
    args = sys.argv[1:]
    skip_tables = False
    fix_mode = False
    output_path = None
    dry_run = False
    files = []

    for arg in args:
        if arg == "--check":
            fix_mode = False
        elif arg == "--fix":
            fix_mode = True
        elif arg == "--skip-tables":
            skip_tables = True
        elif arg == "--output":
            if args[-1] == arg:
                print("错误: --output 需要指定输出路径")
                sys.exit(1)
            idx = args.index(arg) + 1
            output_path = args[idx]
            args.pop(idx)
            args.remove(arg)
        elif arg == "--dry-run":
            dry_run = True
        elif arg.startswith("-"):
            print(f"未知选项: {arg}")
            print(__doc__)
            sys.exit(1)
        else:
            files.append(arg)

    if not files:
        print(__doc__)
        print("错误: 请指定要检查的文件")
        sys.exit(1)

    formatter = StyleFormatter(skip_tables=skip_tables)
    total_errors = 0
    total_warnings = 0

    for filepath_str in files:
        filepath = Path(filepath_str)
        if not filepath.exists():
            print(f"错误: 文件不存在: {filepath}")
            sys.exit(1)

        issues, formatted_content = formatter.format_file(filepath, dry_run=dry_run)
        print_report(filepath, issues)

        errors = [i for i in issues if i.level == "error"]
        warnings = [i for i in issues if i.level == "warning"]
        total_errors += len(errors)
        total_warnings += len(warnings)

        # 如果是修正模式且有问题，写入文件
        if fix_mode and issues:
            if dry_run:
                print(f"  [dry-run] 模拟修正: {filepath}")
            else:
                # 备份原文件
                backup_path = filepath.with_suffix(filepath.suffix + '.bak')
                filepath.rename(backup_path)
                # 写入修正后的内容
                filepath.write_text(formatted_content, encoding='utf-8')
                print(f"  已修正: {filepath}")
                print(f"  备份: {backup_path}")

    print(f"\n总计: {total_errors} 个错误, {total_warnings} 个警告")

    if total_errors > 0 and not fix_mode:
        print("请修正后重试。")
        sys.exit(1)
    else:
        if total_errors == 0:
            print("所有文件检查通过！")
        elif fix_mode:
            print("已修正所有格式问题。")
        sys.exit(0)


if __name__ == "__main__":
    main()