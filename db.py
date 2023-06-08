import sqlite3

def connect():
    conn = sqlite3.connect("moderation.db")
    return conn

def create_warnings_table_if_not_exists():
    conn = connect()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            chat_id INTEGER,
            user_id INTEGER,
            warnings INTEGER,
            PRIMARY KEY (chat_id, user_id)
        )
    """)

    conn.commit()
    conn.close()

def create_bans_table_if_not_exists():
    conn = connect()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS bans (
            chat_id INTEGER,
            user_id INTEGER,
            PRIMARY KEY (chat_id, user_id)
        )
    """)

    conn.commit()
    conn.close()

def create_mutes_table_if_not_exists():
    conn = connect()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS mutes (
            chat_id INTEGER,
            user_id INTEGER,
            PRIMARY KEY (chat_id, user_id)
        )
    """)

    conn.commit()
    conn.close()

def init():
    create_warnings_table_if_not_exists()
    create_bans_table_if_not_exists()
    create_mutes_table_if_not_exists()

def add_warning(chat_id, user_id):
    conn = connect()
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO warnings (chat_id, user_id, warnings) VALUES (?, ?, 0)", (chat_id, user_id))
    c.execute("UPDATE warnings SET warnings = warnings + 1 WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))

    conn.commit()
    conn.close()

def get_warnings(chat_id, user_id):
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT warnings FROM warnings WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
    result = c.fetchone()

    conn.close()
    return result[0] if result else 0

def clear_warnings(chat_id, user_id):
    conn = connect()
    c = conn.cursor()

    c.execute("UPDATE warnings SET warnings = 0 WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))

    conn.commit()
    conn.close()

def ban_user(chat_id, user_id):
    conn = connect()
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO bans (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id))
    
    c.execute("DELETE FROM mutes WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))

    conn.commit()
    conn.close()

def unban_user(chat_id, user_id):
    conn = connect()
    c = conn.cursor()

    c.execute("DELETE FROM bans WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))

    conn.commit()
    conn.close()

def is_user_banned(chat_id, user_id):
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT 1 FROM bans WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
    result = c.fetchone()

    conn.close()
    return bool(result)

def mute_user(chat_id, user_id):
    conn = connect()
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO mutes (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id))

    conn.commit()
    conn.close()

def unmute_user(chat_id, user_id):
    conn = connect()
    c = conn.cursor()

    c.execute("DELETE FROM mutes WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))

    conn.commit()
    conn.close()

def is_user_muted(chat_id, user_id):
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT 1 FROM mutes WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
    result = c.fetchone()


    conn.close()
    return bool(result)
