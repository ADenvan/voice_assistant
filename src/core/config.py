from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    sample_rate: int = 16000
    chunk_duration_ms: int = 500 # размер чанка для VAD
    vad_threshold: float = 0.5 # порог VAD
    output_device: int | None = None  # None = default device

    whisper_model: str = "base" # модель Whisper
    whisper_device: str = "cpu" # device для Whisper
    whisper_compute_type: str = "int8" # тип вычислений

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    ollama_timeout: int = 60
    ollama_temperature: float = 0.7
    ollama_num_ctx: int = 4096
    ollama_num_predict: int = 256

    silero_language: str = "ru" # 
    silero_speaker: str = "v5_ru" # Это
    silero_voice: str = "baya"
    silero_sample_rate: int = 48000

    activation_mode: str = "button" # button/wake_word/continuous
    wake_word_phrases: list[str] = ["войс ай", "voice ai"]
    wake_word_threshold: float = 0.7
    wake_word_cooldown_s: float = 3.0

    db_path: str = "data/voice_assistant.db"
    history_limit: int = 50

    log_level: str = "INFO"