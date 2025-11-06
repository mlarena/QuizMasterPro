from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db, logger
from app.models import QuizResult, User, Quiz, Question, Answer
from functools import wraps
import json


admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            logger.warning(f'Unauthorized access attempt by {current_user.username if current_user.is_authenticated else "anonymous"} to admin route')
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@admin_required
def dashboard():
    quizzes = Quiz.query.all()
    logger.info(f'Admin {current_user.username} accessed admin dashboard')
    return render_template('admin/dashboard.html', quizzes=quizzes)

@admin_bp.route('/admin/create', methods=['GET', 'POST'])
@admin_required
def create_quiz():
    if request.method == 'POST':
        try:
            data = request.get_json()
            quiz_title = data.get('title')
            quiz_description = data.get('description')
            questions = data.get('questions', [])

            quiz = Quiz(
                title=quiz_title,
                description=quiz_description,
                created_by=current_user.id,
                is_active=True
            )
            db.session.add(quiz)
            db.session.flush()

            for q_idx, q_data in enumerate(questions, 1):
                question = Question(
                    quiz_id=quiz.id,
                    text=q_data['text'],
                    order=q_idx
                )
                db.session.add(question)
                db.session.flush()

                for a_idx, a_data in enumerate(q_data['answers'], 1):
                    answer = Answer(
                        question_id=question.id,
                        text=a_data['text'],
                        is_correct=a_data['is_correct'],
                        order=a_idx
                    )
                    db.session.add(answer)

            db.session.commit()
            logger.info(f'Quiz "{quiz_title}" created by {current_user.username}')
            return jsonify({'success': True, 'message': 'Quiz created successfully'})
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error creating quiz: {str(e)}')
            return jsonify({'success': False, 'message': str(e)}), 500

    return render_template('admin/create_quiz.html')


# ... (существующий код dashboard и create_quiz остается без изменений)
@admin_bp.route('/admin/edit/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        try:
            quiz.title = request.form.get('title')
            quiz.description = request.form.get('description')
            db.session.commit()
            logger.info(f'Quiz details "{quiz.title}" updated by {current_user.username}')
            flash('Quiz details updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating quiz details {quiz_id}: {str(e)}')
            flash(str(e), 'error')
        return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order).all()
    logger.info(f'Admin {current_user.username} accessed edit quiz {quiz_id}')
    return render_template('admin/edit_quiz.html', quiz=quiz, questions=questions)


@admin_bp.route('/admin/edit/<int:quiz_id>/question/<int:question_order>', methods=['GET', 'POST'])
@admin_required
def edit_question(quiz_id, question_order):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order).all()
    total = len(questions)
    if question_order < 1 or question_order > total + 1:
        flash('Invalid question order', 'error')
        return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))
    
    if question_order == total + 1:
        # Create new question
        question = Question(quiz_id=quiz_id, text='', order=question_order)
        db.session.add(question)
        db.session.commit()
        answers = []
        logger.info(f'New question {question_order} added to quiz {quiz_id} by {current_user.username}')
    else:
        question = questions[question_order - 1]
        answers = Answer.query.filter_by(question_id=question.id).order_by(Answer.order).all()

    if request.method == 'POST':
        try:
            data = request.get_json()
            question.text = data.get('text')
            Answer.query.filter_by(question_id=question.id).delete()
            db.session.flush()
            for a_idx, a_data in enumerate(data.get('answers', []), 1):
                answer = Answer(
                    question_id=question.id,
                    text=a_data['text'],
                    is_correct=a_data['is_correct'],
                    order=a_idx
                )
                db.session.add(answer)
            db.session.commit()
            logger.info(f'Question {question_order} in quiz {quiz_id} updated by {current_user.username}')
            action = data.get('action')
            if action == 'next' and question_order < total + 1:
                return jsonify({'success': True, 'redirect': url_for('admin.edit_question', quiz_id=quiz_id, question_order=question_order + 1)})
            elif action == 'prev' and question_order > 1:
                return jsonify({'success': True, 'redirect': url_for('admin.edit_question', quiz_id=quiz_id, question_order=question_order - 1)})
            else:
                return jsonify({'success': True, 'redirect': url_for('admin.edit_quiz', quiz_id=quiz_id)})
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating question {question_order} in quiz {quiz_id}: {str(e)}')
            return jsonify({'success': False, 'message': str(e)}), 500

    question_data = {
        'text': question.text,
        'answers': [{'id': a.id, 'text': a.text, 'is_correct': a.is_correct} for a in answers]
    }
    return render_template('admin/edit_question.html', quiz=quiz, question_data=question_data, question_order=question_order, total_questions=total + (1 if question_order > total else 0))

