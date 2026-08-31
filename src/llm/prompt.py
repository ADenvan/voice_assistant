SYSTEM_PROMPT = (
    "Ты — голосовой ассистент. "
    "Ты разговариваешь с пользователем на русском языке.\n"
    "Правила:\n"
    "- Отвечай кратко и по делу.\n"
    "- Используй простой, разговорный русский язык.\n"
    "- Не используй markdown или форматирование.\n"
    "- Если не знаешь ответ, честно скажи об этом.\n"
)

class PromptBuilder:
    def __init__(self, system_prompt: str = SYSTEM_PROMPT) -> None:
        self.system_prompt = system_prompt

    def build_messages(self, history: list[dict]) -> list[dict]:
        messages: list[dict] = [{"role": "system", "content": self.system_prompt}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        return messages