"""Configuration management for le-code terminal AI assistant."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings."""

    # API Configuration
    ZHIPUAI_API_KEY: str = os.getenv("ZHIPUAI_API_KEY", "")
    ZHIPUAI_BASE_URL: str = "https://api.minimax.chat/v1"
    MODEL_NAME: str = os.getenv("LE_CODE_MODEL", "glm-4.6v")

    # Token limits
    MAX_TOKENS: int = int(os.getenv("LE_CODE_MAX_TOKENS", "8192"))
    TEMPERATURE: float = float(os.getenv("LE_CODE_TEMPERATURE", "0.6"))

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
        if not cls.ZHIPUAI_API_KEY:
            print("Error: ZHIPUAI_API_KEY environment variable is not set.")
            print("Please set it with: export ZHIPUAI_API_KEY=your-api-key")
            print("Or create a .env file with: ZHIPUAI_API_KEY=your-api-key")
            return False
        return True


# Create default settings instance
settings = Settings()
settings.__post_init__()
