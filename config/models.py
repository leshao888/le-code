"""Model configuration and capabilities.

This module defines supported models and their capabilities.
Users can add custom models by modifying config/models.json.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, TypedDict

CONFIG_DIR = Path(__file__).parent
MODELS_CONFIG_FILE = CONFIG_DIR / "models.json"


class ModelConfig(TypedDict):
    """Type definition for model configuration."""
    provider: str
    base_url: str
    api_type: str  # "openai" or "anthropic"
    supports_thinking: bool
    thinking_parser: str  # "minimax_claude" or "no_thinking"
    supports_tools: bool
    supports_streaming: bool
    context_window: int
    description: str


# Default model definitions
DEFAULT_MODELS: Dict[str, ModelConfig] = {
    "MiniMax-M2.7": {
        "provider": "minimax",
        "base_url": "https://api.minimax.chat/v1",
        "api_type": "openai",
        "supports_thinking": True,
        "thinking_parser": "minimax_claude",
        "supports_tools": True,
        "supports_streaming": True,
        "context_window": 100000,
        "description": "MiniMax M2.7 MoE model"
    },
    "MiniMax-Text-01": {
        "provider": "minimax",
        "base_url": "https://api.minimax.chat/v1",
        "api_type": "openai",
        "supports_thinking": True,
        "thinking_parser": "minimax_claude",
        "supports_tools": True,
        "supports_streaming": True,
        "context_window": 100000,
        "description": "MiniMax Text model"
    },
    "glm-4.7": {
        "provider": "zhipu",
        "base_url": "https://open.bigmodel.cn/api/anthropic",
        "api_type": "anthropic",
        "supports_thinking": True,
        "thinking_parser": "minimax_claude",
        "supports_tools": True,
        "supports_streaming": True,
        "context_window": 128000,
        "description": "Zhipu GLM-4.7 model"
    },
    "glm-4": {
        "provider": "zhipu",
        "base_url": "https://open.bigmodel.cn/api/anthropic",
        "api_type": "anthropic",
        "supports_thinking": True,
        "thinking_parser": "minimax_claude",
        "supports_tools": True,
        "supports_streaming": True,
        "context_window": 128000,
        "description": "Zhipu GLM-4 model"
    },
    "gpt-4o": {
        "provider": "openai",
        "base_url": "https://api.openai.com/v1",
        "api_type": "openai",
        "supports_thinking": False,
        "thinking_parser": "no_thinking",
        "supports_tools": True,
        "supports_streaming": True,
        "context_window": 128000,
        "description": "OpenAI GPT-4o"
    },
    "gpt-4o-mini": {
        "provider": "openai",
        "base_url": "https://api.openai.com/v1",
        "api_type": "openai",
        "supports_thinking": False,
        "thinking_parser": "no_thinking",
        "supports_tools": True,
        "supports_streaming": True,
        "context_window": 128000,
        "description": "OpenAI GPT-4o Mini"
    },
    "qwen-plus": {
        "provider": "qwen",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_type": "openai",
        "supports_thinking": True,
        "thinking_parser": "minimax_claude",
        "supports_tools": True,
        "supports_streaming": True,
        "context_window": 100000,
        "description": "Alibaba Qwen Plus"
    },
    "deepseek-chat": {
        "provider": "deepseek",
        "base_url": "https://api.deepseek.com/v1",
        "api_type": "openai",
        "supports_thinking": False,
        "thinking_parser": "no_thinking",
        "supports_tools": True,
        "supports_streaming": True,
        "context_window": 64000,
        "description": "DeepSeek Chat"
    },
    "kimi-k2.5": {
        "provider": "moonshot",
        "base_url": "https://api.moonshot.cn/v1",
        "api_type": "openai",
        "supports_thinking": True,
        "thinking_parser": "minimax_claude",
        "supports_tools": True,
        "supports_streaming": True,
        "context_window": 128000,
        "description": "Kimi K2.5 by Moonshot"
    }
}


class ModelRegistry:
    """Singleton registry for managing available models."""

    _instance: Optional['ModelRegistry'] = None
    _models: Dict[str, ModelConfig] = {}
    _current_model_name: str = "MiniMax-M2.7"

    def __new__(cls) -> 'ModelRegistry':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self) -> None:
        """Load models from defaults and user config."""
        # Start with default models
        self._models = DEFAULT_MODELS.copy()

        # Try to load user overrides from models.json
        if MODELS_CONFIG_FILE.exists():
            try:
                with open(MODELS_CONFIG_FILE, "r", encoding="utf-8") as f:
                    user_models = json.load(f)
                    self._models.update(user_models)
            except (json.JSONDecodeError, IOError):
                pass

    def reload(self) -> None:
        """Reload models from configuration files."""
        self._load_models()

    @classmethod
    def get_model_config(cls, model_name: str) -> Optional[ModelConfig]:
        """
        Get configuration for a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Model configuration dict or None if not found
        """
        instance = cls()
        return instance._models.get(model_name)

    @classmethod
    def list_all_models(cls) -> List[str]:
        """List all available model names."""
        instance = cls()
        return list(instance._models.keys())

    @classmethod
    def get_default_model(cls) -> str:
        """Get the default model name."""
        return "MiniMax-M2.7"

    @classmethod
    def get_current_model_name(cls) -> str:
        """Get the currently selected model name."""
        instance = cls()
        return instance._current_model_name

    @classmethod
    def set_current_model(cls, model_name: str) -> bool:
        """
        Set the current model.

        Args:
            model_name: Name of the model to select

        Returns:
            True if successful, False if model not found
        """
        instance = cls()
        if model_name in instance._models:
            instance._current_model_name = model_name
            return True
        return False

    @classmethod
    def get_current_model(cls) -> Optional[ModelConfig]:
        """Get the configuration for the currently selected model."""
        instance = cls()
        return instance._models.get(instance._current_model_name)


# Backward compatibility functions
def load_models_config() -> Dict[str, ModelConfig]:
    """Load models configuration from file."""
    return ModelRegistry()._models


def get_model_config(model_name: str) -> Optional[ModelConfig]:
    """
    Get configuration for a specific model.

    Args:
        model_name: Name of the model

    Returns:
        Model configuration dict or None if not found
    """
    return ModelRegistry.get_model_config(model_name)


def list_available_models() -> List[str]:
    """List all available model names."""
    return ModelRegistry.list_all_models()


def get_default_model() -> str:
    """Get the default model name."""
    return ModelRegistry.get_default_model()


class ModelCapabilities:
    """Capabilities of a specific model configuration."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get("provider", "unknown")
        self.base_url = config.get("base_url", "")
        self.api_type = config.get("api_type", "openai")
        self.supports_thinking = config.get("supports_thinking", False)
        self.thinking_parser = config.get("thinking_parser", "no_thinking")
        self.supports_tools = config.get("supports_tools", True)
        self.supports_streaming = config.get("supports_streaming", True)
        self.context_window = config.get("context_window", 0)
        self.description = config.get("description", "")

    def __repr__(self) -> str:
        return f"ModelCapabilities({self.provider}, thinking={self.supports_thinking})"


def create_models_json_example() -> Dict[str, ModelConfig]:
    """Create an example models.json file."""
    return {
        # Example: Adding a custom model
        # "my-custom-model": {
        #     "provider": "custom",
        #     "base_url": "https://custom-api.example.com/v1",
        #     "api_type": "openai",
        #     "supports_thinking": True,
        #     "thinking_parser": "minimax_claude",
        #     "supports_tools": True,
        #     "supports_streaming": True,
        #     "context_window": 8000,
        #     "description": "My Custom Model"
        # }
    }
