import asyncio
import logging
import os

import numpy as np

from src.core.config import Config

logger = logging.getLogger("voice_ai.tts")
# """
# Что такое TTS?
# TTS (Text-to-Speech) — преобразует текст в аудио.
# "Привет, как дела?" → Silero TTS → np.ndarray (48kHz, float32)

# Ключевые концепции
# 1. Silero TTS:
# - Нейросеть от Silero
# - Поддерживает русский язык, несколько голосов
# - Качество хорошее, работает локально

# 2. Голоса (speakers):
# - Для русского: v5_ru
# - Голоса: baya, kseniya, xenia, brian и др.

# 3. Sample Rate:
# - TTS генерирует аудио на 48000 Hz
# - Это отличается от микрофона (16000 Hz)
# - Pipeline должен учитывать разницу

# 4. Конфликт имён src:
# - Наш проект: src/
# - Silero TTS: тоже имеет src/ внутри torch hub

# При импорте from src.silero import silero_tts
# Python может найти НАШ src/ вместо Silero

# Решение: временно убрать наш src из sys.modules и sys.path
# """


class SileroTTSEngine:
    def __init__(self, config: Config) -> None:
        self._language = config.silero_language
        self._speaker = config.silero_speaker
        self._voice = config.silero_voice
        self._sample_rate = config.silero_sample_rate
        self._model = None
        self._symbols = None
        self._apply_tts_fn = None

    def load(self) -> None:
        self._load_model()

    def _load_model(self) -> None:
        if self._model is None:
            import sys
            import torch

            logger.info("Loading Silero TTS model (language=%s)...", self._language)

            hub_dir = torch.hub.get_dir()
            repo_dir = os.path.join(hub_dir, "snakers4_silero-models_master")

            silero_src_dir = os.path.join(repo_dir, "src")


            silero_init = os.path.join(silero_src_dir, "__init__.py") # TODO: Удалить Это может быть лишним, но если работает — оставим
            created_init = False
            if not os.path.exists(silero_init):
                with open(silero_init, "w"):
                    pass
                created_init = True

            saved_src = sys.modules.pop("src", None)
            saved_src_subs = {k: v for k, v in list(sys.modules.items()) if k.startswith("src.")}
            for k in saved_src_subs:
                del sys.modules[k]

            if repo_dir not in sys.path:
                sys.path.insert(0, repo_dir)

            try:
                from src.silero import silero_tts

                result = silero_tts(
                    language=self._language,
                    speaker=self._speaker,
                )
            finally:
                if repo_dir in sys.path:
                    sys.path.remove(repo_dir)
                for k in list(sys.modules):
                    if k == "src" or k.startswith("src."):
                        del sys.modules[k]
                if saved_src is not None:
                    sys.modules["src"] = saved_src
                sys.modules.update(saved_src_subs)
                if created_init:
                    try:
                        os.remove(silero_init)
                    except OSError:
                        pass

            if isinstance(result, tuple) and len(result) == 5:
                self._model, self._symbols, sr, _, self._apply_tts_fn = result
                if self._sample_rate not in (sr, [sr]):
                    logger.info(
                        "TTS sample_rate adjusted: config=%d, model=%s",
                        self._sample_rate,
                        sr,
                    )
            else:
                self._model = result[0] if isinstance(result, (tuple, list)) else result

            logger.info("Silero TTS model loaded")

    def _synthesize_sync(self, text: str) -> np.ndarray | None:
        if not text.strip():
            logger.debug("TTS: skipping empty text")
            return None
        try:
            self._load_model()
            logger.info(
                "TTS: synthesizing text (%d chars): %.80s%s",
                len(text),
                text,
                "..." if len(text) > 80 else "",
            )
            if self._apply_tts_fn is not None:
                logger.info(
                    "TTS: using v5 apply_tts_fn API (voice=%s, sr=%d)",
                    self._voice,
                    self._sample_rate,
                )
                audios = self._apply_tts_fn(
                    [text],
                    self._model,
                    self._sample_rate,
                    self._symbols,
                    "cpu",
                )
                result = np.array(audios[0], dtype=np.float32)
                logger.info(
                    "TTS: v5 synthesis result shape=%s dtype=%s min=%.6f max=%.6f rms=%.6f len=%d",
                    result.shape,
                    result.dtype,
                    float(result.min()),
                    float(result.max()),
                    float(np.sqrt(np.mean(result**2))),
                    len(result),
                )
                if result.max() == 0 and result.min() == 0:
                    logger.warning("TTS: v5 result is all zeros (silence)!")
                return result
            logger.info(
                "TTS: using legacy apply_tts API (speaker=%s, sr=%d)",
                self._voice,
                self._sample_rate,
            )
            audio_tensor = self._model.apply_tts(
                text=text,
                speaker=self._voice,
                sample_rate=self._sample_rate,
            )
            result = audio_tensor.numpy().astype(np.float32)
            logger.info(
                "TTS: legacy synthesis result shape=%s dtype=%s min=%.6f max=%.6f rms=%.6f len=%d",
                result.shape,
                result.dtype,
                float(result.min()),
                float(result.max()),
                float(np.sqrt(np.mean(result**2))),
                len(result),
            )
            if result.max() == 0 and result.min() == 0:
                logger.warning("TTS: legacy result is all zeros (silence)!")
            return result
        except Exception as e:
            logger.error("TTS synthesis failed: %s", e, exc_info=True)
            return None

    async def synthesize(self, text: str) -> np.ndarray | None:
        try:
            result = await asyncio.to_thread(self._synthesize_sync, text)
        except Exception as e:
            logger.error("TTS synthesis error: %s", e)
            return None

        if result is None and text.strip():
            logger.warning("TTS returned None for non-empty text, falling back to text-only mode")
        return result
