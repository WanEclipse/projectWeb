from flask import Flask, request, jsonify, render_template, make_response
import sqlite3
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('cafe.db')
    c = conn.cursor()

    # Таблица с напитками (Web-флаг)
    c.execute('''CREATE TABLE IF NOT EXISTS drinks
                 (id INTEGER PRIMARY KEY, name TEXT, price REAL, secret_note TEXT)''')
    c.execute("DELETE FROM drinks")
    drinks = [
        (1, 'Эспрессо', 150, 'обычный кофе'),
        (2, 'Капучино', 200, 'с пенкой'),
        (3, 'Латте', 220, 'молочный'),
        (4, 'Босс-кофе', 999, 'RDGCTF{two_mAn}')   # ← WEB-ФЛАГ
    ]
    c.executemany('INSERT INTO drinks VALUES (?,?,?,?)', drinks)

    # Отдельная таблица для Joy-флага
    c.execute('''CREATE TABLE IF NOT EXISTS game_flag
                 (id INTEGER PRIMARY KEY, flag TEXT)''')
    c.execute("DELETE FROM game_flag")
    c.execute("INSERT INTO game_flag (flag) VALUES (?)", ('RDGCTF{yelloW}',))   # ← JOY-ФЛАГ

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/order')
def order():
    search = request.args.get('search', '')
    conn = sqlite3.connect('cafe.db')
    c = conn.cursor()
    # УЯЗВИМЫЙ ЗАПРОС – SQL‑ИНЪЕКЦИЯ
    query = f"SELECT name, price FROM drinks WHERE name LIKE '%{search}%'"
    try:
        c.execute(query)
        results = c.fetchall()
        conn.close()
        # Скрываем "Босс-кофе" из обычного вывода на странице
        filtered = [{'name': r[0], 'price': r[1]} for r in results if r[0] != 'Босс-кофе']
        return jsonify(filtered)
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Что-то пошло не так...'}), 500

@app.route('/admin')
def admin():
    if request.cookies.get('admin') == '1':
        conn = sqlite3.connect('cafe.db')
        c = conn.cursor()
        c.execute("SELECT secret_note FROM drinks WHERE name='Босс-кофе'")
        flag = c.fetchone()[0]
        conn.close()
        return f"<h1>Секретный напиток (Web): {flag}</h1>"
    else:
        return "<h1>Доступ запрещён</h1>", 403

@app.route('/play')
def play():
    return render_template('game.html')

@app.route('/flag')
def get_flag():
    # Если админ – отдаём Web-флаг
    if request.cookies.get('admin') == '1':
        conn = sqlite3.connect('cafe.db')
        c = conn.cursor()
        c.execute("SELECT secret_note FROM drinks WHERE name='Босс-кофе'")
        flag = c.fetchone()[0]
        conn.close()
        return jsonify({'flag': flag, 'category': 'web'})

    # Если выиграна игра – отдаём Joy-флаг
    if request.cookies.get('game_won') == '1':
        conn = sqlite3.connect('cafe.db')
        c = conn.cursor()
        c.execute("SELECT flag FROM game_flag WHERE id=1")
        flag = c.fetchone()[0]
        conn.close()
        return jsonify({'flag': flag, 'category': 'joy'})

    return jsonify({'error': 'Недостаточно прав'}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
