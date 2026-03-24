"""Main entry point for le-code terminal AI assistant."""

import os
import sys

# Reconfigure stdout/stderr to use UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from typing import Optional, Dict, Any, List, Iterator

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from ai.client import MiniMaxAIClient
from ai.tools import ALL_TOOLS
from cli.ui import TerminalUI, default_ui
from cli.input_handler import default_input_handler
from memory.memory_manager import ConversationMemory, SessionManager

from tools.file_ops import read_file, write_file, glob_search, grep_search
from tools.shell import execute_command
from tools.code_ops import edit_file, insert_code


class LeCodeApp:
    """Main application class for le-code."""

    def __init__(self):
        """Initialize the application."""
        if not settings.validate():
            sys.exit(1)

        self.ui = default_ui
        self.ai_client = MiniMaxAIClient()
        self.memory = ConversationMemory()
        self.session_manager = SessionManager()

        # Set system prompt
        self.memory.add_message(
            "user",
            "你是一个专业的编程助手，叫做 le-code。"
            "你可以帮助用户进行各种编程任务，包括："
            "1. 回答编程问题"
            "2. 生成、修改和调试代码"
            "3. 读取、写入和编辑文件"
            "4. 执行 shell 命令"
            "5. 搜索网络获取最新信息"
            ""
            "当你调用 web_search 工具后，会返回搜索结果。你必须："
            "- 仔细阅读搜索结果"
            "- 将结果整合到你的回答中"
            "- 不要重复调用相同的工具"
            ""
            "请使用清晰、简洁的语言回答。"
        )

    def run(self) -> None:
        """Run the main application loop."""
        self.ui.show_welcome()

        # Health check
        if not self.ai_client.health_check():
            self.ui.display_error("Failed to connect to MiniMax API. Please check your API key.")
            return

        # Main loop
        while self.ui.is_running():
            try:
                self._process_input()
            except KeyboardInterrupt:
                self.ui.stop()
                break
            except Exception as e:
                self.ui.display_error(f"Unexpected error: {e}")

    def _process_input(self) -> None:
        """Process user input."""
        input_str = self.ui.get_user_input()

        if not input_str:
            return

        # Parse input
        is_command, command, args = default_input_handler.parse_input(input_str)

        # Handle special commands
        if is_command:
            if self.ui.handle_special_command(command, args):
                return

            # Handle commands that need memory access
            self._handle_memory_command(command, args)
            return

        # Regular message - add to memory
        self.memory.add_message("user", args.get("content", input_str))
        self.ui.display_message("user", args.get("content", input_str))

        # Process with AI
        self._process_with_ai()

    def _process_with_ai(self) -> None:
        """Process current conversation with AI with streaming support."""
        try:
            # Get messages for API call
            messages = self.memory.get_messages()

            # Get response (streaming enabled)
            response = self.ai_client.create_message(
                messages=messages,
                tools=ALL_TOOLS,
                stream=True
            )

            # Check if streaming is enabled
            if response.get("stream"):
                # Display waiting animation
                self.ui.display_waiting_animation()

                # Process streaming response
                self._process_streaming_response(response["generator"])
            else:
                # Handle non-streaming response
                if response["tool_calls"]:
                    self._handle_tool_calls(response)

                if response["content"]:
                    self.ui.display_assistant_response(response["content"])
                    self.memory.add_message("assistant", response["content"])

        except Exception as e:
            self.ui.display_error(f"Error communicating with AI: {e}")

    def _process_streaming_response(self, generator) -> None:
        """Process streaming response from AI."""
        try:
            # Collect content for memory
            full_content = []
            thinking_content = []
            tool_calls = []
            is_first_content = True

            # Start streaming - this clears the "thinking" message
            self.ui.start_streaming()

            for event in generator:
                event_type = event.get("type")

                if event_type == "thinking":
                    # Display thinking content with special formatting
                    thinking_text = event.get("content", "")
                    if thinking_text:
                        thinking_content.append(thinking_text)
                        self.ui.display_thinking(thinking_text)

                elif event_type == "status":
                    # Display status messages (e.g., "searching...")
                    status_text = event.get("content", "")
                    if status_text:
                        self.ui.display_status_update(status_text)

                elif event_type == "content":
                    chunk = event.get("content", "")
                    if chunk:
                        full_content.append(chunk)
                        self.ui.display_stream_chunk(chunk)

                elif event_type == "tool_call":
                    tool_call = event.get("tool_call", {})
                    tool_calls.append(tool_call)

            # Complete streaming
            self.ui.end_streaming()

            # Handle tool calls if any
            if tool_calls:
                self.ui.display_info("\n[Executing tools...]")
                for tool_call in tool_calls:
                    tool_name = tool_call.get("name")
                    # Parse arguments from JSON string
                    try:
                        import json
                        tool_input = json.loads(tool_call.get("arguments", "{}"))
                    except:
                        tool_input = {}

                    tool_id = tool_call.get("id")

                    # Display tool call
                    self.ui.display_info(f"Calling tool: {tool_name}({tool_input})")

                    # Execute tool
                    result = self._execute_tool(tool_name, tool_input)

                    # Display result
                    self.ui.display_info(f"Tool result: {result[:200]}...")

                    # Add tool result to conversation
                    tool_result = {
                        "name": tool_name,
                        "input": tool_input,
                        "result": result,
                    }

                    # Send tool result back to AI and get follow-up response
                    self._get_followup_with_tool_result(tool_call, result)

            # Add full content to memory (only if no tool calls were made)
            elif full_content:
                content = "".join(full_content)
                self.memory.add_message("assistant", content)

        except Exception as e:
            self.ui.end_streaming()
            self.ui.display_error(f"Error during streaming: {e}")

    def _handle_tool_calls(self, response: Dict[str, Any]) -> None:
        """
        Handle tool calls from AI response.

        Args:
            response: AI response with tool calls
        """
        tool_calls = response["tool_calls"]

        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_input = tool_call.get("input", {})

            # Execute tool
            result = self._execute_tool(tool_name, tool_input)

            # Display tool result
            tool_result = {
                "name": tool_name,
                "input": tool_input,
                "result": result,
            }
            self.ui.display_assistant_response("", [tool_result])

            # Add tool result to conversation
            self.memory.add_message(
                "assistant",
                f"Executed tool: {tool_name}",
                tool_call=tool_result
            )

            # Get follow-up response from AI
            self._get_followup_response(tool_name, result)

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute a tool.

        Args:
            tool_name: Name of the tool
            tool_input: Tool arguments

        Returns:
            Tool result string
        """
        try:
            if tool_name == "read_file":
                success, result = read_file(tool_input.get("file_path", ""))
                return result if success else f"Error: {result}"

            elif tool_name == "write_file":
                success, result = write_file(
                    tool_input.get("file_path", ""),
                    tool_input.get("content", "")
                )
                return result if success else f"Error: {result}"

            elif tool_name == "glob_search":
                success, result = glob_search(tool_input.get("pattern", ""))
                if success:
                    return f"Found {len(result)} files:\n" + "\n".join(result)
                return f"Error: {result}"

            elif tool_name == "grep_search":
                pattern = tool_input.get("pattern", "")
                file_pattern = tool_input.get("file_pattern")
                success, result = grep_search(pattern, file_pattern)
                if success:
                    return f"Found {len(result)} matches:\n" + "\n".join(result)
                return f"Error: {result}"

            elif tool_name == "execute_command":
                success, result = execute_command(
                    tool_input.get("command", ""),
                    tool_input.get("timeout")
                )
                return result if success else f"Error: {result}"

            elif tool_name == "edit_file":
                success, result = edit_file(
                    tool_input.get("file_path", ""),
                    tool_input.get("old_text", ""),
                    tool_input.get("new_text", "")
                )
                return result if success else f"Error: {result}"

            elif tool_name == "insert_code":
                success, result = insert_code(
                    tool_input.get("file_path", ""),
                    tool_input.get("line_number", 1),
                    tool_input.get("code", "")
                )
                return result if success else f"Error: {result}"

            elif tool_name == "web_search":
                result = self.ai_client._execute_web_search(tool_input)
                return result

            else:
                return f"Unknown tool: {tool_name}"

        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def _get_followup_response(self, tool_name: str, tool_result: str) -> None:
        """
        Get follow-up response from AI after tool execution.

        Args:
            tool_name: Name of tool that was executed
            tool_result: Result of tool execution
        """
        try:
            # Get messages
            messages = self.memory.get_messages()

            # Get follow-up response
            response = self.ai_client.create_message(messages)

            if response["content"]:
                self.ui.display_assistant_response(response["content"])
                self.memory.add_message("assistant", response["content"])

        except Exception as e:
            self.ui.display_error(f"Error getting follow-up: {e}")

    def _get_followup_with_tool_result(self, tool_call: Dict[str, Any], tool_result: str) -> None:
        """
        Send tool result back to AI and get follow-up response.

        Args:
            tool_call: The tool call that was executed
            tool_result: The result of the tool execution
        """
        try:
            messages = self.memory.get_messages()

            # Parse tool arguments
            try:
                import json
                arguments = json.loads(tool_call.get("arguments", "{}"))
            except:
                arguments = {}

            # Add tool result as plain text message (more compatible)
            messages.append({
                "role": "user",
                "content": f"以下是搜索结果，请基于这些信息回答用户的问题：\n\n{tool_result}"
            })

            # Display waiting indicator
            self.ui.display_waiting_animation()

            # Get follow-up response without tools to prevent further tool calls
            response = self.ai_client.create_message(
                messages=messages,
                stream=True
            )

            if response.get("stream"):
                self._process_streaming_response(response["generator"])
            else:
                if response.get("content"):
                    self.ui.display_assistant_response(response["content"])
                    self.memory.add_message("assistant", response["content"])

        except Exception as e:
            self.ui.display_error(f"Error getting follow-up with tool result: {e}")

    def _handle_memory_command(self, command: str, args: Dict[str, Any]) -> None:
        """
        Handle memory-related commands.

        Args:
            command: Command name
            args: Command arguments
        """
        if default_input_handler.is_save_command(command):
            filename = args.get("filename")
            if self.memory.save(filename):
                self.ui.display_success(f"Session saved: {filename or self.memory.session_id}")
            else:
                self.ui.display_error("Failed to save session")

        elif default_input_handler.is_load_command(command):
            session_id = args.get("session_id")
            if not session_id:
                self.ui.display_error("Please specify a session ID: /load <id>")
                return

            loaded_memory = ConversationMemory.load(session_id)
            if loaded_memory:
                self.memory = loaded_memory
                self.ui.display_success(f"Loaded session: {session_id}")
            else:
                self.ui.display_error(f"Session not found: {session_id}")

        elif default_input_handler.is_context_command(command):
            self.ui.display_info(self.memory.get_context())


def main():
    """Main entry point."""
    try:
        app = LeCodeApp()
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
