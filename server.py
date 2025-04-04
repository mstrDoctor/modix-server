from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import psycopg2
import psycopg2.extras

app = Flask(__name__)
CORS(app)

# Получаем строку подключения из переменной среды
DATABASE_URL = os.environ.get('DATABASE_URL')

# Создаём соединение с PostgreSQL
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Инициализация таблиц
def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            file_id TEXT,
            name TEXT,
            text TEXT,
            timestamp BIGINT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            file_id TEXT PRIMARY KEY,
            likes INTEGER DEFAULT 0,
            downloads INTEGER DEFAULT 0
        );
    """)
    conn.commit()

init_db()

# === Роуты ===

@app.route('/comments/<file_id>', methods=['GET', 'POST'])
def comments(file_id):
    if request.method == 'GET':
        cursor.execute("SELECT name, text, timestamp FROM comments WHERE file_id = %s", (file_id,))
        comments = cursor.fetchall()
        return jsonify([dict(c) for c in comments])
    else:
        data = request.json
        cursor.execute("""
            INSERT INTO comments (file_id, name, text, timestamp)
            VALUES (%s, %s, %s, extract(epoch from now()) * 1000)
        """, (file_id, data.get("name", "Аноним"), data.get("text", "")))
        conn.commit()
        return jsonify({"status": "ok"})

@app.route('/like/<file_id>', methods=['POST'])
def like(file_id):
    cursor.execute("""
        INSERT INTO stats (file_id, likes, downloads)
        VALUES (%s, 1, 0)
        ON CONFLICT (file_id) DO UPDATE SET likes = stats.likes + 1
    """, (file_id,))
    conn.commit()

    cursor.execute("SELECT likes FROM stats WHERE file_id = %s", (file_id,))
    likes = cursor.fetchone()["likes"]
    return jsonify({"likes": likes})

@app.route('/stats/<file_id>', methods=['GET'])
def get_stats(file_id):
    cursor.execute("SELECT likes, downloads FROM stats WHERE file_id = %s", (file_id,))
    row = cursor.fetchone()
    if row:
        return jsonify(dict(row))
    else:
        return jsonify({"likes": 0, "downloads": 0})

@app.route('/files/<file_id>', methods=['GET'])
def download(file_id):
    cursor.execute("""
        INSERT INTO stats (file_id, likes, downloads)
        VALUES (%s, 0, 1)
        ON CONFLICT (file_id) DO UPDATE SET downloads = stats.downloads + 1
    """, (file_id,))
    conn.commit()
    return jsonify({"status": "ok"})

# Запуск
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
