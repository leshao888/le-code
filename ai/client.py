"""AI client using MiniMax API (via OpenAI SDK)."""

import os
import time
from typing import List, Dict, Any, Optional, Iterator, Union
import openai
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

from config.settings import settings


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


class MiniMaxAIClient:
    """MiniMax client wrapper using OpenAI SDK."""

    def __init__(self):
        """Initialize the MiniMax client."""
        self.client = OpenAI(
            api_key=settings.ZHIPUAI_API_KEY,
            base_url=settings.ZHIPUAI_BASE_URL,
            timeout=60.0,
            max_retries=3
        )
        self.model = settings.MODEL_NAME

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
                "model": self.model,
                "max_tokens": settings.MAX_TOKENS,
                "messages": messages,
                "temperature": settings.TEMPERATURE,
            }

            if tools:
                kwargs["tools"] = convert_tools_to_openai_format(tools)

            if stream:
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
            Dict with 'content', 'thinking', 'tool_call', or 'status' key
        """
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": settings.MAX_TOKENS,
                "messages": messages,
                "temperature": settings.TEMPERATURE,
                "stream": True
            }

            if tools:
                kwargs["tools"] = convert_tools_to_openai_format(tools)

            # Enable MiniMax extended features (thinking, plugins)
            kwargs["extra_headers"] = {
                "minimax-extension": '{"plugins": {"search": {"enable": true}}, "thinking": {"type": "extension", "enable": true}}'
            }

            stream = self.client.chat.completions.create(**kwargs)

            # Buffer for accumulating tool call data
            tool_call_buffer = {}
            # Buffer for thinking content
            thinking_buffer = ""
            in_thinking = False

            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason

                # Check for extended data (thinking, plugin info)
                if hasattr(chunk, 'extensions') and chunk.extensions:
                    ext = chunk.extensions
                    # Check for thinking content
                    if 'thinking' in ext:
                        thinking_content = ext['thinking']
                        if isinstance(thinking_content, str) and thinking_content:
                            thinking_buffer += thinking_content
                            yield {"type": "thinking", "content": thinking_content}
                    # Check for plugin status
                    if 'plugins' in ext:
                        plugin_info = ext['plugins']
                        if isinstance(plugin_info, dict):
                            status = plugin_info.get('status', '')
                            if status:
                                yield {"type": "status", "content": status}

                # Check for content
                if delta.content:
                    content = delta.content

                    # Check if this chunk contains thinking markers (MiniMax uses <think> and </think>)
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
                                # Content after </think> - this is the actual response
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

                # Check for tool calls
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
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

                # Check if this is the final chunk - yield any remaining tool calls or thinking
                if finish_reason in ["tool_calls", "stop", "length"]:
                    # Yield any remaining thinking content
                    if thinking_buffer.strip():
                        yield {"type": "thinking", "content": thinking_buffer.strip()}
                        thinking_buffer = ""
                    if tool_call_buffer:
                        for index in sorted(tool_call_buffer.keys()):
                            yield {"type": "tool_call", "tool_call": tool_call_buffer[index]}
                        tool_call_buffer = {}

        except RateLimitError as e:
            print(f"[Rate limit exceeded. Please wait: {e}]")
            raise
        except APIConnectionError as e:
            print(f"[Connection error: {e}]")
            raise
        except APIError as e:
            print(f"[API error: {e}]")
            raise


    def create_message_stream(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Iterator[str]:
        """
        Create a streaming message.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool definitions

        Yields:
            Text chunks from the streaming response
        """
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": settings.MAX_TOKENS,
                "messages": messages,
                "temperature": settings.TEMPERATURE,
                "stream": True
            }

            if tools:
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
                # Search with real-time results
                for result in ddgs.text(query, max_results=count):
                    all_results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', '')[:200]
                    })

            if not all_results:
                return "No search results found. Please try a different query."

            # Format and return results
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
        return [
            settings.MODEL_NAME,
            "MiniMax-Text-01",
            "MiniMax-Embeddings-01",
        ]

    def health_check(self) -> bool:
        """
        Check if the API is accessible.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            self.client.chat.completions.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception:
            return False


# Create default client instance
default_client = MiniMaxAIClient()