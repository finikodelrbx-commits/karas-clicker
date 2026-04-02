from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

DB_NAME = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (username TEXT PRIMARY KEY, password TEXT, game_data TEXT)''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", 
                       (data['username'], data['password'], data['game_data']))
        conn.commit()
        return jsonify({"status": "ok"})
    except:
        return jsonify({"status": "error", "message": "Ник уже занят!"}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                          (data['username'], data['password'])).fetchone()
    conn.close()
    if user:
        return jsonify({"status": "ok", "game_data": user[2]})
    return jsonify({"status": "error", "message": "Неверный логин или пароль"}), 401

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET game_data = ? WHERE username = ?", 
                   (data['game_data'], data['username']))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@socketio.on('send_msg')
def handle_message(data):
    emit('receive_msg', {'u': data['u'], 't': data['t']}, broadcast=True)

if __name__ == '__main__':
    init_db()
    print(">>> СЕРВЕР KARAS CLICKER ЗАПУЩЕН НА ПОРТУ 5000")
    socketio.run(app, port=5000)