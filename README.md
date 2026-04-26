# Chinese Typo Formatter

中文排版格式修正工具。对中文文档、文章、邮件、消息等正式文本进行格式和排版修正。

[![Skill Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 功能特点

- ✅ **中外混排修正**：中外之间自动添加空格
- ✅ **数字与单位修正**：数字与中文、单位之间添加空格
- ✅ **标点符号规范化**：中文全角标点（，。！？），外文半角标点（,.!?）
- ✅ **引号修正**：简体中文使用直角引号「」
- ✅ **重复标点修正**：自动合并连续标点（！！！→！）
- ✅ **Markdown 格式修正**：标题、列表、超链接格式规范化
- ✅ **破折号/省略号修正**：使用中文破折号——和省略号……
- ✅ **自动化脚本**：支持批量检查和修正文件

## 适用场景

- 中文文档排版修正
- Markdown 文件格式规范化
- 邮件、消息等正式文本整理
- 中外混排格式检查
- 项目文档格式统一

## 安装

### 方式 1：从文件安装（OpenCode/Claude Code）

将 `chinese-typo-formatter` 目录复制到你的 skills 目录：

```
~/.config/opencode/skills/
```

### 方式 2：直接使用

```bash
# 克隆仓库
git clone https://github.com/your-repo/chinese-typo-formatter.git

cd chinese-typo-formatter
```

## 使用方法

### 在 AI 助手中使用（推荐）

当你说以下内容时，skill 会自动触发：

| 中文触发词 | 外文触发词 |
|------------|------------|
| 写文档 | write doc |
| 写文章 | write article |
| 写邮件 | write email |
| 编辑中文 | edit Chinese |
| 检查格式 | check format |
| 修正排版 | fix typography |
| 混排 | proofread |
| 格式化文档 | format document |
| review 文档格式 | review document format |
| proofread | proofread |

**示例：**

```
帮我检查一下这篇文章的格式
```

AI 会自动调用 skill，对文本进行排版修正。

### 使用脚本批量处理

#### 检查模式（只检查不修正）

```bash
python scripts/formatter.py --check document.md
```

#### 修正模式（检查并自动修正）

```bash
python scripts/formatter.py --fix document.md
```

#### 模拟运行（不实际写入文件）

```bash
python scripts/formatter.py --fix --dry-run document.md
```

#### 批量处理多个文件

```bash
python scripts/formatter.py --fix *.md
```

#### 跳过 Markdown 表格

```bash
python scripts/formatter.py --fix --skip-tables document.md
```

#### 指定输出文件

```bash
python scripts/formatter.py --fix --output output.md document.md
```

### 脚本选项说明

| 选项 | 说明 |
|------|------|
| `--check` | 只检查不修正（默认） |
| `--fix` | 检查并自动修正格式问题 |
| `--skip-tables` | 跳过 Markdown 表格行 |
| `--output <path>` | 指定输出文件 |
| `--dry-run` | 模拟修正，不实际写入文件 |

## 排版规则

| 类别 | 规则 | 正确示例 | 错误示例 |
|------|------|----------|----------|
| 空格 | 中外之间加空格 | 使用 GPT 模型 | 使用GPT模型 |
| 空格 | 数字与单位之间加空格 | 5 kg | 5kg |
| 标点 | 中文使用全角标点 | 你好，世界！ | Hello, world! |
| 标点 | 外文使用半角标点 | Hello, world! | Hello，world！ |
| 引号 | 简体中文使用直角引号 | 「引号」 | "引号" |
| 标点 | 禁止重复标点 | 太好了！ | 太好了！！ |
| Markdown | 标题井号后加空格 | # 标题 | #标题 |
| Markdown | 列表项中外加空格 | - 项目 | -项目 |

## 退出码

| 退出码 | 说明 |
|--------|------|
| 0 | 无错误（或已修正） |
| 1 | 发现格式错误（仅 --check 模式） |

## 修正示例

### 修正前

```markdown
#项目介绍

这是一个使用Python和JavaScript开发的项目。代码托管在GitHub上。

##功能特性

-用户管理
-数据分析
- API集成

她对他说："这是一个秘密"。这太棒了！！！
```

### 修正后

```markdown
# 项目介绍

这是一个使用 Python 和 JavaScript 开发的项目。代码托管在 GitHub 上。

## 功能特性

- 用户管理
- 数据分析
- API 集成

她对他说：「这是一个秘密」。这太棒了！
```

## 依赖

- Python 3.7+

无需额外安装依赖，仅使用标准库。

## 许可证

MIT License

## 更新日志

### v1.0.0 (2026-04-26)

- 初始版本发布
- 支持中外混排格式修正
- 支持 Markdown 格式修正
- 提供自动化检查和修正脚本