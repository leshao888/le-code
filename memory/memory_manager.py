"""Memory management for conversation history."""

import json
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from config.settings import settings


class ConversationMemory:
    """Manage conversation history and context."""

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize conversation memory.

        Args:
            session_id: Optional session identifier
        """
        self.session_id = session_id or self._generate_session_id()
        self.messages: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "session_id": self.session_id,
        }

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = str(int(time.time()))
        hash_input = f"{timestamp}-{os.urandom(4).hex()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def add_message(self, role: str, content: str, **kwargs) -> None:
        """
        Add a message to the conversation.

        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            **kwargs: Additional metadata
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        message.update(kwargs)

        self.messages.append(message)
        self.metadata["last_updated"] = datetime.now().isoformat()
        self._auto_compress()

    def get_messages(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Get messages for API call.

        Args:
            include_system: Whether to include system messages

        Returns:
            List of message dictionaries
        """
        messages = []

        for msg in self.messages:
            if not include_system and msg["role"] == "system":
                continue
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        return messages

    def get_recent_messages(self, count: int = 10) -> List[Dict[str, str]]:
        """
        Get the most recent N messages.

        Args:
            count: Number of recent messages

        Returns:
            List of recent message dictionaries
        """
        recent = self.messages[-count:] if count else self.messages
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in recent
        ]

    def clear(self) -> None:
        """Clear all messages except system messages."""
        system_messages = [msg for msg in self.messages if msg["role"] == "system"]
        self.messages = system_messages
        self.metadata["last_updated"] = datetime.now().isoformat()

    def get_context(self) -> str:
        """
        Get a summary of the conversation context.

        Returns:
            Context summary string
        """
        if not self.messages:
            return "No conversation history."

        user_msgs = [m for m in self.messages if m["role"] == "user"]
        assistant_msgs = [m for m in self.messages if m["role"] == "assistant"]

        return (
            f"Conversation has {len(user_msgs)} user messages and "
            f"{len(assistant_msgs)} assistant responses. "
            f"Last update: {self.metadata['last_updated']}"
        )

    def save(self, filename: Optional[str] = None) -> bool:
        """
        Save conversation to file.

        Args:
            filename: Optional filename (defaults to session_id.json)

        Returns:
            True if successful
        """
        try:
            if filename is None:
                filename = f"{self.session_id}.json"

            filepath = settings.MEMORY_DIR / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "metadata": self.metadata,
                "messages": self.messages,
            }

            filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))
            return True

        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False

    @classmethod
    def load(cls, filename: str) -> Optional['ConversationMemory']:
        """
        Load conversation from file.

        Args:
            filename: Filename to load

        Returns:
            ConversationMemory instance or None if failed
        """
        try:
            filepath = settings.MEMORY_DIR / filename

            if not filepath.exists():
                return None

            data = json.loads(filepath.read_text(encoding='utf-8'))

            memory = cls()
            memory.metadata = data.get("metadata", {})
            memory.messages = data.get("messages", [])
            memory.session_id = memory.metadata.get("session_id", memory.session_id)

            return memory

        except Exception as e:
            print(f"Error loading conversation: {e}")
            return None

    def _auto_compress(self) -> None:
        """Automatically compress long conversations."""
        # Compress if we have too many messages
        MAX_MESSAGES = 50

        if len(self.messages) <= MAX_MESSAGES:
            return

        # Keep system messages and recent messages
        system_msgs = [m for m in self.messages if m["role"] == "system"]
        recent_msgs = self.messages[-MAX_MESSAGES:]

        self.messages = system_msgs + recent_msgs

        print(f"[Compressed conversation from {len(self.messages)} to {MAX_MESSAGES} messages]")

    def get_token_count(self) -> int:
        """
        Estimate token count of conversation.

        Returns:
            Estimated token count
        """
        total_chars = sum(len(msg.get("content", "")) for msg in self.messages)
        # Rough estimate: 4 chars per token
        return total_chars // 4

    def get_file_references(self) -> List[str]:
        """
        Extract file references from conversation.

        Returns:
            List of file paths mentioned
        """
        import re

        file_pattern = r'[\w\-./]+\.(?:py|js|ts|java|c|cpp|h|go|rs|rb|json|yaml|yml|md|txt|html|css)'
        files = set()

        for msg in self.messages:
            matches = re.findall(file_pattern, msg.get("content", ""))
            files.update(matches)

        return sorted(files)


class SessionManager:
    """Manage multiple conversation sessions."""

    def __init__(self):
        """Initialize session manager."""
        self.sessions_dir = settings.SESSIONS_DIR
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def list_sessions(self) -> List[str]:
        """
        List all available sessions.

        Returns:
            List of session IDs
        """
        try:
            sessions = []

            for file in self.sessions_dir.glob("*.json"):
                try:
                    data = json.loads(file.read_text(encoding='utf-8'))
                    sessions.append({
                        "id": file.stem,
                        "created": data.get("metadata", {}).get("created_at"),
                        "updated": data.get("metadata", {}).get("last_updated"),
                    })
                except:
                    pass

            return sorted(sessions, key=lambda x: x.get("updated", ""), reverse=True)

        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if successful
        """
        try:
            filepath = self.sessions_dir / f"{session_id}.json"

            if not filepath.exists():
                return False

            filepath.unlink()
            return True

        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.

        Args:
            session_id: Session ID

        Returns:
            Session info dictionary or None
        """
        try:
            filepath = self.sessions_dir / f"{session_id}.json"

            if not filepath.exists():
                return None

            data = json.loads(filepath.read_text(encoding='utf-8'))

            return {
                "id": session_id,
                "created": data.get("metadata", {}).get("created_at"),
                "updated": data.get("metadata", {}).get("last_updated"),
                "message_count": len(data.get("messages", [])),
            }

        except Exception:
            return None


# Import os for _generate_session_id
import os
