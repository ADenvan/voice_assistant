import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, TypedDict, runtime_checkable

import numpy as np

# """
# protocols.py — что это и зачем?
# Protocol — это интерфейс в Python (structural typing). Он описывает контракт: какие методы должен иметь объект, без наследования."""

class PipelineState(Enum):
    IDLE = auto()
    LISTENING = auto()
    PROCESSING_STT = auto()
    THINKING = auto()
    SPEAKING = auto()


@dataclass
class TurnResult:
    user_text: str
    assistant_text: str
    latency_ms: int
    interrupted: bool = False


class Message(TypedDict):
    role: str
    content: str
    timestamp: str


@dataclass
class SessionInfo:
    session_id: str
    created_at: str
    turn_count: int = 0


@runtime_checkable
class AudioInput(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def read_chunk(self) -> np.ndarray: ...


@runtime_checkable
class LocalAudioInput(AudioInput, Protocol):
    async def record_utterance(
        self,
        vad: object | None = None,
        max_duration_s: float = 10.0,
        silence_timeout_s: float = 1.5,
    ) -> np.ndarray: ...

    async def stream_utterances(
        self,
        vad: object,
        wake_word: object | None = None,
    ) -> AsyncIterator[np.ndarray]: ...

@runtime_checkable
class AudioOutput(Protocol):
    async def play(self, audio: np.ndarray, sample_rate: int) -> None: ...
    def interrupt(self) -> None: ...
    async def stop(self) -> None: ...

@runtime_checkable
class VAD(Protocol):
    def is_speech(self, chunk: np.ndarray) -> bool: ...
    def get_speech_prob(self, chunk: np.ndarray) -> float: ...

@runtime_checkable
class STTEngine(Protocol):
    async def transcribe(self, audio: np.ndarray) -> str: ...

@runtime_checkable
class LLMClient(Protocol):
    async def chat_stream(self, messages: list[dict]) -> AsyncIterator[str]: ...
    async def chat(self, messages: list[dict]) -> str: ...

@runtime_checkable
class TTSEngine(Protocol):
    async def synthesize(self, text: str) -> np.ndarray | None: ...


@runtime_checkable
class WakeWordDetector(Protocol):
    def load(self) -> None: ...
    async def detect(self, audio: np.ndarray) -> bool: ...


@runtime_checkable
class MemoryStore(Protocol):
    async def create_session(self) -> str: ...
    async def save_message(self, session_id: str, role: str, content: str) -> None: ...
    async def get_history(self, session_id: str, limit: int) -> list[dict]: ...
    async def delete_session(self, session_id: str) -> None: ...
    async def list_sessions(self) -> list[SessionInfo]: ...
    async def session_exists(self, session_id: str) -> bool: ...
