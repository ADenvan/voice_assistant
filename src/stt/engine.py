import asyncio
import logging

import numpy as np

from src.core.config import Config
from src.core.exceptions import EmptyTranscriptionError, STTError

logger = logging.getLogger("voice_ai.stt")
"""
Что такое STT?
STT (Speech-to-Text) — преобразует аудио в текст.
np.ndarray (аудио, 16kHz) → faster-whisper → "Привет, как дела?"

Ключевые концепции
1. faster-whisper:
- Это оптимизированная реализация Whisper от OpenAI
- Использует CTranslate2 вместо PyTorch
- Быстрее и легче, но требует отдельной установки

2. Модели Whisper:
- tiny    → самый быстрый, низкое качество
- base    → баланс (для учебного проекта)
- small   → лучше
- medium  → ещё лучше
- large   → лучшее качество, медленный
- large-v3 → последняя версия

3. Lazy loading:
- Модель загружается при первом вызове, не при создании объекта
- Экономит память и время запуска

4. Async wrapper:
- faster-whisper синхронный → оборачиваем в asyncio.to_thread
- Чтобы не блокировать event loop
"""


class FasterWhisperEngine:
    def __init__(self, config: Config) -> None:
        self._model_name = config.whisper_model
        self._device = config.whisper_device
        self._compute_type = config.whisper_compute_type
        self._model = None

    def load(self) -> None:
        """Публичный метод для предзагрузки модели"""
        self._load_model()

    def _load_model(self) -> None:
        if self._model is None:
            from faster_whisper import WhisperModel

            logger.info(
                "Loading Whisper model: %s (device=%s, compute_type=%s)",
                self._model_name,
                self._device,
                self._compute_type,
            )
            self._model = WhisperModel(
                self._model_name,
                device=self._device,
                compute_type=self._compute_type,
            )
            logger.info("Whisper model loaded")

    def _transcribe_sync(self, audio: np.ndarray) -> str:
        """Синхронная транскрипция (вызывается в потоке)"""
        self._load_model()
        if len(audio) == 0:
            return ""
        segments, _ = self._model.transcribe(audio, language="ru")
        text = " ".join(s.text for s in segments).strip()
        return text

    async def transcribe(self, audio: np.ndarray) -> str:
        """Async интерфейс для pipeline"""
        try:
            text = await asyncio.to_thread(self._transcribe_sync, audio)
        except Exception as e:
            raise STTError(f"Transcription failed: {e}") from e

        if not text:
            raise EmptyTranscriptionError("STT returned empty result")

        logger.info("Transcribed: %s (%d chars)", text[:50], len(text))
        return text
