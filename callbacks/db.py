# db.py
import pymysql
from pymysql.cursors import DictCursor
import threading

# Конфигурация подключения
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "KAgdeckeywukMe0",
    "database": "analizeprog",
    "port": 3306,
    "cursorclass": DictCursor,
    "autocommit": True,
    "charset": "utf8mb4"
}

# 🔒 Потокобезопасный singleton
_connection_lock = threading.Lock()
_pool = None

def get_connection():
    global _pool
    with _connection_lock:
        try:
            if _pool is None:
                _pool = pymysql.connect(**db_config)
            return _pool
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
