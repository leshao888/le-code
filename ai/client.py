"""AI client with pluggable model support."""

import time
from typing import List, Dict, Any, Optional, Iterator

from openai import OpenAI, APIError, APIConnectionError, RateLimitError

from config.settings import settings
from config.models import ModelRegistry, ModelConfig


def convert_tools_to_openai_format(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert tools from Anthropic format to OpenAI format.

    Args:
        tools: List of tool definitions in Anthropic format

    Returns:
        List of tool definitions in OpenAI format
    """
    openai_tools = []
    for tool in tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {})
            }
        }
        openai_tools.append(openai_tool)
    return openai_tools


class AIClient:
    """Generic AI client with model configuration support."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the AI client.

        Args:
            model_name: Optional model name to use. If None, uses the default from settings.
        """
        # Get model configuration from registry
        if model_name:
            ModelRegistry.set_current_model(model_name)

        self.model_config = ModelRegistry.get_current_model()
        if not self.model_config:
            raise ValueError(f"Model '{model_name or settings.MODEL}' not found in registry")

        # Initialize the appropriate client based on api_type
        self._init_client()

    def _init_client(self) -> None:
        """Initialize the HTTP client based on model configuration."""
        base_url = self.model_config.get("base_url", "")
        api_key = settings.API_KEY

        if self.model_config.get("api_type") == "anthropic":
            # For Anthropic-compatible APIs (like Zhipu GLM)
            # Use OpenAI SDK with Anthropic-compatible endpoint
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=60.0,
                max_retries=3
            )
        else:
            # For OpenAI-compatible APIs
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=60.0,
                max_retries=3
            )

    @property
    def model_name(self) -> str:
        """Get the current model name."""
        return ModelRegistry.get_current_model_name()

    def create_message(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Create a message with optional streaming.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool definitions
            stream: Whether to stream the response

        Returns:
            Response dictionary from the API
        """
        try:
            kwargs = {
                "model": self.model_name,
                "max_tokens": settings.MAX_TOKENS,
                "messages": messages,
                "temperature": settings.TEMPERATURE,
            }

            if tools and self.model_config.get("supports_tools", True):
                kwargs["tools"] = convert_tools_to_openai_format(tools)

            if stream and self.model_config.get("supports_streaming", True):
                return {"stream": True, "generator": self._create_message_stream(messages, tools)}
            else:
                response = self.client.chat.completions.create(**kwargs)
                return self._format_response(response)

        except RateLimitError as e:
            print(f"\n[Rate limit exceeded. Please wait: {e}]")
            raise
        except APIConnectionError as e:
            print(f"\n[Connection error: {e}]")
            raise
        except APIError as e:
            print(f"\n[API error: {e}]")
            raise

    def _create_message_stream(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Create a streaming message generator.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool definitions

        Yields:
            Event dictionaries with 'type' and 'content' keys
        """
        try:
            kwargs = {
                "model": self.model_name,
                "max_tokens": settings.MAX_TOKENS,
                "messages": messages,
                "temperature": settings.TEMPERATURE,
                "stream": True
            }

            if tools and self.model_config.get("supports_tools", True):
                kwargs["tools"] = convert_tools_to_openai_format(tools)

            stream = self.client.chat.completions.create(**kwargs)

            # Check if model supports thinking
            supports_thinking = self.model_config.get("supports_thinking", False)
            thinking_parser = self.model_config.get("thinking_parser", "no_thinking")

            if supports_thinking and thinking_parser == "minimax_claude":
                yield from self._stream_with_thinking(stream)
            else:
                yield from self._stream_simple(stream)

        except RateLimitError as e:
            print(f"[Rate limit exceeded. Please wait: {e}]")
            raise
        except APIConnectionError as e:
            print(f"[Connection error: {e}]")
            raise
        except APIError as e:
            print(f"[API error: {e}]")
            raise

    def _stream_simple(self, stream) -> Iterator[Dict[str, Any]]:
        """Simple streaming without thinking block parsing."""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield {"type": "content", "content": chunk.choices[0].delta.content}

    def _stream_with_thinking(self, stream) -> Iterator[Dict[str, Any]]:
        """Streaming with thinking block parsing for Claude-style models."""
        thinking_buffer = ""
        in_thinking = False
        tool_call_buffer: Dict[int, Dict[str, Any]] = {}

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            finish_reason = chunk.choices[0].finish_reason

            # Handle content delta
            if delta.content:
                content = delta.content
                if "</think>" in content:
                    # End of thinking
                    parts = content.split("</think>")
                    for j, part in enumerate(parts):
                        if j == 0:
                            if part:
                                if in_thinking:
                                    thinking_buffer += part
                                else:
                                    yield {"type": "content", "content": part}
                        elif part:
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
                            if part.strip():
                                if in_thinking:
                                    thinking_buffer += part
                                else:
                                    yield {"type": "content", "content": part}
                        elif part:
                            in_thinking = True
                            thinking_buffer += part
                elif in_thinking:
                    thinking_buffer += content
                else:
                    yield {"type": "content", "content": content}

            # Handle tool calls
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    try:
                        index = tool_call.index
                        if index not in tool_call_buffer:
                            tool_call_buffer[index] = {
                                "id": "",
                                "name": "",
                                "arguments": ""
                            }
                        if tool_call.id:
                            tool_call_buffer[index]["id"] = tool_call.id
                        if tool_call.function and tool_call.function.name:
                            tool_call_buffer[index]["name"] = tool_call.function.name
                        if tool_call.function and tool_call.function.arguments:
                            tool_call_buffer[index]["arguments"] += tool_call.function.arguments
                    except Exception as e:
                        print(f"[Debug] Error parsing tool_call: {e}, tool_call: {tool_call}")

            # Yield remaining content at end
            if finish_reason in ["tool_calls", "stop", "length"]:
                if thinking_buffer.strip():
                    yield {"type": "thinking", "content": thinking_buffer.strip()}
                    thinking_buffer = ""
                if tool_call_buffer:
                    for index in sorted(tool_call_buffer.keys()):
                        yield {"type": "tool_call", "tool_call": tool_call_buffer[index]}
                    tool_call_buffer = {}

    def create_message_stream(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Iterator[str]:
        """
        Create a streaming message (simple text streaming).

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool definitions

        Yields:
            Text chunks from the streaming response
        """
        try:
            kwargs = {
                "model": self.model_name,
                "max_tokens": settings.MAX_TOKENS,
                "messages": messages,
                "temperature": settings.TEMPERATURE,
                "stream": True
            }

            if tools and self.model_config.get("supports_tools", True):
                kwargs["tools"] = convert_tools_to_openai_format(tools)

            stream = self.client.chat.completions.create(**kwargs)
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except RateLimitError as e:
            print(f"\n[Rate limit exceeded. Please wait: {e}]")
            raise
        except APIConnectionError as e:
            print(f"\n[Connection error: {e}]")
            raise
        except APIError as e:
            print(f"\n[API error: {e}]")
            raise

    def create_message_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a message with tool calls and handle tool responses.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: List of tool definitions

        Returns:
            Final response dictionary with content and tool results
        """
        response = self.create_message(messages, tools, stream=False)

        if response.get("tool_calls"):
            tool_results = []
            for tool_call in response.get("tool_calls", []):
                tool_name = tool_call.get("name")
                tool_id = tool_call.get("id")
                tool_input = tool_call.get("input", {})

                if tool_name == "web_search":
                    result = self._execute_web_search(tool_input)
                    tool_results.append({
                        "tool_call_id": tool_id,
                        "output": result
                    })
                else:
                    tool_results.append({
                        "tool_call_id": tool_id,
                        "output": f"Tool {tool_name} not implemented yet"
                    })

            if tool_results:
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": result["tool_call_id"],
                            "content": result["output"]
                        } for result in tool_results
                    ]
                })

                final_response = self.create_message(messages, tools, stream=False)
                return final_response

        return response

    def _execute_web_search(self, tool_input: Dict[str, Any]) -> str:
        """
        Execute web search using DuckDuckGo for real-time results.

        Args:
            tool_input: Dictionary containing web search parameters

        Returns:
            Formatted search results as string
        """
        try:
            from ddgs import DDGS

            query = tool_input.get("query", "")
            count = min(tool_input.get("count", 10), 10)

            all_results = []

            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=count):
                    all_results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', '')[:200]
                    })

            if not all_results:
                return "No search results found. Please try a different query."

            formatted_results = []
            for i, result in enumerate(all_results[:count], 1):
                formatted_results.append(
                    f"{i}. {result['title']}\n   URL: {result['url']}\n   {result['snippet']}"
                )

            return "\n\n".join(formatted_results)

        except ImportError:
            return "Web search is unavailable: duckduckgo-search package not installed. Please run: pip install duckduckgo-search"
        except Exception as e:
            return f"Web search error: {str(e)}"

    def _format_response(self, response) -> Dict[str, Any]:
        """
        Format the OpenAI response into a standardized dictionary.

        Args:
            response: OpenAI ChatCompletion object

        Returns:
            Formatted response dictionary
        """
        result = {
            "content": "",
            "tool_calls": [],
            "stop_reason": response.choices[0].finish_reason if response.choices else None,
            "usage": {
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
            }
        }

        if response.choices:
            choice = response.choices[0]
            if choice.message:
                if choice.message.content:
                    result["content"] = choice.message.content
                if choice.message.tool_calls:
                    for tool_call in choice.message.tool_calls:
                        result["tool_calls"].append({
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "input": eval(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments,
                        })

        return result

    def get_available_models(self) -> List[str]:
        """
        Get list of available models.

        Returns:
            List of model names
        """
        return ModelRegistry.list_all_models()

    def health_check(self) -> bool:
        """
        Check if the API is accessible.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            self.client.chat.completions.create(
                model=self.model_name,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception:
            return False


# Backward compatibility alias
MiniMaxAIClient = AIClient

# Create default client instance
default_client = AIClient()
