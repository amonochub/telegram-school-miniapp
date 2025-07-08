import sqlite3
from typing import Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "school_kapotnya.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id BIGINT UNIQUE,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                role TEXT DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, user))
        return None
    
    def register_user(self, telegram_id: int, username: str, first_name: str, last_name: str, role: str = 'student'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT OR REPLACE INTO users (telegram_id, username, first_name, last_name, role) VALUES (?, ?, ?, ?, ?)',
            (telegram_id, username, first_name, last_name, role)
        )
        
        conn.commit()
        conn.close()
