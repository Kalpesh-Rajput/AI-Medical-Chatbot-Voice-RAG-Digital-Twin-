import sqlite3
import json
import time
import os

DB_PATH = "conversation_logs.db"

def init_db():
    """Create logs table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_query TEXT,
            bot_answer TEXT,
            vitals TEXT,
            sources TEXT,
            cached INTEGER,
            via_voice INTEGER
        )
    """)

    conn.commit()
    conn.close()


def log_conversation(user_query, bot_answer, vitals, sources, cached, via_voice):
    """Insert a log record into SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs (timestamp, user_query, bot_answer, vitals, sources, cached, via_voice)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        time.strftime("%Y-%m-%d %H:%M:%S"),
        user_query,
        bot_answer,
        json.dumps(vitals),
        json.dumps(sources),
        1 if cached else 0,
        1 if via_voice else 0
    ))

    conn.commit()
    conn.close()

# Initialize DB on first import
init_db()
