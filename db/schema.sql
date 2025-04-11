CREATE TABLE IF NOT EXISTS volontari (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);