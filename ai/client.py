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
            Dict with 'content' or 'tool_call' key
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

            # Buffer for accumulating tool call data
            tool_call_buffer = {}

            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                # Check for content
                if delta.content:
                    yield {"type": "content", "content": delta.content}

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

                # Check if this is the final chunk for tool calls
                if chunk.choices[0].finish_reason == "tool_calls":
                    # Yield all accumulated tool calls
                    for index in sorted(tool_call_buffer.keys()):
                        yield {"type": "tool_call", "tool_call": tool_call_buffer[index]}
                    tool_call_buffer = {}

                # Check if this is the final chunk for content
                if chunk.choices[0].finish_reason in ["stop", "length"]:
                    if tool_call_buffer:
                        # There were tool calls but no explicit tool_calls finish reason
                        for index in sorted(tool_call_buffer.keys()):
                            yield {"type": "tool_call", "tool_call": tool_call_buffer[index]}
                        tool_call_buffer = {}

        except RateLimitError as e:
            print(f"\n[Rate limit exceeded. Please wait: {e}]")
            raise
        except APIConnectionError as e:
            print(f"\n[Connection error: {e}]")
            raise
        except APIError as e:
            print(f"\n[API error: {e}]")
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
        Execute web search using MiniMax Search API.

        Args:
            tool_input: Dictionary containing web search parameters

        Returns:
            Formatted search results as string
        """
        import requests
        import json
        from urllib.parse import quote

        try:
            query = tool_input.get("query", "")
            count = min(tool_input.get("count", 10), 10)

            # Try MiniMax search API
            url = f"https://api.minimax.chat/api/search?query={quote(query)}&count={count}"
            headers = {
                "Authorization": f"Bearer {settings.ZHIPUAI_API_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            data = response.json()
            results = data.get("data", [])

            if not results:
                return "No search results found."

            formatted_results = []
            for i, result in enumerate(results, 1):
                title = result.get("title", "No title")
                result_url = result.get("url", "No URL")
                summary = result.get("summary", "No summary")
                formatted_results.append(
                    f"{i}. {title}\n   URL: {result_url}\n   Summary: {summary}\n"
                )

            return "\n".join(formatted_results)

        except requests.exceptions.RequestException as e:
            return f"Web search is currently unavailable: {str(e)}. Please try again later or rephrase your question."
        except json.JSONDecodeError:
            return "Web search is currently unavailable (invalid response). Please try again later."
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