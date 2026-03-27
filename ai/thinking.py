"""Thinking process parsing strategies for different models."""

from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any, Optional
import re


class ThinkingParser(ABC):
    """Abstract base class for thinking process parsers."""

    @abstractmethod
    def parse(self, content: str, in_thinking: bool, thinking_buffer: str) -> Iterator[Dict[str, Any]]:
        """
        Parse content and yield events.

        Args:
            content: The content chunk to parse
            in_thinking: Whether we are currently inside a thinking block
            thinking_buffer: Accumulated thinking content

        Yields:
            Dict events with 'type' key: 'content', 'thinking', 'thinking_end'
        """
        pass

    @abstractmethod
    def is_thinking_tag_supported(self) -> bool:
        """Return True if this parser supports thinking tags."""
        pass


class MinimaxClaudeThinkingParser(ThinkingParser):
    """
    Thinking parser for MiniMax/Claude models.
    These models use <think>/</think> tags for thinking process.
    """

    def is_thinking_tag_supported(self) -> bool:
        return True

    def parse(self, content: str, in_thinking: bool, thinking_buffer: str) -> Iterator[Dict[str, Any]]:
        """Parse MiniMax/Claude style thinking tags."""
        if "</think>" in content:
            # End of thinking
            parts = content.split("</think>")
            for j, part in enumerate(parts):
                if j == 0:
                    # Content before </think>
                    if part:
                        if in_thinking:
                            thinking_buffer += part
                        else:
                            yield {"type": "content", "content": part}
                elif part:
                    # Content after </think> - this is actual response
                    if in_thinking and thinking_buffer.strip():
                        yield {"type": "thinking", "content": thinking_buffer.strip()}
                    thinking_buffer = ""
                    in_thinking = False
                    if part.strip():
                        yield {"type": "content", "content": part}
        elif "<think>" in content:
            # Start of thinking
            parts = content.split("<think>")
            for j, part in enumerate(parts):
                if j == 0:
                    # Content before <think>
                    if part.strip():
                        if in_thinking:
                            thinking_buffer += part
                        else:
                            yield {"type": "content", "content": part}
                elif part:
                    # Content after <think> - this is thinking
                    in_thinking = True
                    thinking_buffer += part
        elif in_thinking:
            # Continue thinking
            thinking_buffer += content
        else:
            yield {"type": "content", "content": content}

        # Return current state
        yield {"type": "state", "in_thinking": in_thinking, "buffer": thinking_buffer}


class NoThinkingParser(ThinkingParser):
    """
    Thinking parser for models that don't support thinking tags.
    Just yields content as-is.
    """

    def is_thinking_tag_supported(self) -> bool:
        return False

    def parse(self, content: str, in_thinking: bool, thinking_buffer: str) -> Iterator[Dict[str, Any]]:
        """No-op parser - just yield content."""
        if content:
            yield {"type": "content", "content": content}
        yield {"type": "state", "in_thinking": False, "buffer": ""}


class ThinkingParserFactory:
    """Factory for creating thinking parsers based on model type."""

    _parsers = {
        "minimax_claude": MinimaxClaudeThinkingParser,
        "no_thinking": NoThinkingParser,
    }

    @classmethod
    def create(cls, parser_type: str = "auto") -> ThinkingParser:
        """
        Create a thinking parser.

        Args:
            parser_type: One of 'auto', 'minimax_claude', 'no_thinking'
                       'auto' will detect based on model name

        Returns:
            ThinkingParser instance
        """
        if parser_type == "auto":
            # Default to minimax_claude style (most common)
            return MinimaxClaudeThinkingParser()

        parser_class = cls._parsers.get(parser_type, MinimaxClaudeThinkingParser)
        return parser_class()

    @classmethod
    def register(cls, name: str, parser_class: type):
        """Register a new parser type."""
        cls._parsers[name] = parser_class

    @classmethod
    def auto_detect(cls, model_name: str) -> ThinkingParser:
        """
        Auto-detect parser based on model name patterns.

        Args:
            model_name: Name of the model

        Returns:
            Appropriate ThinkingParser instance
        """
        model_lower = model_name.lower()

        # Models known to support thinking tags
        thinking_models = [
            "minimax", "claude", "gemini",
            "glm-4", "glm-4.6", "glm-4.7",
            "qwen", "yi", "deepseek"
        ]

        for model_prefix in thinking_models:
            if model_prefix in model_lower:
                return MinimaxClaudeThinkingParser()

        # Default to no thinking for unknown models
        return NoThinkingParser()
