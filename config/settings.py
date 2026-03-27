"""Configuration management for le-code terminal AI assistant."""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get config directory
CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / "config.json"
EXAMPLE_CONFIG_FILE = CONFIG_DIR / "config.example.json"


def _load_config() -> dict:
    """Load configuration from config.json file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Warning] Failed to load config.json: {e}")
            return {}
    else:
        if EXAMPLE_CONFIG_FILE.exists():
            print("[Info] config.json not found, please copy config.example.json to config.json and fill in your API key")
        return {}


def _get_config_value(key: str, default=None):
    """Get config value with environment variable override support."""
    # Environment variable takes priority (e.g., MINIMAX_API_KEY, MINIMAX_BASE_URL)
    env_key = f"MINIMAX_{key.upper()}"
    if env_key in os.environ:
        return os.environ[env_key]

    # Then check config file
    config = _load_config()
    return config.get(key, default)


class Settings:
    """Application settings."""

    # API Configuration - supports config.json and environment variables
    API_KEY: str = _get_config_value("api_key", "")
    BASE_URL: str = _get_config_value("base_url", "https://api.minimax.chat/v1")
    MODEL_NAME: str = _get_config_value("model_name", "MiniMax-Text-01")

    # Token limits
    MAX_TOKENS: int = int(_get_config_value("max_tokens", "8192"))
    TEMPERATURE: float = float(_get_config_value("temperature", "0.6"))

    # File and memory configuration
    WORKING_DIR: Path = Path.cwd()
    MEMORY_DIR: Path = Path.home() / ".claude" / "memory" / "le-code"
    SESSIONS_DIR: Path = Path.home() / ".claude" / "projects" / "le-code"

    # Shell configuration
    SHELL_TIMEOUT: int = int(os.getenv("LE_CODE_SHELL_TIMEOUT", "30"))
    MAX_OUTPUT_LENGTH: int = int(os.getenv("LE_CODE_MAX_OUTPUT_LENGTH", "10000"))

    # UI configuration
    ENABLE_COLORS: bool = True
    SHOW_TOOL_CALLS: bool = True

    def __post_init__(self):
        """Ensure required directories exist."""
        self.MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls) -> bool:
        """Validate required settings."""
        if not cls.API_KEY:
            print("Error: API_KEY is not set.")
            print("Please set it in config.json or via MINIMAX_API_KEY environment variable")
            print(f"Copy {EXAMPLE_CONFIG_FILE} to {CONFIG_FILE} and fill in your API key")
            return False
        return True


# Create default settings instance
settings = Settings()
settings.__post_init__()
