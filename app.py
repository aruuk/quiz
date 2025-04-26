from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import Config
from models import db, User
from weather_api import get_weather 
from quiz_data import quiz_questions
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    print("API KEY:", app.config['WEATHER_API_KEY'])
    if request.method == 'POST':
        city = request.form['city']
        weather = get_weather(city, app.config['WEATHER_API_KEY'])
        if weather is None:
            flash("Не удалось получить прогноз. Проверьте название города.", "danger")
    return render_template('index.html', weather=weather)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('quiz'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        display_name = request.form['display_name'].strip()
        password = request.form['password']
        confirm = request.form['confirm']

        if not username or not display_name or not password or not confirm:
            flash("Заполните все поля", "danger")
            return redirect(url_for('register'))

        if len(username) < 3:
            flash("Логин должен быть не менее 3 символов", "danger")
            return redirect(url_for('register'))

        if password != confirm:
            flash("Пароли не совпадают", "danger")
            return redirect(url_for('register'))

        if len(password) < 6:
            flash("Пароль должен быть не менее 6 символов", "danger")
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash("Логин уже используется", "danger")
            return redirect(url_for('register'))

        user = User(username=username, display_name=display_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Успешная регистрация!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('quiz'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('quiz'))

        flash("Неверный логин или пароль")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    question = random.choice(quiz_questions)

    if request.method == 'POST':
        selected = request.form.get('answer')
        correct = request.form.get('correct')

        if selected == correct:
            current_user.score += 1
            db.session.commit()
            flash("Правильно!", "success")
        else:
            flash("Неправильно!", "danger")

        return redirect(url_for('quiz'))

    return render_template('quiz.html', question=question, score=current_user.score)

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.score.desc()).limit(10).all()
    return render_template('leaderboard.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
