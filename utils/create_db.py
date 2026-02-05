import psycopg

# Изменено: импортируем CONNECT_DB_NO_DBNAME вместо дублирования строки подключения
# Было: строка подключения (host, port, user, password) была скопирована прямо сюда
# Стало: берём готовую строку из config.py — одно место для всех настроек
from config import CONNECT_DB, CONNECT_DB_NO_DBNAME

async def create_db():
    # Изменено: используем CONNECT_DB_NO_DBNAME из config.py
    # Было: connect = f"host=127.0.0.1 port=5432 user=postgres password=1 connect_timeout=10"
    # Стало: connect = CONNECT_DB_NO_DBNAME (берётся из config.py)
    conn = psycopg.connect(CONNECT_DB_NO_DBNAME)
    conn.autocommit = True

    curs = conn.cursor()
    try:
        curs.execute(f"CREATE DATABASE mabl WITH OWNER = postgres ENCODING = 'UTF8'")
    except Exception as exc:
        # Изменено: добавлен print, чтобы видеть ошибку в логах
        # Было: pass (ошибка молча проглатывалась, непонятно что произошло)
        # Стало: печатаем ошибку — обычно это "database already exists", и это нормально
        print(f"Создание БД: {exc}")
    finally:
        curs.close()
        conn.close()

    async with await psycopg.AsyncConnection.connect(CONNECT_DB) as conn:
        async with conn.cursor() as curs:
            await curs.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    phone TEXT,
                    device TEXT,
                    problem TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # Добавлено: создание таблицы comments
            # Было: таблица comments НЕ создавалась, хотя используется в db_request.py
            #       (add_comments, get_comments). Без неё бот падал при работе с комментариями
            # Стало: таблица создаётся автоматически вместе с orders
            await curs.execute(
                """
                CREATE TABLE IF NOT EXISTS comments (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id),
                    comment TEXT,
                    editor VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            await conn.commit()
