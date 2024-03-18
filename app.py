from flask import Flask, render_template, request, redirect, url_for, session,send_from_directory,send_file,Response
from functools import wraps 
import os
from flask_sqlalchemy import SQLAlchemy
from flask import make_response
from gtts import gTTS
from models import db,User
from flask_migrate import Migrate
from flask import request, jsonify
from googletrans import Translator
import pyttsx3
import tempfile
from io import BytesIO
from nltk.corpus import wordnet as wn
app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)
migrate = Migrate(app, db)

translator = Translator()
engine = pyttsx3.init()
TEMPLATES_DIR = os.path.join('E:', 'MCA', 'templates')
#app1= Flask(__name__, static_folder='static')
# Define the User model for the database.
SUPPORTED_LANGUAGES = {
    'ta': 'Tamil',
    'kn': 'Kannada',
    'te': 'Telugu',
     'en':'English'
    # Add more languages as needed...
}


# Define a function to create database tables.
def recreate_tables():
    with app.app_context():
        db.create_all()

# Create the database tables.
recreate_tables()

# ... Rest of your Flask routes and code ...


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
    
    # Check if the user already exists in the database.
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return "User already exists. Please sign in <a href='/'>here</a>."
    
    # Create a new user and add it to the database.
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
    user_id = session.get('user_id')  # Retrieve user ID from session
    if user_id:  # Check if user ID exists in session
        user = User.query.get(user_id)  # Fetch user by user ID
        if user:
            percentage = request.form.get('percentage')
            if percentage:
                user.exercise_percentage = float(percentage)
                db.session.commit()
                return 'Percentage updated successfully', 200
            else:
                return 'No percentage provided', 400
    return 'User is not logged in', 401


# Route for completing a listening quiz5
@app.route('/complete_quiz', methods=['POST'])
def complete_quiz():
    # Extract the score from the JSON data
    score = request.json.get('score')
    
    # Ensure the score is not None
    if score is not None:
        # Update the use's score in the database
        user_name = session.get('user_name')
        user = User.query.filter_by(name=session.get('user_name')).first()
        if user:
            # Ensure user.score is not None before adding the score
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
        # If the score is not provided, return an error response
        return jsonify({'error': 'Score not provided'}), 400


# Route for completing an interactive lesson
@app.route('/complete_interactive_lesson', methods=['POST'])
def complete_interactive_lesson():
    user_id = request.form.get('user_id')
    print("Received user_id:", user_id)  
    print(user_id)
    if user_id:
        try:
            user = User.query.get(user_id)
            print("\n\n\n",type(user),"\n\n\n")
            print("User found:", user)  # Print out the user object for debugging

            if user:
                user.lessons_completed += 25  # Increment the score by 50
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
  user_id= request.form.get('user_id')
  if user_id:
    try:
      # Fetch the user from the database
      user = User.query.get(user_id)

      # Update audio_completed only if the user exists
      if user:
        user.audio_completed += 5  # Increment the score by 1
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
    # Create a new user
    new_user = User(username='testuser', audio_completed=10)
    db.session.add(new_user)
    db.session.commit()

    # Retrieve all users from the database
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

@app.route('/synthesize', methods=['GET'])
def synthesize_speech():
    translated_text = request.args.get('translated_text')
    target_language = request.args.get('target_language')

    if translated_text and target_language:
        # Check if the target language is in the list of supported languages
        if target_language not in SUPPORTED_LANGUAGES:
            return jsonify({'error': f'Language not supported: {target_language}'}), 400

        # Convert translated text to speech
        tts = gTTS(text=translated_text, lang=target_language)
        speech_bytes = BytesIO()
        tts.write_to_fp(speech_bytes)
        speech_bytes.seek(0)

        # Return the audio blob
        return Response(speech_bytes, mimetype='audio/mpeg')
    else:
        return jsonify({'error': 'Missing parameters'}), 400

