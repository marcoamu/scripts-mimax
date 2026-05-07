-- Chat Channels System
CREATE TABLE IF NOT EXISTS chat_channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES chat_channels(id) ON DELETE CASCADE,
    user_alias VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_users (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES chat_channels(id) ON DELETE CASCADE,
    user_alias VARCHAR(100) NOT NULL,
    ip_address VARCHAR(50),
    joined_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    UNIQUE(channel_id, user_alias)
);