# database.py
import sqlite3
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("bot.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_tables()
    
    def init_tables(self):
        # 1. Welcome settings
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS welcome (
                chat_id INTEGER PRIMARY KEY,
                video_id TEXT,
                text TEXT
            )
        """)
        
        # 2. Rules
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                chat_id INTEGER PRIMARY KEY,
                rule_text TEXT
            )
        """)
        
        # 3. Teach system
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS teaches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                chat_id INTEGER
            )
        """)
        
        # 4. Warnings (spam)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                chat_id INTEGER,
                user_id INTEGER,
                count INTEGER DEFAULT 0,
                mute_until TIMESTAMP,
                PRIMARY KEY (chat_id, user_id)
            )
        """)
        
        # 5. Call settings
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS call_settings (
                chat_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT '🇲🇲',
                call_count INTEGER DEFAULT 5,
                who_can_call TEXT DEFAULT 'all',
                use_emoji INTEGER DEFAULT 1
            )
        """)
        
        # 6. Banned users
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS banned (
                chat_id INTEGER,
                user_id INTEGER,
                banned_at TIMESTAMP,
                PRIMARY KEY (chat_id, user_id)
            )
        """)
        
        # 7. Broadcast groups
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS broadcast_groups (
                group_id INTEGER PRIMARY KEY,
                group_name TEXT,
                group_link TEXT,
                added_at TIMESTAMP
            )
        """)
        
        # 8. Broadcast private chats
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS broadcast_private (
                user_id INTEGER PRIMARY KEY,
                chat_id INTEGER,
                added_at TIMESTAMP
            )
        """)
        
        # 9. Broadcast codes
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS broadcast_codes (
                code TEXT PRIMARY KEY,
                owner_id INTEGER,
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                used_by INTEGER,
                used_at TIMESTAMP,
                is_used INTEGER DEFAULT 0,
                message_text TEXT,
                message_type TEXT
            )
        """)
        
        # 10. Registered Bots (Bot Manager)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS registered_bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_token TEXT UNIQUE,
                bot_name TEXT,
                bot_username TEXT,
                bot_id INTEGER,
                added_by INTEGER,
                added_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                last_checked TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    # ===== WELCOME =====
    def set_welcome(self, chat_id, video_id, text=""):
        self.cursor.execute(
            "INSERT OR REPLACE INTO welcome (chat_id, video_id, text) VALUES (?, ?, ?)",
            (chat_id, video_id, text)
        )
        self.conn.commit()
    
    def get_welcome(self, chat_id):
        self.cursor.execute("SELECT video_id, text FROM welcome WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        return {"video_id": result[0], "text": result[1]} if result else None
    
    def delete_welcome(self, chat_id):
        self.cursor.execute("DELETE FROM welcome WHERE chat_id = ?", (chat_id,))
        self.conn.commit()
    
    def set_welcome_text(self, chat_id, text):
        welcome = self.get_welcome(chat_id)
        if welcome:
            self.cursor.execute(
                "UPDATE welcome SET text = ? WHERE chat_id = ?",
                (text, chat_id)
            )
        else:
            self.cursor.execute(
                "INSERT INTO welcome (chat_id, text) VALUES (?, ?)",
                (chat_id, text)
            )
        self.conn.commit()
    
    # ===== RULES =====
    def set_rule(self, chat_id, rule_text):
        self.cursor.execute(
            "INSERT OR REPLACE INTO rules (chat_id, rule_text) VALUES (?, ?)",
            (chat_id, rule_text)
        )
        self.conn.commit()
    
    def get_rule(self, chat_id):
        self.cursor.execute("SELECT rule_text FROM rules WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def delete_rule(self, chat_id):
        self.cursor.execute("DELETE FROM rules WHERE chat_id = ?", (chat_id,))
        self.conn.commit()
    
    # ===== TEACH =====
    def save_teach(self, question, answer, chat_id):
        self.cursor.execute(
            "INSERT INTO teaches (question, answer, chat_id) VALUES (?, ?, ?)",
            (question, answer, chat_id)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_teach(self, question, chat_id):
        self.cursor.execute(
            "SELECT answer FROM teaches WHERE question = ? AND chat_id = ? LIMIT 1",
            (question, chat_id)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    # ===== WARNINGS =====
    def get_warning_count(self, chat_id, user_id):
        self.cursor.execute(
            "SELECT count, mute_until FROM warnings WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id)
        )
        result = self.cursor.fetchone()
        if result:
            return {"count": result[0], "mute_until": result[1]}
        return {"count": 0, "mute_until": None}
    
    def increment_warning(self, chat_id, user_id):
        current = self.get_warning_count(chat_id, user_id)
        new_count = current['count'] + 1
        mute_until = None
        
        if new_count >= 3:
            mute_until = (datetime.now() + timedelta(minutes=3)).isoformat()
        
        self.cursor.execute(
            "INSERT OR REPLACE INTO warnings (chat_id, user_id, count, mute_until) VALUES (?, ?, ?, ?)",
            (chat_id, user_id, new_count, mute_until)
        )
        self.conn.commit()
        return {"count": new_count, "mute_until": mute_until}
    
    def reset_warning(self, chat_id, user_id):
        self.cursor.execute(
            "DELETE FROM warnings WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id)
        )
        self.conn.commit()
    
    def is_muted(self, chat_id, user_id):
        warning = self.get_warning_count(chat_id, user_id)
        if warning['mute_until']:
            mute_until = datetime.fromisoformat(warning['mute_until'])
            if datetime.now() < mute_until:
                return True, mute_until
            else:
                self.reset_warning(chat_id, user_id)
        return False, None
    
    # ===== CALL SETTINGS =====
    def get_call_settings(self, chat_id):
        self.cursor.execute(
            "SELECT language, call_count, who_can_call, use_emoji FROM call_settings WHERE chat_id = ?",
            (chat_id,)
        )
        result = self.cursor.fetchone()
        if result:
            return {
                "language": result[0],
                "call_count": result[1],
                "who_can_call": result[2],
                "use_emoji": bool(result[3])
            }
        return {"language": "🇲🇲", "call_count": 5, "who_can_call": "all", "use_emoji": True}
    
    def update_call_settings(self, chat_id, setting, value):
        settings = self.get_call_settings(chat_id)
        settings[setting] = value
        self.cursor.execute(
            "INSERT OR REPLACE INTO call_settings (chat_id, language, call_count, who_can_call, use_emoji) VALUES (?, ?, ?, ?, ?)",
            (chat_id, settings['language'], settings['call_count'], settings['who_can_call'], int(settings['use_emoji']))
        )
        self.conn.commit()
    
    # ===== BAN =====
    def ban_user(self, chat_id, user_id):
        self.cursor.execute(
            "INSERT OR REPLACE INTO banned (chat_id, user_id, banned_at) VALUES (?, ?, ?)",
            (chat_id, user_id, datetime.now().isoformat())
        )
        self.conn.commit()
    
    def is_banned(self, chat_id, user_id):
        self.cursor.execute(
            "SELECT banned_at FROM banned WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id)
        )
        return self.cursor.fetchone() is not None
    
    def unban_user(self, chat_id, user_id):
        self.cursor.execute(
            "DELETE FROM banned WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id)
        )
        self.conn.commit()
    
    # ===== BROADCAST GROUPS =====
    def add_broadcast_group(self, group_id, group_name="", group_link=""):
        self.cursor.execute(
            "INSERT OR REPLACE INTO broadcast_groups (group_id, group_name, group_link, added_at) VALUES (?, ?, ?, ?)",
            (group_id, group_name, group_link, datetime.now().isoformat())
        )
        self.conn.commit()
    
    def remove_broadcast_group(self, group_id):
        self.cursor.execute("DELETE FROM broadcast_groups WHERE group_id = ?", (group_id,))
        self.conn.commit()
    
    def get_broadcast_groups(self):
        self.cursor.execute("SELECT group_id, group_name, group_link FROM broadcast_groups")
        return self.cursor.fetchall()
    
    def get_broadcast_groups_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM broadcast_groups")
        return self.cursor.fetchone()[0]
    
    # ===== BROADCAST PRIVATE =====
    def add_broadcast_private(self, user_id, chat_id):
        self.cursor.execute(
            "INSERT OR REPLACE INTO broadcast_private (user_id, chat_id, added_at) VALUES (?, ?, ?)",
            (user_id, chat_id, datetime.now().isoformat())
        )
        self.conn.commit()
    
    def get_broadcast_private(self):
        self.cursor.execute("SELECT user_id, chat_id FROM broadcast_private")
        return self.cursor.fetchall()
    
    # ===== BROADCAST CODES =====
    def save_broadcast_code(self, code, owner_id, expires_at):
        self.cursor.execute(
            "INSERT INTO broadcast_codes (code, owner_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (code, owner_id, datetime.now().isoformat(), expires_at.isoformat())
        )
        self.conn.commit()
    
    def get_broadcast_code(self, code):
        self.cursor.execute(
            "SELECT * FROM broadcast_codes WHERE code = ?",
            (code,)
        )
        return self.cursor.fetchone()
    
    def use_broadcast_code(self, code, user_id, message_text):
        self.cursor.execute(
            "UPDATE broadcast_codes SET used_by = ?, used_at = ?, is_used = 1, message_text = ? WHERE code = ?",
            (user_id, datetime.now().isoformat(), message_text, code)
        )
        self.conn.commit()
    
    def get_all_broadcast_codes(self, limit=50):
        self.cursor.execute(
            "SELECT code, owner_id, created_at, expires_at, used_by, used_at, is_used, message_text FROM broadcast_codes ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return self.cursor.fetchall()
    
    # ===== BOT MANAGER =====
    def register_bot(self, token, bot_name, bot_username, bot_id, added_by):
        self.cursor.execute(
            "INSERT OR REPLACE INTO registered_bots (bot_token, bot_name, bot_username, bot_id, added_by, added_at, is_active) VALUES (?, ?, ?, ?, ?, ?, 1)",
            (token, bot_name, bot_username, bot_id, added_by, datetime.now().isoformat())
        )
        self.conn.commit()
        return True
    
    def get_all_registered_bots(self):
        self.cursor.execute("SELECT bot_token, bot_name, bot_username, bot_id, added_by, added_at, is_active FROM registered_bots ORDER BY added_at DESC")
        return self.cursor.fetchall()
    
    def get_active_bots(self):
        self.cursor.execute("SELECT bot_token, bot_name, bot_username, bot_id FROM registered_bots WHERE is_active = 1")
        return self.cursor.fetchall()
    
    def update_bot_status(self, token, is_active):
        self.cursor.execute(
            "UPDATE registered_bots SET is_active = ?, last_checked = ? WHERE bot_token = ?",
            (is_active, datetime.now().isoformat(), token)
        )
        self.conn.commit()
    
    def remove_bot(self, token):
        self.cursor.execute("DELETE FROM registered_bots WHERE bot_token = ?", (token,))
        self.conn.commit()
    
    def close(self):
        self.conn.close()