@app.route('/speak', methods=['POST'])
def speak():
    # Get user message and target language from request
    user_message = request.form.get('user_message')
    target_language = request.form.get('target_language', 'en')  # Default to English if target language not provided

    if not user_message:
        return jsonify({'error': 'User message not provided'}), 400

    try:
        # Perform text-to-speech synthesis
        tts = gTTS(text=user_message, lang=target_language, slow=False)
        
        # Save synthesized speech to a temporary file
        _, temp_file_path = tempfile.mkstemp(suffix='.mp3')
        tts.save(temp_file_path)

        # Update user's percentage
        user_id = request.form.get('user_id')  # Assuming you store user's name in cookies
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if user:
                user.percentage += 0.5
                db.session.commit()

        # Return the synthesized speech file to the client
        return send_file(temp_file_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progresstracking')
def progress():
    # Get the user's progress from the database
    user_name = session.get('user_name')  # Safely retrieve the user_name from the session
    if user_name:
        user = User.query.filter_by(name=user_name).first()

        # Calculate progress percentage for each category
        if user:
            total_categories = 5  # Assuming there are 5 categories
            total_completed = (
                (user.score or 0) + 
                (user.percentage or 0) + 
                (user.audio_completed or 0) + 
                (user.lessons_completed or 0) + 
                (user.exercise_percentage or 0)
            )
            progress_percentage = (total_completed / total_categories ) * 100 
             # Assuming each category has 3 tasks

            progress_data = {
                'quiz score': user.score,
                'speaking percentage': user.percentage,
                'Listening Audio': user.audio_completed,
                'Interactive Lessons': user.lessons_completed,
                'Exercises Percentage': user.exercise_percentage,
                'total percentage':progress_percentage
            }
            # Render the progress template and pass the progress data to it
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
        # Retrieve user_id from session or set it to None if not available
        user_id = session.get('user_id', None)
        return render_template('Speaking.html', user_id=user_id)
    elif request.method == 'POST':
        # Handle POST request if needed
        pass


@app.route('/comprehension')
def comprehension():
   return render_template('comprehension.html')
@app.route('/lesson')
def lesson():
    return render_template('lesson.html')
@app.route('/exercises')
def exercises():
    return render_template('exercises.html')

@app.route('/audio materials')
def audio_materials():
    return render_template('audio materials.html')

@app.route('/quizzes')
def quizzes():
    return render_template('quizzes.html')
@app.route('/lesson1 tamil')
def lesson1_tamil():
    return render_template('lesson1 tamil.html')

@app.route('/lesson2 tamil')
def lesson2_tamil():
    return render_template('lesson2 tamil.html')

@app.route('/lesson1 hindi')
def lesson1_hindi():
    return render_template('lesson1 hindi.html')

@app.route('/lesson2 hindi')
def lesson2_hindi():
    return render_template('lesson2 hindi.html')

@app.route('/lesson1 kannada')
def lesson1_kannada():
    return render_template('lesson1 kannada.html')

@app.route('/lesson2 kannada')
def lesson2_kannada():
    return render_template('lesson2 kannada.html')

@app.route('/exercise-1 tamil')
def exercise_1_tamil():
    return render_template('exercise-1 tamil.html')

@app.route('/exercise-2 tamil')
def exercise_2_tamil():
    return render_template('exercise-2 tamil.html')

@app.route('/exercise-1 hindi')
def exercise_1_hindi():
    return render_template('exercise-1 hindi.html')

@app.route('/exercise-2 hindi')
def exercise_2_hindi():
    return render_template('exercise-2 hindi.html')

@app.route('/exercise-1 kannada')
def exercise_1_kannada():
    return render_template('exercise-1 kannada.html')

@app.route('/exercise-2 kannada')
def exercise_2_kannada():
    return render_template('exercise-2 kannada.html')
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)
@app.route('/jpg/<path:filename>')
def serve_jpg(filename):
    return send_from_directory('static/jpg', filename)
@app.route('/hindiqz-1')
def hindi_quiz1():
    return render_template('hindiqz-1.html')

@app.route('/hindiqz-2')
def hindi_quiz2():
    return render_template('hindiqz-2.html')

@app.route('/hindiqz-3')
def hindi_quiz3():
    return render_template('hindiqz-3.html')

@app.route('/Quiz-1')
def tamil_quiz1():
    return render_template('Quiz-1.html')

@app.route('/Quiz-2')
def tamil_quiz2():
    return render_template('Quiz-2.html')
@app.route('/Quiz-3')
def tamil_quiz3():
    return render_template('Quiz-3.html')

@app.route('/kannadaqz-1')
def kannada_quiz1():
    return render_template('kannadaqz-1.html')

@app.route('/kannadaqz-2')
def kannada_quiz2():
    return render_template('kannadaqz-2.html')

@app.route('/kannadaqz-3')
def kannada_quiz3():
    return render_template('kannadaqz-3.html')

@app.route('/login', methods=['POST'])
def require_login(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_name' not in session:
            return redirect('/')
        return view(*args, **kwargs)
    return wrapped_view

# Rest of your code


if __name__ == '__main__':
    app.run(debug=True)