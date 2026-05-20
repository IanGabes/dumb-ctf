from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from questions import questions

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-very-secret2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    current_question = db.Column(db.Integer, default=1)
    answers = db.relationship('UserAnswer', backref='user', lazy=True)

class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    submitted_answer = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('quiz'))
        
        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/quiz', methods=['GET', 'POST'])
@app.route('/quiz/<int:q_id>', methods=['GET', 'POST'])
@login_required
def quiz(q_id=None):
    # If no q_id is provided, go to the user's current progress
    if q_id is None:
        return redirect(url_for('quiz', q_id=current_user.current_question))
    
    # Safety check: Cannot skip ahead
    if q_id > current_user.current_question:
        return redirect(url_for('quiz', q_id=current_user.current_question))
    
    # Check if finished
    if q_id > len(questions):
        return render_template('finished.html')
    
    question_data = questions[q_id - 1]
    
    if request.method == 'POST':
        # Only process answers if they are on their furthest question
        if q_id == current_user.current_question:
            user_answer_text = request.form.get('answer', '').strip()
            if user_answer_text.lower() == question_data['answer'].lower():
                # Save the answer
                new_answer = UserAnswer(user_id=current_user.id, question_id=q_id, submitted_answer=user_answer_text)
                db.session.add(new_answer)
                
                current_user.current_question += 1
                db.session.commit()
                return redirect(url_for('quiz', q_id=current_user.current_question))
            else:
                flash('IncorrecT', 'error')
        else:
            # If they are viewing an old question and "submit", just take them to the next one they've already cleared
            return redirect(url_for('quiz', q_id=q_id + 1))
            
    # Retrieve previous answer if it exists
    prev_ans_obj = UserAnswer.query.filter_by(user_id=current_user.id, question_id=q_id).first()
            
    return render_template('quiz.html', 
                           question=question_data, 
                           is_latest=(q_id == current_user.current_question),
                           max_reached=current_user.current_question,
                           prev_answer=prev_ans_obj.submitted_answer if prev_ans_obj else None)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
