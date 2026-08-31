class VoiceAIError(Exception):
    """Базовое исключение для всех ошибок voice_ai."""


class AudioError(VoiceAIError):
    """Ошибки захвата/воспроизведения звука."""


class DeviceNotFoundError(AudioError):
    """Аудиоустройство недоступно."""


class STTError(VoiceAIError):
    """Ошибки преобразования речи в текст."""


class EmptyTranscriptionError(STTError):
    """STT вернул пустой результат."""


class LLMError(VoiceAIError):
    """Ошибки подключения или генерации LLM."""


class LLMConnectionError(LLMError):
    """Не удаётся подключиться к серверу Ollama."""


class LLMTimeoutError(LLMError):
    """Истекло время генерации LLM."""


class TTSError(VoiceAIError):
    """Ошибки преобразования текста в речь."""


class WakeWordError(VoiceAIError):
    """Ошибки обнаружения ключевого слова пробуждения."""


class MemoryError(VoiceAIError):
    """Ошибки базы данных/хранилища."""