@admin_bp.route('/admin/delete/<int:quiz_id>', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        title = quiz.title
        db.session.delete(quiz)
        db.session.commit()
        logger.info(f'Quiz "{title}" deleted by {current_user.username}')
        flash('Quiz deleted successfully', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting quiz {quiz_id}: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/admin/results')
@admin_required
def results_overview():
    from sqlalchemy import text
    query = text("""
        SELECT qr.id, q.title, u.username, qr.score, qr.completed_at, qr.details
        FROM quiz_result qr
        inner join "user" u on qr.user_id = u.id
        inner join quiz q on qr.quiz_id = q.id
        order by qr.completed_at desc
    """)
    results = db.session.execute(query).fetchall()
    
    results_list = []
    for row in results:
        results_list.append({
            'id': row[0],
            'title': row[1],
            'username': row[2],
            'score': row[3],
            'completed_at': row[4],
            'details': row[5]  # JSON string, but not parsed here for overview
        })
    
    logger.info(f'Admin {current_user.username} accessed test results overview')
    return render_template('admin/results_overview.html', results=results_list)



@admin_bp.route('/admin/results/<int:result_id>')
@admin_required
def quiz_result_details(result_id):
    result = QuizResult.query.get_or_404(result_id)
    quiz = Quiz.query.get_or_404(result.quiz_id)
    user = User.query.get_or_404(result.user_id)
    
    try:
        raw_details = result.details or '{}'  # Fallback на пустой объект
        data = json.loads(raw_details)
        
        # Извлекаем список деталей: если dict — берем .get('results'), если list — как есть
        if isinstance(data, dict):
            quiz_results = data.get('results', [])
        elif isinstance(data, list):
            quiz_results = data
        else:
            quiz_results = []
        
        logger.info(f'Result {result_id}: Loaded {len(quiz_results)} details items from raw: {raw_details[:100]}...')
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f'Invalid JSON in result {result_id} details: {str(e)}, raw: {result.details[:200]}')
        quiz_results = []
        flash(f'Invalid result data for ID {result_id}. Check logs for details.', 'error')
    
    detailed_results = []
    for idx, dr in enumerate(quiz_results):
        if not isinstance(dr, dict):
            logger.warning(f'Result {result_id}: Item {idx} is not dict: {type(dr)}')
            continue
        
        try:
            q_id = int(dr.get('question_id', 0))
            if q_id == 0:
                logger.warning(f'Result {result_id}: Invalid question_id in item {idx}: {dr.get("question_id")}')
                continue
            
            question = Question.query.get_or_404(q_id)
            
            # Безопасное приведение ID к int для user_answers и correct_answers
            user_ans_ids = [int(a_id) for a_id in dr.get('user_answers', []) if str(a_id).strip().isdigit()]
            user_ans_texts = []
            for a_id in user_ans_ids:
                answer = Answer.query.get(a_id)
                if answer:
                    user_ans_texts.append(answer.text)
                else:
                    logger.warning(f'Result {result_id}: Missing answer ID {a_id} for user_answers in item {idx}')
            
            correct_ans_ids = [int(a_id) for a_id in dr.get('correct_answers', []) if str(a_id).strip().isdigit()]
            correct_ans_texts = []
            for a_id in correct_ans_ids:
                answer = Answer.query.get(a_id)
                if answer:
                    correct_ans_texts.append(answer.text)
                else:
                    logger.warning(f'Result {result_id}: Missing answer ID {a_id} for correct_answers in item {idx}')
            
            detailed_results.append({
                'question_text': question.text,
                'is_correct': dr.get('is_correct', False),
                'user_answers_text': user_ans_texts,
                'correct_answers_text': correct_ans_texts
            })
            logger.debug(f'Result {result_id}: Processed item {idx} for q_id {q_id}, correct: {dr.get("is_correct")}')
        except Exception as e:
            logger.error(f'Error processing detail {idx} in result {result_id}: {str(e)}, item: {dr}')
            continue
    
    logger.info(f'Admin {current_user.username} accessed details for result {result_id} - {len(detailed_results)} processed items')
    
    if not detailed_results:
        flash('No valid question details found for this result. The test may have no questions or data is corrupted.', 'warning')
    
    return render_template('admin/quiz_result_details.html', 
                          quiz=quiz, 
                          user=user, 
                          result=result, 
                          quiz_results=detailed_results)
