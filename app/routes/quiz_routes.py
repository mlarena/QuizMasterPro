from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from app import db, logger
from app.models import Quiz, Question, Answer, QuizResult
from datetime import datetime
import json

quiz_bp = Blueprint('quiz', __name__, template_folder='../../templates/quiz')

@quiz_bp.route('/')
@login_required
def list_quizzes():
    #Quiz.query.all()
    #quizzes = Quiz.query.filter_by(is_active=True).order_by(Quiz.created_at.desc()).all()
    quizzes = Quiz.query.all()
    logger.info(f'User {current_user.username} accessed quiz list')
    return render_template('quiz/list.html', quizzes=quizzes)

@quiz_bp.route('/<int:quiz_id>/take')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order).all()
    
    questions_data = []
    for q in questions:
        answers = Answer.query.filter_by(question_id=q.id).order_by(Answer.order).all()
        questions_data.append({
            'id': q.id,
            'text': q.text,
            'answers': [{'id': a.id, 'text': a.text} for a in answers]
        })
    
    logger.info(f'User {current_user.username} started quiz {quiz_id}')
    return render_template('quiz/take.html', quiz=quiz, questions=questions_data)

@quiz_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    try:
        user_answers = request.get_json()
        
        # Get correct answers
        correct_answers = db.session.query(Question.id, Answer.id)\
            .join(Answer, Question.id == Answer.question_id)\
            .filter(Question.quiz_id == quiz_id, Answer.is_correct == True)\
            .all()
        
        correct_dict = {}
        for q_id, a_id in correct_answers:
            if q_id not in correct_dict:
                correct_dict[q_id] = []
            correct_dict[q_id].append(a_id)
        
        # Check answers
        results = []
        total = len(correct_dict)
        correct = 0
        
        for q_id, user_a_ids in user_answers.items():
            q_id = int(q_id)
            user_a_ids = [int(a_id) for a_id in user_a_ids]
            
            correct_a_ids = correct_dict.get(q_id, [])
            is_correct = set(user_a_ids) == set(correct_a_ids)
            
            if is_correct:
                correct += 1
            
            results.append({
                'question_id': q_id,
                'is_correct': is_correct,
                'user_answers': user_a_ids,
                'correct_answers': correct_a_ids
            })
        
        # Save result — ИСПРАВЛЕНО: сохраняем полный dict, а не только list
        full_results = {
            'total_questions': total,
            'correct_count': correct,
            'incorrect_count': total - correct,
            'results': results  # list of {'question_id': ..., 'is_correct': ..., 'user_answers': [...], 'correct_answers': [...]}
        }
        result = QuizResult(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=correct / total * 100 if total > 0 else 0,
            details=json.dumps(full_results, ensure_ascii=False)
        )
        db.session.add(result)
        db.session.commit()
        
        logger.info(f'User {current_user.username} completed quiz {quiz_id} with score {correct}/{total}')
        
        return jsonify(full_results)  # Возвращаем то же для frontend
    except Exception as e:
        logger.error(f'Error submitting quiz {quiz_id} for user {current_user.username}: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500


@quiz_bp.route('/<int:quiz_id>/result')
@login_required
def quiz_result(quiz_id):
    result = QuizResult.query.filter_by(quiz_id=quiz_id, user_id=current_user.id).order_by(QuizResult.completed_at.desc()).first()
    if not result:
        logger.warning(f'No result found for quiz {quiz_id} and user {current_user.username}')
        flash('No result found for this quiz', 'error')
        return redirect(url_for('quiz.list_quizzes'))
    
    quiz_results = json.loads(result.details)  # Теперь dict: {'total_questions': ..., 'results': [...]}
    
    # Загружаем вопросы и ответы для сопоставления ID с текстами
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order).all()
    all_answers = Answer.query.filter(Answer.question_id.in_([q.id for q in questions])).all()
    answers_dict = {}  # {question_id: {answer_id: text}}
    for a in all_answers:
        if a.question_id not in answers_dict:
            answers_dict[a.question_id] = {}
        answers_dict[a.question_id][a.id] = a.text
    
    # Обогащаем results (список внутри dict)
    for detail in quiz_results['results']:
        q_id = detail['question_id']
        question = next((q for q in questions if q.id == q_id), None)
        if question:
            detail['question_text'] = question.text
            detail['user_answers_text'] = [answers_dict.get(q_id, {}).get(a_id, f'Unknown ({a_id})') for a_id in detail['user_answers']]
            detail['correct_answers_text'] = [answers_dict.get(q_id, {}).get(a_id, f'Unknown ({a_id})') for a_id in detail['correct_answers']]
    
    logger.info(f'User {current_user.username} viewed result for quiz {quiz_id}')
    return render_template('quiz/result.html', 
                          quiz=Quiz.query.get(quiz_id), 
                          result=result, 
                          quiz_results=quiz_results)  # Передаем dict напрямую