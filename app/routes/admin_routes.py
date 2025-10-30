from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db, logger
from app.models import Quiz, Question, Answer
from functools import wraps

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

# ... (существующий код delete_quiz остается без изменений)





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