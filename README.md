# le-code - Terminal AI Programming Assistant

> **全程使用 Claude Code + MiniMax 2.7 模型开发实现**

一个类似 Claude Code 的终端 AI 编程工具，支持配置不同模型和 API，帮助你回答编程问题、生成和修改代码。

## 特性

- 🚀 **多模型支持**: 通过配置文件轻松切换不同模型（MiniMax、Kimi、OpenAI 兼容接口等）
- 📁 **文件操作**: 支持读取、写入、搜索和编辑代码文件
- 💻 **命令执行**: 在终端中执行 shell 命令并获取输出
- 🔍 **网络搜索**: 内置 DuckDuckGo 搜索，获取实时信息
- 💾 **对话记忆**: 自动保存对话历史，支持多会话管理
- 🎨 **美观界面**: 使用 Rich 库提供彩色高亮和 Markdown 渲染
- ⚙️ **灵活配置**: 支持配置文件和环境变量两种配置方式
- 🔌 **可插拔架构**: 通过 `models.json` 可轻松添加自定义模型

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
    "model": "MiniMax-M2.7",
    "max_tokens": 8192,
    "temperature": 1.0
}
```

### 获取 API Key

1. 访问 [MiniMax 开放平台](https://www.minimax.chat/)、[Moonshot](https://www.moonshot.cn/) 或你的 AI 模型提供商
2. 注册并登录账户
3. 在 API Keys 页面创建 API Key

### 环境变量配置（可选）

你也可以使用环境变量配置，优先级高于配置文件：

```bash
export AI_API_KEY="your-api-key"
export AI_MODEL="MiniMax-M2.7"
export AI_MAX_TOKENS="8192"
export AI_TEMPERATURE="1.0"
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
    "model": "MiniMax-M2.7",
    "max_tokens": 8192,
    "temperature": 1.0
}
```

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `AI_API_KEY` | API Key | 必填 |
| `AI_MODEL` | 模型名称 | `MiniMax-M2.7` |
| `AI_MAX_TOKENS` | 最大 token 数 | `8192` |
| `AI_TEMPERATURE` | 温度参数 (0-1) | `0.6` |
| `LE_CODE_SHELL_TIMEOUT` | 命令超时时间(秒) | `30` |
| `LE_CODE_MAX_OUTPUT_LENGTH` | 最大输出长度 | `10000` |

### 切换模型

#### 方式一：修改 config.json

修改 `config/config.json` 中的 `model` 字段：

```json
{
    "api_key": "your-api-key",
    "model": "kimi-k2.5",
    "max_tokens": 8192,
    "temperature": 1.0
}
```

#### 方式二：添加自定义模型

1. 在 `config/models.json` 中添加模型配置：

```json
{
    "my-custom-model": {
        "provider": "myprovider",
        "base_url": "https://api.myprovider.com/v1",
        "api_type": "openai",
        "supports_thinking": true,
        "thinking_parser": "minimax_claude",
        "supports_tools": true,
        "supports_streaming": true,
        "context_window": 128000,
        "description": "My Custom Model"
    }
}
```

2. 在 `config/config.json` 中切换到新模型：

```json
{
    "api_key": "your-api-key",
    "model": "my-custom-model",
    ...
}
```

### 模型配置项说明

| 字段 | 说明 | 可选值 |
|------|------|--------|
| `provider` | 提供商名称 | `minimax`, `moonshot`, `openai`, `deepseek`, `zhipu`, `qwen` 等 |
| `base_url` | API 端点 | 如 `https://api.moonshot.cn/v1` |
| `api_type` | API 类型 | `openai` 或 `anthropic` |
| `supports_thinking` | 是否支持思考过程 | `true` / `false` |
| `thinking_parser` | 思考过程解析器 | `minimax_claude`（支持思考）或 `no_thinking` |
| `supports_tools` | 是否支持工具调用 | `true` / `false` |
| `supports_streaming` | 是否支持流式输出 | `true` / `false` |
| `context_window` | 上下文窗口大小 | 整数，如 `128000` |
| `description` | 模型描述 | 字符串 |

### 内置支持模型

| 模型 | Provider | 支持思考 |
|------|----------|----------|
| MiniMax-M2.7 | minimax | ✅ |
| MiniMax-Text-01 | minimax | ✅ |
| glm-4.7 | zhipu | ✅ |
| glm-4 | zhipu | ✅ |
| gpt-4o | openai | ❌ |
| gpt-4o-mini | openai | ❌ |
| qwen-plus | qwen | ✅ |
| deepseek-chat | deepseek | ❌ |
| kimi-k2.5 | moonshot | ✅ |

## 项目结构

```
le-code/
├── main.py                 # 主入口
├── cli/
│   ├── ui.py              # 终端 UI 组件
│   ├── input_handler.py   # 用户输入处理
│   └── output_formatter.py # 输出格式化
├── ai/
│   ├── client.py          # AI 客户端 (支持多模型)
│   ├── tools.py           # 工具函数定义
│   └── thinking.py        # 思考过程解析
├── tools/
│   ├── file_ops.py        # 文件操作工具
│   ├── shell.py           # Shell 命令执行
│   └── code_ops.py        # 代码操作工具
├── memory/
│   └── memory_manager.py  # 对话记忆管理
├── config/
│   ├── settings.py        # 配置管理
│   ├── models.py         # 模型注册表
│   ├── models.json       # 用户自定义模型配置
│   ├── config.json       # 用户配置 (不提交)
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

A: 访问你的 AI 模型提供商开放平台（如 MiniMax、Moonshot、OpenAI 等），注册账户后在 API Keys 页面创建。

### Q: 如何切换不同的模型？

A: 修改 `config/config.json` 文件中的 `model` 配置即可切换模型。预置模型包括 MiniMax、Kimi、GLM、GPT、Qwen、DeepSeek 等。

### Q: 支持哪些模型？

A: 支持所有 OpenAI SDK 兼容的模型，包括 MiniMax、Moonshot (Kimi)、GLM、OpenAI、Qwen、DeepSeek 等。只需配置相应的 base_url 和 model。

### Q: 如何添加自定义模型？

A: 在 `config/models.json` 中添加新模型配置，参考上文的"添加自定义模型"部分。

### Q: 对话历史保存在哪里？

A: 保存在 `~/.claude/memory/le-code/` 目录下。

### Q: 如何清除对话历史？

A: 使用 `/clear` 命令清除当前会话的历史。

### Q: 环境变量和配置文件哪个优先？

A: 环境变量优先级更高，会覆盖配置文件中的值。

### Q: Kimi K2.5 的 temperature 必须是多少？

A: Kimi K2.5 只支持 `temperature=1.0`，需要在配置文件中设置。

## 故障排除

### 连接 API 失败

1. 检查 API Key 是否正确
2. 确认模型名称是否正确
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

# 测试连接
python test_connection.py

# 运行
python main.py
```

### 测试不同模型

```bash
# 测试 MiniMax
python -c "from ai.client import AIClient; c = AIClient('MiniMax-M2.7'); print(c.health_check())"

# 测试 Kimi
python -c "from ai.client import AIClient; c = AIClient('kimi-k2.5'); print(c.health_check())"
```

## 许可证

MIT License

## 当前实现状态

### 开发工具

- **开发过程**: 全程使用 Claude Code + MiniMax 2.7 模型驱动开发
- **模型架构**: 重构为可插拔的 `ModelRegistry` 架构，支持通过配置文件添加自定义模型
