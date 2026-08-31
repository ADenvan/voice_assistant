import asyncio
import logging

import numpy as np
import sounddevice as sd
from scipy.signal import resample as scipy_resample

from src.core.config import Config

logger = logging.getLogger("voice_ai.audio.output")


class SoundDeviceOutput:
    def __init__(self, config: Config) -> None:
        self._interrupt = False
        self._config = config
        self._output_device = getattr(config, "output_device", None)
        self._log_device_info()

    def _log_device_info(self) -> None:
        try:
            dev_pair = sd.default.device
            default_out = dev_pair[1]
            try:
                default_out = int(default_out)
            except (TypeError, ValueError):
                logger.warning("Could not determine default output device: %r", dev_pair)
                return
            dev = sd.query_devices(default_out)
            logger.info(
                "Default audio output: [%d] %s (sr=%s, ch=%s)",
                default_out,
                dev["name"],
                dev["default_samplerate"],
                dev["max_output_channels"],
            )
            if self._output_device is not None:
                target = sd.query_devices(int(self._output_device))
                logger.info("Configured output device: [%d] %s", int(self._output_device), target["name"])
        except Exception as e:
            logger.warning("Could not query audio output device: %s", e)

    def _get_device(self) -> int | None:
        """Вернуть ID устройства или None для default"""
        if self._output_device is not None:
            return int(self._output_device)
        return None

    async def play(self, audio: np.ndarray, sample_rate: int = 48000) -> None:
        """
        1. Подготовить аудио (clamp, dtype)
        2. Проверить sample_rate устройства
        3. Если отличается → resample
        4. Воспроизвести через sounddevice
        5. Ждать окончания, проверяя interrupt
        """
        self._interrupt = False
        logger.info(
            "AudioOutput.play: dtype=%s shape=%s sr=%d samples=%d duration=%.2fs",
            audio.dtype,
            audio.shape,
            sample_rate,
            len(audio),
            len(audio) / sample_rate,
        )

        # 1. Подготовка
        audio_prepared = self._prepare_audio(audio)
        # 2. Проверить device sample rate
        device = self._get_device()
        play_sr = sample_rate

        if device is not None:
            dev_info = sd.query_devices(device)
            dev_sr = int(dev_info["default_samplerate"])
            if dev_sr != sample_rate:
                logger.info("Resampling %dHz -> %dHz for device [%d]", sample_rate, dev_sr, device)
                audio_prepared = resample_audio(audio_prepared, sample_rate, dev_sr)
                play_sr = dev_sr

        # 3. Воспроизвести
        audio_2d = audio_prepared.reshape(-1, 1) if audio_prepared.ndim == 1 else audio_prepared

        logger.info("Playing %d samples at %dHz on device %s", len(audio_prepared), play_sr, device)

        try:
            sd.play(audio_2d, samplerate=play_sr, device=device, blocking=False)
        except Exception as e:
            logger.error("Playback start error: %s", e, exc_info=True)
            return
        # 4. Ждать с проверкой interrupt
        duration_s = len(audio_prepared) / play_sr
        poll_interval = 0.1
        elapsed = 0.0

        while elapsed < duration_s + 0.5:
            if self._interrupt:
                logger.info("Playback interrupted by user")
                sd.stop()
                return
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        sd.wait()
        logger.info("AudioOutput.play: playback completed")

    def _prepare_audio(self, audio: np.ndarray) -> np.ndarray:
        """Конвертировать в float32 и clamp"""
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        return np.clip(audio, -1.0, 1.0)

    def interrupt(self) -> None:
        """Установить флаг прерывания"""
        self._interrupt = True
        sd.stop()

    async def stop(self) -> None:
        """Остановить воспроизведение"""
        sd.stop()


def resample_audio(audio: np.ndarray, orig_rate: int, target_rate: int) -> np.ndarray:
    if orig_rate == target_rate:
        return audio
    num_samples = int(len(audio) * target_rate / orig_rate)
    return scipy_resample(audio, num_samples).astype(np.float32)
