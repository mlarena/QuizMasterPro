Вот как обновить модель `Question` и базу данных с новыми полями:

### 1. Сначала обновите модель `Question` в `app/models.py`:

```python
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    text = db.Column(db.Text, nullable=False)  # Основной текст вопроса (можно использовать для английского)
    text_ru = db.Column(db.Text)  # Текст вопроса на русском
    explanation = db.Column(db.Text)  # Пояснение к вопросу
    order = db.Column(db.Integer)
    
    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.text[:50]}...>'
```

### 2. Создайте миграцию для базы данных:

```powershell
# Активируйте виртуальное окружение (если еще не активировано)
.\venv\Scripts\activate

# Создайте новую миграцию
python -m flask db migrate -m "Add text_ru and explanation fields to Question"

# Примените миграцию
python -m flask db upgrade
```

### 3. Обновите представления, где используется `Question`:

#### В `app/routes/admin_routes.py` обновите обработчики, связанные с вопросами:

```python
@admin_bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET', 'POST'])
@login_required
def manage_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        data = request.get_json()
        
        Question.query.filter_by(quiz_id=quiz_id).delete()
        
        for q in data['questions']:
            question = Question(
                quiz_id=quiz_id,
                text=q.get('text', ''),
                text_ru=q.get('text_ru', ''),
                explanation=q.get('explanation', ''),
                order=q['order']
            )
            db.session.add(question)
            db.session.flush()
            
            for a in q['answers']:
                answer = Answer(
                    question_id=question.id,
                    text=a['text'],
                    is_correct=a['is_correct'],
                    order=a['order']
                )
                db.session.add(answer)
        
        db.session.commit()
        return jsonify({'success': True})
    
    # Остальной код остается без изменений
```

#### В шаблоне `app/templates/admin/manage_questions.html` добавьте новые поля:

```html
<!-- В форме добавления вопроса добавьте: -->
<div class="form-group">
    <label>Текст вопроса (русский)</label>
    <input type="text" class="form-control" data-field="text_ru">
</div>

<div class="form-group">
    <label>Пояснение</label>
    <textarea class="form-control" data-field="explanation"></textarea>
</div>
```

### 4. Обновите JavaScript (app/static/js/admin.js):

В функции `addQuestionElement` добавьте новые поля:

```javascript
function addQuestionElement(questionData = null) {
    // ... существующий код ...
    
    const questionRuInput = document.createElement('input');
    questionRuInput.type = 'text';
    questionRuInput.placeholder = 'Текст вопроса (русский)';
    questionRuInput.dataset.field = 'text_ru';
    if (questionData) questionRuInput.value = questionData.text_ru || '';
    
    const explanationInput = document.createElement('textarea');
    explanationInput.placeholder = 'Пояснение к вопросу';
    explanationInput.dataset.field = 'explanation';
    if (questionData) explanationInput.value = questionData.explanation || '';
    
    // Добавьте эти поля в форму вопроса
    questionHeader.appendChild(questionRuInput);
    questionHeader.appendChild(explanationInput);
    
    // ... остальной код ...
}
```

### 5. Обновите функцию `collectQuizData`:

```javascript
function collectQuizData() {
    const questions = [];
    const questionElements = document.querySelectorAll('.question-card');
    
    questionElements.forEach((qEl, qIdx) => {
        const questionInput = qEl.querySelector('input[data-field="text"]');
        const questionRuInput = qEl.querySelector('input[data-field="text_ru"]');
        const explanationInput = qEl.querySelector('textarea[data-field="explanation"]');
        
        // ... обработка ответов ...
        
        questions.push({
            text: questionInput.value,
            text_ru: questionRuInput.value,
            explanation: explanationInput.value,
            order: qIdx + 1,
            answers: answers
        });
    });
    
    return questions;
}
```

### 6. Перезапустите приложение:

```powershell
python run.py
```

Теперь ваша база данных обновлена с новыми полями, и все представления поддерживают эти изменения. При создании/редактировании вопросов будут доступны новые поля для русского текста и пояснений.