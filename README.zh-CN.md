# Paper Download MCP Server

[English](https://github.com/Oxidane-bot/paper-download-mcp/blob/main/README.md) | 简体中文

一个用于下载学术论文的 MCP 服务，支持 DOI、arXiv ID、URL。

## 你能用到什么

- `paper_download`：下载一篇或多篇论文（单次 1-50 条）
- `paper_get_metadata`：只获取元数据，不下载 PDF
- 可选 PDF 转 Markdown（`to_markdown`）

## 快速开始（MCP 客户端配置）

配置前先确认本机可用 `uvx`：

```bash
uvx --version
```

### Claude Code

按项目作用域添加 MCP：

```bash
claude mcp add --transport stdio --scope project --env PAPER_DOWNLOAD_EMAIL=your-email@university.edu paper-download -- uvx paper-download-mcp
```

这条命令会在当前项目写入 `.mcp.json`。等价配置：

```json
{
  "mcpServers": {
    "paper-download": {
      "command": "uvx",
      "args": ["paper-download-mcp"],
      "env": {
        "PAPER_DOWNLOAD_EMAIL": "your-email@university.edu"
      }
    }
  }
}
```

### Codex

用 CLI 添加：

```bash
codex mcp add paper-download --env PAPER_DOWNLOAD_EMAIL=your-email@university.edu -- uvx paper-download-mcp
```

等价 `~/.codex/config.toml` 配置：

```toml
[mcp_servers.paper-download]
command = "uvx"
args = ["paper-download-mcp"]

[mcp_servers.paper-download.env]
PAPER_DOWNLOAD_EMAIL = "your-email@university.edu"
```

### Claude Desktop

编辑 Claude Desktop 的 MCP 配置文件：

- macOS：`~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows：`%APPDATA%\\Claude\\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "paper-download": {
      "command": "uvx",
      "args": ["paper-download-mcp"],
      "env": {
        "PAPER_DOWNLOAD_EMAIL": "your-email@university.edu"
      }
    }
  }
}
```

修改后重启 Claude Desktop。

## 配置说明

### 必需

- `PAPER_DOWNLOAD_EMAIL`：Unpaywall API 需要该邮箱。

### 可选（高级）

- `PAPER_DOWNLOAD_OUTPUT_DIR`：全局兜底下载目录。

大多数情况下不需要设置 `PAPER_DOWNLOAD_OUTPUT_DIR`。如果某次调用要写到特定目录，直接在 `paper_download` 里传 `output_dir`。

为了兼容历史配置，也支持以下旧变量：

- `SCIHUB_CLI_EMAIL`
- `SCIHUB_OUTPUT_DIR`

## 工具说明

### `paper_download`

支持可配置并发下载（默认 `parallel=10`）。
当 `parallel=1` 时按顺序下载，且每条之间间隔 2 秒。
路由默认优先走 OpenAlex 与 Unpaywall（OA 优先）；MCP 运行时默认关闭 CORE。

参数：

- `identifiers`（必填）：`list[str]`，1-50 项
- `output_dir`（可选）：下载目录，默认使用运行时兜底（`PAPER_DOWNLOAD_OUTPUT_DIR` 或 `./downloads`）
- `parallel`（可选）：并发 worker 数，`1-50`（默认 `10`）
- `to_markdown`（可选）：是否转 Markdown，默认 `false`
- `md_output_dir`（可选）：Markdown 输出目录，默认 `<output_dir>/md`

示例：

```text
paper_download(["10.1038/nature12373"])
paper_download(["10.1038/nature12373", "2301.00001"], output_dir="/path/to/papers")
paper_download(["10.1038/nature12373", "10.1126/science.169.3946.635"], parallel=10)
paper_download(["10.1038/nature12373"], to_markdown=true)
```

### `paper_get_metadata`

快速获取元数据（不下载 PDF）。

参数：

- `identifier`（必填）：DOI、arXiv ID 或 URL

示例：

```text
paper_get_metadata("10.1038/nature12373")
```

## 常见问题

### 报错 `PAPER_DOWNLOAD_EMAIL environment variable is required`

在 MCP 配置的 `env` 中设置 `PAPER_DOWNLOAD_EMAIL`。

### 报错 `uvx: command not found`

先安装 `uv`，再重新执行 MCP 配置命令。

### 下载目录报错（无权限或路径不存在）

在工具调用里显式传可写目录：

```text
paper_download(["10.1038/nature12373"], output_dir="/absolute/path")
```

## 法律提示

该工具会访问多个论文来源（包括 Unpaywall 和 Sci-Hub）。请自行确保使用行为符合你所在地区的法律与版权要求。

## 许可证

MIT，见 `LICENSE`。
