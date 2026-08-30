# voice assistant — Local Russian Voice Assistant

Full pipeline: **Microphone → VAD → STT → LLM → TTS → Speakers**

## Architecture

```
Mic (16kHz) → [Silero VAD] → [faster-whisper STT] → Text
  → [Ollama LLM, streaming] → Response
  → [Silero TTS v5] → Audio → [sounddevice] → Speakers
```

| Component | Technology | Model |
|-----------|-----------|--------|
| VAD | Silero | silero-vad (512 windows) |
| STT | faster-whisper | large-v3, CUDA |
| LLM | Ollama | qwen2.5:7b |
| TTS | Silero | v5_ru, voice=baya, 48kHz |
| Memory | SQLite (aiosqlite) | — |

