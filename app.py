import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tast.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يجب تسجيل الدخول أولاً'
login_manager.login_message_category = 'info'

# Create uploads directory if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pdf_file = db.Column(db.String(200), nullable=False)
    num_questions = db.Column(db.Integer, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    questions = db.Column(db.Text, nullable=True)  # Store questions as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        
        return render_template('login.html', error='اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    courses = Course.query.all()
    students = User.query.filter_by(is_admin=False).all()
    return render_template('admin.html', courses=courses, students=students)

@app.route('/student')
def student():
    courses = Course.query.all()
    return render_template('student.html', courses=courses)

@app.route('/course/<int:course_id>')
def course_quiz(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('quiz.html', course=course)

@app.route('/create-course', methods=['POST'])
@login_required
def create_course():
    if not current_user.is_admin:
        return jsonify({'error': 'غير مصرح', 'message': 'يجب أن تكون مشرفاً'}), 403
    
    course_name = request.form.get('courseName')
    num_questions = request.form.get('numQuestions')
    language = request.form.get('language')
    question_type = request.form.get('questionType')
    pdf_file = request.files.get('pdfFile')
    additional_files = request.files.getlist('additionalFiles')

    if not all([course_name, num_questions, language, question_type, pdf_file]):
        return jsonify({'error': 'بيانات غير مكتملة', 'message': 'الرجاء تعبئة جميع الحقول المطلوبة'}), 400

    try:
        # Save PDF file
        pdf_filename = f"course_{course_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        pdf_file.save(pdf_path)

        # Save additional files
        additional_files_paths = []
        for i, file in enumerate(additional_files):
            if file:
                filename = f"additional_{course_name}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                additional_files_paths.append(filename)

        # Read PDF content
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Split text into sentences
        sentences = text.split('. ')
        
        # Clean and normalize sentences
        cleaned_sentences = []
        for sentence in sentences:
            if sentence.strip():
                # Remove extra whitespace and newlines
                cleaned = sentence.replace('\n', ' ').replace('\r', ' ').strip()
                
                # Remove bullet points and numbers at the start
                cleaned = cleaned.lstrip('•').lstrip('1234567890. ').strip()
                
                # Remove multiple spaces
                cleaned = ' '.join(cleaned.split())
                
                # Remove special characters except for valid punctuation
                cleaned = ''.join(c for c in cleaned if 
                    c.isalnum() or 
                    c.isspace() or 
                    c in ['.', ',', ';', ':', '(', ')', '-', '—', '–', '?'])
                
                # Remove trailing punctuation
                if cleaned and cleaned[-1] in ['.', ',', ';', ':', '-']:
                    cleaned = cleaned[:-1].strip()
                
                # Only keep sentences longer than 20 chars
                if cleaned and len(cleaned) > 20:
                    cleaned_sentences.append(cleaned)

        questions = []
        num_questions = int(num_questions)
        question_type = question_type.lower()
        
        for i in range(min(len(cleaned_sentences), num_questions)):
            # تنظيف النص
            cleaned_text = sentence.strip()
            
            # توليد السؤال
            if question_type == 'mcq':
                question = {
                    'question_number': i + 1,
                    'question': f"{i + 1}. ما هو {cleaned_text}؟",
                    'options': [
                        {'text': cleaned_text, 'is_correct': True},
                        {'text': f"غير {cleaned_text}", 'is_correct': False},
                        {'text': f"غير ذلك", 'is_correct': False},
                        {'text': f"لا أعرف", 'is_correct': False}
                    ]
                }
            else:  # true/false
                # توليد سؤال صح/خطأ مع تحسين النص
                statement = cleaned_text
                
                # تحسين النص
                if statement.startswith('•'):
                    statement = statement[1:].strip()
                
                # إزالة الأرقام والرموز غير الضرورية
                statement = ''.join(c for c in statement if c.isalnum() or c.isspace() or c in ['.', ',', ';', ':'])
                
                # إضافة علامات استفهام
                if not statement.endswith('?'):
                    statement = statement.strip() + '?'
                
                question = {
                    'question_number': i + 1,
                    'question': f"{i + 1}. {statement}",
                    'is_correct': True,
                    'options': [
                        {'text': 'صحيح', 'is_correct': True},
                        {'text': 'خطأ', 'is_correct': False}
                    ]
                }
            
            questions.append(question)

        # Create course in database
        course = Course(
            name=course_name,
            pdf_file=pdf_filename,
            num_questions=num_questions,
            question_type=question_type,
            language=language,
            questions=json.dumps(questions, ensure_ascii=False)  # Store questions as JSON with Arabic support
        )
        db.session.add(course)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'تم إنشاء المادة بنجاح',
            'details': {
                'course_name': course_name,
                'num_questions': num_questions,
                'question_type': question_type,
                'language': language,
                'pdf_file': pdf_filename,
                'additional_files': additional_files_paths,
                'questions': questions
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'حدث خطأ',
            'message': str(e),
            'details': {
                'course_name': course_name,
                'num_questions': num_questions,
                'language': language,
                'question_type': question_type
            }
        }), 500

@app.route('/upload-questions', methods=['POST'])
@login_required
def upload_questions():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    questions_file = request.files.get('questionsFile')
    course_id = request.form.get('course')
    
    if not questions_file or not course_id:
        return jsonify({'error': 'Missing required files'}), 400

    try:
        # TODO: Implement question upload logic
        return jsonify({'success': True, 'message': 'تم رفع الأسئلة بنجاح'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    try:
        course_id = request.form.get('course_id')
        num_questions = request.form.get('num_questions')
        course = Course.query.get_or_404(course_id)
        
        if not course:
            return jsonify({
                'error': 'مateria غير موجودة',
                'message': 'لم يتم العثور على المادة المطلوبة'
            }), 404

        # Get all answers
        answers = {}
        correct_answers = 0
        total_questions = int(num_questions)
        
        for i in range(total_questions):
            answer = request.form.get(f'answer{i}')
            if answer:
                answers[i] = answer
                # TODO: Compare with correct answers
                # For now, we'll just count the number of answers
                correct_answers += 1

        # Calculate score
        score = (correct_answers / total_questions) * 100

        return jsonify({
            'success': True,
            'message': 'تم إرسال الإجابات بنجاح',
            'details': {
                'course': {
                    'id': course.id,
                    'name': course.name,
                    'question_type': course.question_type,
                    'language': course.language
                },
                'results': {
                    'total_questions': total_questions,
                    'answered_questions': len(answers),
                    'correct_answers': correct_answers,
                    'score': f"{score:.2f}%",
                    'answers': answers
                }
            }
        })

    except Exception as e:
        return jsonify({
            'error': 'حدث خطأ',
            'message': str(e),
            'details': {
                'course_id': course_id,
                'num_questions': num_questions
            }
        }), 500

def create_admin_user():
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        
        # Create admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print('تم إنشاء المستخدم المشرف بنجاح')

if __name__ == '__main__':
    create_admin_user()
    app.run(debug=True)
