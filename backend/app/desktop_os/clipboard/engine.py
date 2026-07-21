from typing import List, Optional

class DesktopClipboardEngine:
    """Manages system clipboard operations and clipboard history caching."""

    def __init__(self):
        self._history: List[str] = []
        self._current_content: str = ""

    def read_clipboard(self) -> str:
        """Reads content from system clipboard."""
        return self._current_content

    def write_clipboard(self, text: str) -> bool:
        """Writes content to system clipboard and caches history."""
        clean_text = text.strip()
        self._current_content = clean_text
        if not self._history or self._history[-1] != clean_text:
            self._history.append(clean_text)
            if len(self._history) > 50:
                self._history.pop(0)
        return True

    def get_clipboard_history(self) -> List[str]:
        """Retrieves clipboard history."""
        return list(reversed(self._history))

    def search_clipboard(self, query: str) -> List[str]:
        """Searches clipboard history matching query."""
        return [item for item in self._history if query.lower() in item.lower()]
