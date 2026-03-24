# le-code - Terminal AI Programming Assistant

一个类似 Claude Code 的终端 AI 编程工具，使用智谱 AI 的 GLM-4.7 模型帮助你回答编程问题、生成和修改代码。

## 特性

- 🚀 **智能代码生成**: 使用 GLM-4.7 高智能模型进行代码生成和修改
- 📁 **文件操作**: 支持读取、写入、搜索和编辑代码文件
- 💻 **命令执行**: 在终端中执行 shell 命令并获取输出
- 💾 **对话记忆**: 自动保存对话历史，支持多会话管理
- 🎨 **美观界面**: 使用 Rich 库提供彩色高亮和 Markdown 渲染
- 💰 **成本优化**: 支持智谱 AI Coding Plan，享受优惠套餐

## 安装

### 前置要求

- Python 3.9 或更高版本
- pip 包管理器

### 安装步骤

1. 克隆或下载本项目

```bash
cd le-code
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置 API Key

创建 `.env` 文件或设置环境变量：

```bash
# 方式 1: 创建 .env 文件
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key

# 方式 2: 设置环境变量
export ZHIPUAI_API_KEY="your-api-key-here"
```

### 获取 API Key

1. 访问 [智谱 AI 开放平台](https://bigmodel.cn/)
2. 注册并登录账户
3. 在 API Keys 页面创建 API Key
4. （推荐）订阅 [GLM Coding Plan](https://bigmodel.cn/glm-coding) 享受优惠套餐

## 使用

### 启动

```bash
python main.py
```

### 基本命令

在终端中你可以使用以下特殊命令：

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助信息 |
| `/clear` | 清除对话历史 |
| `/exit` | 退出程序 |
| `/sessions` | 列出所有保存的会话 |
| `/save [filename]` | 保存当前会话 |
| `/load <session_id>` | 加载指定的会话 |
| `/model` | 显示当前模型信息 |
| `/context` | 显示对话上下文信息 |

### 使用示例

#### 1. 生成代码

```
> 帮我创建一个 Python 文件 hello.py，打印 "Hello, World!"
```

#### 2. 读取文件

```
> 读取 hello.py 文件的内容
```

#### 3. 修改代码

```
> 在 hello.py 中添加一个函数，计算斐波那契数列
```

#### 4. 执行代码

```
> 执行 hello.py 文件
```

#### 5. 搜索文件

```
> 搜索所有的 .py 文件
```

#### 6. 搜索内容

```
> 在所有 Python 文件中搜索 "def" 关键字
```

## Coding Plan 配置

### 什么是 Coding Plan？

GLM Coding Plan 是智谱 AI 专为 AI 编程打造的订阅套餐，提供高额用量和优惠价格。

### 套餐对比

| 套餐 | 价格 | 每 5 小时限额 | 每周限额 |
|------|------|---------------|-----------|
| Lite | ¥49/月 | 约 80 次 prompts | 约 400 次 |
| Pro | ¥149/月 | 约 400 次 prompts | 约 2000 次 |
| Max | ¥299/月 | 约 1600 次 prompts | 约 8000 次 |

### 配置方式

1. 订阅 Coding Plan 套餐
2. 使用相同的 API Key
3. 工具会自动使用 Coding Plan base URL

### 优势

- 相当于月订阅费用的 15-30 倍额度
- 55+ Tokens/秒的生成速度
- 稳定无忧，无封号风险
- 支持图像视频理解、联网搜索等功能

## 配置选项

可以通过环境变量自定义配置：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ZHIPUAI_API_KEY` | 智谱 AI API Key | 必填 |
| `LE_CODE_MODEL` | 使用的模型 | `glm-4.7` |
| `LE_CODE_MAX_TOKENS` | 最大 token 数 | `8192` |
| `LE_CODE_TEMPERATURE` | 温度参数 (0-1) | `0.6` |
| `LE_CODE_SHELL_TIMEOUT` | 命令超时时间(秒) | `30` |
| `LE_CODE_MAX_OUTPUT_LENGTH` | 最大输出长度 | `10000` |

## 项目结构

```
le-code/
├── main.py                 # 主入口
├── cli/
│   ├── ui.py              # 终端 UI 组件
│   ├── input_handler.py   # 用户输入处理
│   └── output_formatter.py # 输出格式化
├── ai/
│   ├── client.py          # 智谱 AI 客户端
│   ├── tools.py           # 工具函数定义
│   └── error_handler.py   # 错误处理
├── tools/
│   ├── file_ops.py        # 文件操作工具
│   ├── shell.py           # Shell 命令执行
│   └── code_ops.py        # 代码操作工具
├── memory/
│   └── memory_manager.py  # 对话记忆管理
├── config/
│   └── settings.py        # 配置管理
├── requirements.txt
├── .env.example
└── README.md
```

## 安全说明

- **API Key 安全**: 请勿将 API Key 提交到代码仓库
- **命令执行**: 工具会自动过滤危险命令
- **文件操作**: 仅允许访问当前工作目录及其子目录

## 常见问题

### Q: 如何获取 API Key？

A: 访问 [智谱 AI 开放平台](https://bigmodel.cn/) 注册账户后在 API Keys 页面创建。

### Q: 为什么建议使用 Coding Plan？

A: Coding Plan 提供大幅优惠，相当于月费用的 15-30 倍额度，适合高频使用。

### Q: 支持哪些模型？

A: 支持 GLM-4.7、GLM-4.6、GLM-4.5、GLM-4.5-Air 等模型。

### Q: 如何查看使用量？

A: 登录智谱 AI 开放平台，在用量统计页面查看套餐使用情况。

### Q: 对话历史保存在哪里？

A: 保存在 `~/.claude/memory/le-code/` 目录下。

### Q: 如何清除对话历史？

A: 使用 `/clear` 命令清除当前会话的历史。

## 故障排除

### 连接 API 失败

1. 检查 API Key 是否正确
2. 确认网络连接正常
3. 检查 API Key 是否有足够的额度

### 命令执行超时

调整环境变量 `LE_CODE_SHELL_TIMEOUT` 增加超时时间。

### 文件编码错误

工具会自动检测文件编码。如果二进制文件无法解码，会提示跳过。

## 开发

### 运行开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API Key
export ZHIPUAI_API_KEY="your-dev-api-key"

# 运行
python main.py
```

### 添加新工具

1. 在 `ai/tools.py` 中定义新工具
2. 在 `tools/` 中实现工具逻辑
3. 在 `main.py` 的 `_execute_tool` 方法中添加处理逻辑

## 参考资料

- [智谱 AI 官方文档](https://docs.bigmodel.cn/cn/api/introduction)
- [GLM Coding Plan 套餐](https://docs.bigmodel.cn/cn/coding-plan/overview)
- [Claude API 兼容接口](https://docs.bigmodel.cn/cn/guide/develop/claude/introduction)
- [Anthropic Python SDK](https://docs.anthropic.com/en/api/python)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**Powered by ZhipuAI GLM-4.7**
