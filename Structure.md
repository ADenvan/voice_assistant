# Структура проекта

voice_assistant/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Pydantic Settings
│   │   ├── exceptions.py      # Иерархия ошибок
│   │   ├── protocols.py       # Python Protocol интерфейсы
│   │   └── pipeline.py        # Оркестрация + State Machine
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── input.py           # Microphone (sounddevice)
│   │   ├── output.py          # Speakers (sounddevice)
│   │   ├── vad.py             # VAD (Silero + Energy)
│   │   └── wake_word.py       # Wake word detection
│   ├── stt/
│   │   ├── __init__.py
│   │   └── engine.py          # faster-whisper
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py          # Ollama HTTP client
│   │   └── prompt.py          # System prompt + message builder
│   ├── tts/
│   │   ├── __init__.py
│   │   └── engine.py          # Silero TTS
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── database.py        # SQLite async store
│   │   └── context.py         # History trimming
│   └── cli/
│       ├── __init__.py
│       └── app.py             # Typer CLI
├── data/                      # SQLite DB
├── .env
├── pyproject.toml
├── requirements.txt
└── README.md

# Схема взаимодействия модулей
┌─────────────────────────────────────────────────────────────────────┐
│                         CLI (Typer)                                 │
│                    voice_assistant run                               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ creates
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PipelineFactory                                   │
│              (собирает все компоненты)                               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ injects
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PIPELINE                                      │
│  ┌─────────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌────────┐│
│  │   Mic   │──▶│ VAD │──▶│ STT │──▶│ LLM │──▶│ TTS │──▶│Speaker ││
│  │ (input) │   │     │   │     │   │     │   │     │   │(output) ││
│  └────┬────┘   └─────┘   └─────┘   └─────┘   └─────┘   └────────┘│
│       │                                                           │
│       │    ┌───────────┐   ┌──────────┐   ┌──────────────┐        │
│       └───▶│ Wake Word │   │  Memory  │   │    Config    │        │
│            │ (optional)│   │ (SQLite) │   │  (pydantic)  │        │
│            └───────────┘   └──────────┘   └──────────────┘        │
│                                                                     │
│  State Machine: IDLE → LISTENING → STT → THINKING → SPEAKING      │
└─────────────────────────────────────────────────────────────────────┘