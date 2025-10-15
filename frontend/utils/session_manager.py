"""Session management for conversation history."""
from typing import List, Dict, Optional
import json


class SessionManager:
    """Manage conversation session and memory."""

    def __init__(self, max_turns: int = 20):
        """
        Initialize session manager.

        Args:
            max_turns: Maximum number of conversation turns to keep
        """
        self.max_turns = max_turns
        self.conversation_history: List[Dict[str, str]] = []

    def add_turn(self, user_message: str, assistant_message: str):
        """
        Add a conversation turn.

        Args:
            user_message: User's message
            assistant_message: Assistant's response
        """
        self.conversation_history.append({
            "user": user_message,
            "assistant": assistant_message
        })

        # Keep only last max_turns
        if len(self.conversation_history) > self.max_turns:
            self.conversation_history = self.conversation_history[-self.max_turns:]

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history.

        Returns:
            List of conversation turns
        """
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_context_window(self, num_turns: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get a window of recent conversation turns.

        Args:
            num_turns: Number of recent turns to return (default: all)

        Returns:
            Recent conversation turns
        """
        if num_turns:
            return self.conversation_history[-num_turns:]
        return self.conversation_history

    def export_history(self) -> str:
        """
        Export conversation history as JSON.

        Returns:
            JSON string of conversation history
        """
        return json.dumps(self.conversation_history, indent=2)

    def import_history(self, history_json: str):
        """
        Import conversation history from JSON.

        Args:
            history_json: JSON string of conversation history
        """
        try:
            self.conversation_history = json.loads(history_json)
            if len(self.conversation_history) > self.max_turns:
                self.conversation_history = self.conversation_history[-self.max_turns:]
        except json.JSONDecodeError:
            pass

    def get_stats(self) -> Dict:
        """
        Get session statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_turns": len(self.conversation_history),
            "max_turns": self.max_turns,
            "total_user_messages": len([t for t in self.conversation_history if "user" in t]),
            "total_assistant_messages": len([t for t in self.conversation_history if "assistant" in t])
        }
