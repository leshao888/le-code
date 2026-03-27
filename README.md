# le-code - Terminal AI Programming Assistant

> **全程使用 Claude Code + MiniMax 2.7 模型开发实现**

一个类似 Claude Code 的终端 AI 编程工具，支持配置不同模型和 API，帮助你回答编程问题、生成和修改代码。

## 特性

- 🚀 **多模型支持**: 通过配置文件轻松切换不同模型（MiniMax、OpenAI 兼容接口等）
- 📁 **文件操作**: 支持读取、写入、搜索和编辑代码文件
- 💻 **命令执行**: 在终端中执行 shell 命令并获取输出
- 🔍 **网络搜索**: 内置 DuckDuckGo 搜索，获取实时信息
- 💾 **对话记忆**: 自动保存对话历史，支持多会话管理
- 🎨 **美观界面**: 使用 Rich 库提供彩色高亮和 Markdown 渲染
- ⚙️ **灵活配置**: 支持配置文件和环境变量两种配置方式

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

```bash
# 复制配置示例文件
cp config/config.example.json config/config.json

# 编辑 config/config.json，填入你的 API Key 和模型信息
```

**配置文件示例：**

```json
{
    "api_key": "your-api-key-here",
    "base_url": "https://api.minimax.chat/v1",
    "model_name": "MiniMax-Text-01",
    "max_tokens": 8192,
    "temperature": 0.6
}
```

### 获取 API Key

1. 访问 [MiniMax 开放平台](https://www.minimax.chat/) 或你的 AI 模型提供商
2. 注册并登录账户
3. 在 API Keys 页面创建 API Key

### 环境变量配置（可选）

你也可以使用环境变量配置，优先级高于配置文件：

```bash
export MINIMAX_API_KEY="your-api-key"
export MINIMAX_BASE_URL="https://api.minimax.chat/v1"
export MINIMAX_MODEL_NAME="MiniMax-Text-01"
```

## 使用

### 启动

```bash
python main.py
```

或使用快捷脚本：

```bash
# Windows
run.bat

# Linux/Mac
./run.sh
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

#### 7. 网络搜索

```
> 搜索一下最新的 Python Web 框架
```

## 配置选项

### 配置文件 (config/config.json)

```json
{
    "api_key": "your-api-key",
    "base_url": "https://api.minimax.chat/v1",
    "model_name": "MiniMax-Text-01",
    "max_tokens": 8192,
    "temperature": 0.6
}
```

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `MINIMAX_API_KEY` | API Key | 必填 |
| `MINIMAX_BASE_URL` | API Base URL | `https://api.minimax.chat/v1` |
| `MINIMAX_MODEL_NAME` | 模型名称 | `MiniMax-Text-01` |
| `MINIMAX_MAX_TOKENS` | 最大 token 数 | `8192` |
| `MINIMAX_TEMPERATURE` | 温度参数 (0-1) | `0.6` |
| `LE_CODE_SHELL_TIMEOUT` | 命令超时时间(秒) | `30` |
| `LE_CODE_MAX_OUTPUT_LENGTH` | 最大输出长度 | `10000` |

### 切换模型

只需修改 `config/config.json` 中的配置即可切换模型：

```json
{
    "api_key": "your-new-api-key",
    "base_url": "https://api.new-provider.com/v1",
    "model_name": "new-model-name",
    "max_tokens": 8192,
    "temperature": 0.6
}
```

## 项目结构

```
le-code/
├── main.py                 # 主入口
├── cli/
│   ├── ui.py              # 终端 UI 组件
│   ├── input_handler.py   # 用户输入处理
│   └── output_formatter.py # 输出格式化
├── ai/
│   ├── client.py          # AI 客户端 (OpenAI SDK 兼容)
│   ├── tools.py           # 工具函数定义
│   └── error_handler.py   # 错误处理
├── tools/
│   ├── file_ops.py        # 文件操作工具
│   ├── shell.py           # Shell 命令执行
│   └── code_ops.py        # 代码操作工具
├── memory/
│   └── memory_manager.py  # 对话记忆管理
├── config/
│   ├── settings.py        # 配置管理
│   ├── config.json        # 用户配置 (不提交)
│   └── config.example.json # 配置示例
├── requirements.txt
├── .env.example
└── README.md
```

## 安全说明

- **API Key 安全**: 请勿将 `config/config.json` 或 `.env` 提交到代码仓库（已加入 .gitignore）
- **命令执行**: 工具会自动过滤危险命令
- **文件操作**: 仅允许访问当前工作目录及其子目录

## 常见问题

### Q: 如何获取 API Key？

A: 访问你的 AI 模型提供商开放平台（如 MiniMax、OpenAI 等），注册账户后在 API Keys 页面创建。

### Q: 如何切换不同的模型？

A: 修改 `config/config.json` 文件中的 `model_name` 和 `base_url` 配置即可。

### Q: 支持哪些模型？

A: 支持所有 OpenAI SDK 兼容的模型，包括 MiniMax、GLM、OpenAI 等。只需配置相应的 base_url 和 model_name。

### Q: 对话历史保存在哪里？

A: 保存在 `~/.claude/memory/le-code/` 目录下。

### Q: 如何清除对话历史？

A: 使用 `/clear` 命令清除当前会话的历史。

### Q: 环境变量和配置文件哪个优先？

A: 环境变量优先级更高，会覆盖配置文件中的值。

## 故障排除

### 连接 API 失败

1. 检查 API Key 是否正确
2. 确认 base_url 是否正确
3. 确认网络连接正常
4. 检查 API Key 是否有足够的额度

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
cp config/config.example.json config/config.json
# 编辑 config/config.json

# 运行
python main.py
```

### 添加新工具

1. 在 `ai/tools.py` 中定义新工具
2. 在 `tools/` 中实现工具逻辑
3. 在 `main.py` 的 `_execute_tool` 方法中添加处理逻辑

## 许可证

MIT License

## 当前实现状态

### 开发工具

- **开发过程**: 全程使用 Claude Code + MiniMax 2.7 模型驱动开发
- **SDK**: 使用 OpenAI Python SDK（MiniMax OpenAI 兼容接口）
- **接口**: OpenAI `chat.completions.create` 兼容接口
- **工具调用**: 支持 Function Calling / Tool Use
- **思考过程**: 支持 `<think>`/`</think>` 标签解析（MiniMax/Claude 风格）

### 已测试模型

- ✅ **MiniMax 系列**: `MiniMax-Text-01`、`MiniMax-M2.7` 等（通过 OpenAI 兼容接口）
- ✅ **智谱 GLM 系列**: `glm-4` 等（通过 OpenAI 兼容接口）
- 🔄 **其他 OpenAI 兼容模型**: 理论上支持，详情见下方限制

### 当前限制

1. **思考过程标签**: 代码中针对 `<think>`/`</think>` 格式进行了解析，这是 MiniMax 和 Claude 等模型的格式。如果切换到不支持此格式的模型，思考过程可能无法正常显示。

2. **模型列表**: `get_available_models()` 目前硬编码了 MiniMax 模型列表，后续会改为动态获取。

3. **工具支持**: 工具调用（Function Calling）功能需要模型支持，OpenAI 原生接口模型均可使用。

### 后续计划

- [ ] 支持更多 OpenAI 兼容模型（Qwen、Yi、DeepSeek 等）
- [ ] 动态获取可用模型列表
- [ ] 适配不同模型的思考过程标签格式
- [ ] 添加更多工具和功能
- [ ] 支持 Claude API 原生接口（用于不支持 OpenAI 兼容接口的场景）

## 贡献

欢迎提交 Issue 和 Pull Request！
