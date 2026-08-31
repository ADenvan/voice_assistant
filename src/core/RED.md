
# Pipeline
Что такое Pipeline?

Pipeline — оркестратор, который связывает все компоненты в единый поток.
┌─────────────────────────────────────────────────────────────────┐
│                        PIPELINE                                  │
│                                                                  │
│  Mic ──▶ VAD ──▶ STT ──▶ LLM ──▶ TTS ──▶ Speaker              │
│   │       │       │       │       │       │                      │
│   └───────┴───────┴───────┴───────┴───────┘                     │
│                                                                  │
│  State: IDLE → LISTENING → STT → THINKING → SPEAKING → IDLE    │
│                                                                  │
│  Memory: сохраняет историю между turn'ами                       │
│  Interrupt: пользователь может прервать в любой момент          │
└─────────────────────────────────────────────────────────────────┘

Ключевые концепции
1. State Machine:
IDLE → LISTENING → PROCESSING_STT → THINKING → SPEAKING → IDLE
  ↑                                                         │
  └─────────────────────────────────────────────────────────┘

2. Три режима активации:
button     → нажал Enter → записал → обработал
wake_word  → сказал "войс ай" → записал команду → обработал
continuous → постоянно слушает → обрабатывает каждую фразу

3. Callback hooks:
pipeline.on_state_change = async def(state): ...  # UI обновляет состояние
pipeline.on_transcription = async def(text): ...  # UI показывает текст
pipeline.on_token = async def(token): ...         # UI показывает streaming

4. Interrupt mechanism:
- Пользователь начинает говорить пока ассистент говорит
audio_out.interrupt()  # останавливает воспроизведение
pipeline.interrupt_event.set()  # сигнализирует pipeline

5. PipelineFactory:
- Создаёт pipeline с нужными компонентами
pipeline = PipelineFactory.create_local(config)