class ContextManager:
    def __init__(self, max_messages: int = 50) -> None:
        self.max_messages = max_messages

    def trim_history(self, messages: list[dict]) -> list[dict]:
        """Обрезать историю до max_messages.

        System prompt (role='system') всегда остаётся первым.
        Остальные сообщения обрезаются с конца (новые остаются).
        """
        if len(messages) <= self.max_messages + 1:
            return messages

        system = messages[0] if messages and messages[0]["role"] == "system" else None
        rest = messages[1:] if system else messages
        trimmed = rest[-self.max_messages:]
        return [system, *trimmed] if system else trimmed

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return len(text) // 3
