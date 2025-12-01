# MCP 工具测试指南

## ✅ 配置已完成

MCP 服务器 `paper-download` 已配置并连接成功。

## 🧪 如何测试

### 方式 1：在新的 Claude Code 对话中测试

1. **开始一个新对话**（重要！当前对话是在配置之前开始的）
2. 尝试以下命令：

#### 测试 1: 获取论文元数据（快速，无下载）
```
获取论文 10.1038/nature12373 的元数据
```

**预期结果**：
- 返回 JSON 格式的元数据
- 包含：DOI、标题、年份、期刊、开放获取状态

#### 测试 2: 下载单篇论文
```
下载 DOI 为 10.1038/nature12373 的论文到 ./test_downloads 目录
```

**预期结果**：
- 下载 PDF 文件
- 文件名格式：`[2013] - Nanometre-scale thermometry in a living cell.pdf`
- 返回文件路径和元数据

#### 测试 3: 批量下载
```
批量下载这些论文到 ./test_downloads：
- 10.1038/nature12373
- 10.1126/science.1234567
```

**预期结果**：
- 顺序下载两篇论文
- 显示进度和统计信息
- 列出成功和失败的下载

### 方式 2：命令行测试

如果 MCP 工具在对话中不可用，可以直接测试：

```bash
# 检查服务器状态
claude mcp list

# 查看 paper-download 详情
claude mcp get paper-download

# 直接调用工具测试
cd /home/oxidane/projects/paper-download-mcp
SCIHUB_CLI_EMAIL="test@university.edu" uv run python test_tools.py
SCIHUB_CLI_EMAIL="test@university.edu" uv run python test_metadata.py
```

## 🔧 故障排除

### 工具不可用？

1. **确认服务器已连接**：
   ```bash
   claude mcp list
   # 应该看到：paper-download: ... - ✓ Connected
   ```

2. **检查是否在新对话中**：
   - 当前对话可能在配置前启动
   - 开始新对话以加载新配置的工具

3. **检查批准状态**：
   - `.mcp.json` 中的项目服务器需要批准
   - 启动时应该有提示
   - 如果没有提示，运行：`claude mcp reset-project-choices`

4. **查看配置**：
   ```bash
   cat .mcp.json
   cat .claude/settings.json
   ```

## 📊 可用的 3 个 MCP 工具

1. **paper_metadata** - 获取论文元数据
   - 输入：DOI 或 URL
   - 输出：JSON 格式的元数据
   - 速度：<1 秒

2. **paper_download** - 下载单篇论文
   - 输入：DOI/URL，输出目录（可选）
   - 输出：Markdown 格式的下载详情
   - 速度：2-10 秒

3. **paper_batch_download** - 批量下载
   - 输入：DOI/URL 列表（1-50），输出目录（可选）
   - 输出：Markdown 格式的批量摘要
   - 速度：~3-5 秒/论文

## 🎉 成功标志

如果看到 Claude Code 调用以下工具，说明配置成功：
- `mcp__paper-download__paper_metadata`
- `mcp__paper-download__paper_download`
- `mcp__paper-download__paper_batch_download`

---

**提示**：确保在**新的 Claude Code 对话**中测试，因为 MCP 工具在会话启动时加载。
