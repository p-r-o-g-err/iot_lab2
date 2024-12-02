from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3
from config import *
from database import init_db, get_light_history, get_light_settings
from utils import verify_password

app = Flask(__name__)
app.secret_key = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Проверяем наличие специального флага формы
        if request.form.get('login_attempt') == 'true':
            username = request.form['username']
            password = request.form['password']
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, username, password FROM users WHERE username = ?",
                    (username,))
            user = c.fetchone()
            conn.close()
            
            if user and verify_password(user[2], password):
                login_user(User(user[0], user[1]))
                return redirect(url_for('index'))
            flash('Неверный логин или пароль')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def settings():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if request.method == 'POST':
        min_light = float(request.form['min_light'])
        # max_light = float(request.form['max_light'])
        
        # Проверка корректности введенных значений
        # if min_light >= max_light:
        #     flash('Минимальный уровень освещенности должен быть меньше максимального')
        #     return redirect(url_for('index'))
        
        max_light = 1000
        c.execute("""
            UPDATE light_settings 
            SET min_light = ?, max_light = ? 
            WHERE id = 1
        """, (min_light, max_light))
        conn.commit()
    
    c.execute("SELECT min_light, max_light FROM light_settings WHERE id = 1")
    settings = c.fetchone()
    conn.close()
    
    if request.method == 'POST':
        return redirect(url_for('index'))
    
    return jsonify({
        'min_light': settings[0], 
        'max_light': settings[1]
    })

@app.route('/api/current_light')
@login_required
def current_light():
    """Получение текущих данных об освещенности"""
    try:
        # Получаем последнюю запись из истории освещенности
        history = get_light_history()
        min_light, max_light = get_light_settings()
        
        # Возвращаем последнюю запись (если есть)
        if history:
            last_record = history[-1]
            return jsonify({
                'timestamp': last_record['timestamp'],
                'light_level': last_record['light_level'],
                'light_status': 'ON' if last_record['light_level'] < min_light else 'OFF'
            })
        else:
            return jsonify({'humidity': None, 'fan_status': 'OFF'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@app.route('/api/light_history')
@login_required
def light_history():
    """Получение истории измерений освещенности"""
    history = get_light_history()
    return jsonify(history)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, use_reloader=False)  # use_reloader=False важно при использовании MQTT