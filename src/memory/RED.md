# Memory (SQLite + Context)

- Что такое Memory?
    - Memory — хранит историю диалога между сессиями.

Пользователь: "Привет!"
Ассистент: "Здравствуй!"
    ↓
SQLite: sessions + messages
    ↓
Следующий запрос → get_history() → LLM видит контекст

**Файл**	Назначение
**database.py**	SQLite async — хранение сессий и сообщений
**context.py**	Обрезка истории (чтобы не превысить лимит токков LLM)

## Ключевые концепции
1. aiosqlite:
- async обёртка над sqlite3
- Позволяет читать/писать из async кода без блокировки
2. Схема БД:
```sql
sessions:
  id TEXT PRIMARY KEY
  created_at TEXT

messages:
  id INTEGER PRIMARY KEY AUTOINCREMENT
  session_id TEXT → sessions(id)
  role TEXT ('user' | 'assistant')
  content TEXT
  timestamp TEXT
```

3. WAL mode:
- Write-Ahead Logging — позволяет читать и писать одновременно
- Ускоряет работу, безопаснее для concurrent доступа

4. Context trimming:
- LLM имеет лимит контекста (например, 4096 токенов)
- Если история слишком длинная → обрезаем старые сообщения
- System prompt всегда остаётся первым