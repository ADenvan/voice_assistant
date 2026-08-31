
# input
Audio Output — воспроизводит аудио через динамики.
TTS → np.ndarray (48kHz) → resample? → sounddevice.play() → Speakers
Ключевые концепции

1. Sample Rate mismatch:
TTS генерирует: 48000 Hz
Устройство: 44100 Hz или 48000 Hz или другое
→ нужен ресемплинг

2. Прерывание (interrupt):
Пользователь начинает говорить пока ассистент говорит
→ нужно остановить воспроизведение

3. Clamping:
Аудио должно быть в диапазоне [-1.0, 1.0]
Если значения больше → обрезаем (clip)

# vad
Что здесь реализовал

EnergyVAD — быстрый, простой
    vad = EnergyVAD(config)
    vad.is_speech(chunk)  # RMS > threshold → True

SileroVAD — точный, ML
    vad = SileroVAD(config)
    vad.load()  # загрузка модели
    vad.is_speech(chunk)  # нейросеть → вероятность → True/False

# wake_word

Wake Word Detection
Что такое Wake Word?
Wake Word — кодовая фраза для активации ассистента.
Пользователь: "Войс ай!" → Wake Word: True → Ассистент слушает команду
Пользователь: "Как дела?" → Wake Word: False → Игнорируем

Ключевые концепции
1. Принцип работы:
Короткий аудио-фрагмент (2 сек) → faster-whisper → текст
    ↓
Fuzzy match: "войс ай" vs "войс ай" → True
             "войс ай" vs "voice ai" → True (fuzzy)
             "как дела" vs "войс ай" → False
2. Fuzzy matching:
# Точное совпадение
"войс ай" in "войс ай"  # True

# Нечёткое (SequenceMatcher)
ratio("войс ай", "войс айай")  # 0.89 > threshold → True

# По словам
"войс" in "войс как дела"  # True
3. Cooldown:
После срабатывания → пауза 3 секунды
Чтобы не срабатывало повторно от эха
4. State machine в stream_utterances():
AWAITING_WAKE_WORD → слышим "войс ай" → AWAITING_COMMAND
AWAITING_COMMAND → слышим команду → yield → AWAITING_WAKE_WORD