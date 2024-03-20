from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, send_file, Response
from functools import wraps 
import os
from flask_sqlalchemy import SQLAlchemy
from flask import make_response
from gtts import gTTS
from models import db, User
from flask_migrate import Migrate
from flask import request, jsonify
from googletrans import Translator
import pyttsx3
import tempfile
from io import BytesIO
from jinja2.exceptions import TemplateNotFound

app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)
migrate = Migrate(app, db)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

translator = Translator()
engine = pyttsx3.init()
TEMPLATES_DIR = os.path.join('E:', 'MCA', 'templates')
SUPPORTED_LANGUAGES = {
    'ta': 'Tamil',
    'kn': 'Kannada',
    'te': 'Telugu',
    'en': 'English',
    'hi':'Hindi'
}

def recreate_tables():
    with app.app_context():
        db.create_all()

recreate_tables()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not name or not email or not password:
        return "Please fill in all the required fields. <a href='/'>Go back</a>."
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return "User already exists. Please sign in <a href='/'>here</a>."
    
    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return f"Sign up successful! Welcome, {name}! <a href='/'>Sign in</a>."

@app.route('/signin', methods=['POST'])
def signin():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    
    if not user or user.password != password:
        return "Invalid email or password. <a href='/'>Try again</a>."
    session['user_name'] = user.name 
    session['user_id'] = user.id
    return render_template('success.html', user_name=user.name)

@app.route('/signout')
def signout():
    session.pop('user_name', None)
    return redirect('/')

@app.route('/submit_percentage', methods=["POST"])
def submit_percentage():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            percentage = request.form.get('percentage')
            if percentage:
                user.exercise_percentage = float(percentage)
                db.session.commit()
                return 'Percentage updated successfully', 200
            else:
                return 'No percentage provided', 400
    return 'User is not logged in', 401

@app.route('/complete_quiz', methods=['POST'])
def complete_quiz():
    score = request.json.get('score')
    
    if score is not None:
        user_name = session.get('user_name')
        user = User.query.filter_by(name=session.get('user_name')).first()
        if user:
            if user.score is None:
                user.score = score
            else:
                user.score += score
                print("Updated score:", user.score)
            db.session.commit()
            return jsonify({'message': 'Score updated successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    else:
        return jsonify({'error': 'Score not provided'}), 400

@app.route('/complete_interactive_lesson', methods=['POST'])
def complete_interactive_lesson():
    user_id = request.json.get('user_id')
    if user_id:
        try:
            user = User.query.get(user_id)
            if user:
                user.lessons_completed += 25
                db.session.commit()
                print("Score updated successfully")
                return 'Score updated successfully', 200
            else:
                return 'User not found', 404
        except Exception as e:
            print(f"Error updating score: {e}")
            return 'Error updating score', 500
    else:
        return 'Missing user information', 400

@app.route('/update_score', methods=['POST'])
def update_score():
    user_id = request.form.get('user_id')
    if user_id:
        try:
            user = User.query.get(user_id)
            if user:
                user.audio_completed += 5
                db.session.commit()
                return 'Score updated successfully', 200
            else:
                return 'User not found', 404
        except Exception as e:
            print(f"Error updating score: {e}")
            return 'Error updating score', 500
    else:
        return 'Missing user information', 400

@app.route('/')
def test_orm_operations():
    new_user = User(username='testuser', audio_completed=10)
    db.session.add(new_user)
    db.session.commit()

    users = User.query.all()
    for user in users:
        print(user.username, user.audio_completed)

    return 'Check the Flask console for user data.'

@app.route('/translate', methods=['GET'])
def translate():
    sentence = request.args.get('sentence')
    target_language = request.args.get('target_language')

    if sentence and target_language:
        translator = Translator()
        translated_text = translator.translate(sentence, dest=target_language).text
        return jsonify({'translated_text': translated_text})
    else:
        return jsonify({'error': 'Missing parameters'})

@app.route('/synthesize', methods=['POST','GET'])
def synthesize_speech():
    translated_text = request.form.get('translated_text')
    target_language = request.form.get('target_language')

    if translated_text and target_language:
        if target_language not in SUPPORTED_LANGUAGES:
            return jsonify({'error': f'Language not supported: {target_language}'}), 400

        try:
            tts = gTTS(text=translated_text, lang=target_language, slow=False)
            _, temp_file_path = tempfile.mkstemp(suffix='.mp3')
            tts.save(temp_file_path)

            return send_file(temp_file_path, as_attachment=True)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Missing parameters'}), 400

@app.route('/speak', methods=['POST'])
def speak():
    user_message = request.form.get('user_message')
    target_language = request.form.get('target_language', 'en')

    if not user_message:
        return jsonify({'error': 'User message not provided'}), 400

    try:
        tts = gTTS(text=user_message, lang=target_language, slow=False)
        _, temp_file_path = tempfile.mkstemp(suffix='.mp3')
        tts.save(temp_file_path)

        user_id = request.form.get('user_id')
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if user:
                user.percentage += 0.5
                db.session.commit()

        return send_file(temp_file_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progresstracking')
def progress():
    user_name = session.get('user_name')
    if user_name:
        user = User.query.filter_by(name=user_name).first()

        if user:
            total_categories = 5
            total_completed = (
                (user.score or 0) + 
                (user.percentage or 0) + 
                (user.audio_completed or 0) + 
                (user.lessons_completed or 0) + 
                (user.exercise_percentage or 0)
            )
            progress_percentage = (total_completed / total_categories ) * 100 

            progress_data = {
                'quiz score': user.score,
                'speaking percentage': user.percentage,
                'Listening Audio': user.audio_completed,
                'Interactive Lessons': user.lessons_completed,
                'Exercises Percentage': user.exercise_percentage,
                'total percentage': progress_percentage
            }

            return render_template('progresstracking.html', progress_data=progress_data)
        else:
            return "User not found."
    else:
        return "User not logged in. <a href='/'>Log in</a>."

@app.route('/success')
def success():
    user_name = session.get('user_name')
    if user_name:
        return render_template('success.html', user_name=user_name)
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect('/')

@app.route('/Speaking', methods=['GET', 'POST'])
def speaking():
    if request.method == 'GET':
        user_id = session.get('user_id', None)
        return render_template('Speaking.html', user_id=user_id)
    elif request.method == 'POST':
        pass


@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

@app.route('/jpg/<path:filename>')
def serve_jpg(filename):
    return send_from_directory('static/jpg', filename)
@app.route('/dynamic_page/<page>')
def dynamic_page(page):
    try:
        return render_template(f"{page}.html")
    except TemplateNotFound:
        return render_template("error.html", message="Template not found")
@app.route('/login', methods=['POST'])
def require_login(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_name' not in session:
            return redirect('/')
        return view(*args, **kwargs)
    return wrapped_view

@app.route('/favicon.ico')
def favicon():
    return "",404

if __name__ == '__main__':
    app.run(debug=True)
