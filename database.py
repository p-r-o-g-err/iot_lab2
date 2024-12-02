import sqlite3
from config import DB_NAME
from utils import hash_password

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Создаем таблицу пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    
    # Таблица настроек освещения
    c.execute('''CREATE TABLE IF NOT EXISTS light_settings 
                 (id INTEGER PRIMARY KEY, 
                  min_light REAL, 
                  max_light REAL)''')
    
    # Таблица истории показаний
    c.execute('''CREATE TABLE IF NOT EXISTS light_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        light_level REAL,
        light_status TEXT
    )''')
    
    # Очищаем таблицу истории показаний
    c.execute("DELETE FROM light_history")

    # Добавляем тестового пользователя (admin/admin)
    hashed_pwd = hash_password("admin")
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
             ("admin", hashed_pwd))
    
    # Начальные настройки освещения
    c.execute("INSERT OR IGNORE INTO light_settings (min_light, max_light) VALUES (?, ?)",
             (300, 500))
    
    conn.commit()
    conn.close()

def save_light_data(timestamp, light_level):
    """Сохранение данных об освещенности"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''INSERT INTO light_history 
                 (timestamp, light_level) 
                 VALUES (?, ?)''', 
              (timestamp, light_level))
    
    conn.commit()
    conn.close()

def get_light_history():
    """Получение истории показаний"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Получаем последние 30 записей
    c.execute('''SELECT timestamp, light_level
                 FROM light_history 
                 ORDER BY timestamp DESC 
                 LIMIT 30''')
    
    history = [
        {
            'timestamp': row[0], 
            'light_level': row[1]
        } for row in c.fetchall()
    ]
    
    conn.close()
    return list(reversed(history))

def get_light_settings():
    """Получение настроек освещения"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT min_light, max_light FROM light_settings WHERE id = 1")
    settings = c.fetchone()
    conn.close()
    return settings if settings else (300, 500)