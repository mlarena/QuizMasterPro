document.addEventListener('DOMContentLoaded', function() {
    const questionsContainer = document.getElementById('questionsContainer');
    const addQuestionBtn = document.getElementById('addQuestionBtn');
    const saveQuizBtn = document.getElementById('saveQuizBtn');
    const questionCard = document.querySelector('.question-card');

    const quizData = window.quizData || {title: '', description: '', questions: []};

    if (questionsContainer && addQuestionBtn && saveQuizBtn) {
        if (quizData.questions && quizData.questions.length > 0) {
            quizData.questions.forEach(q => addQuestionElement(questionsContainer, q));
            document.getElementById('quizTitle').value = quizData.title;
            document.getElementById('quizDescription').value = quizData.description;
        } else {
            addQuestionElement(questionsContainer);
        }

        addQuestionBtn.addEventListener('click', () => addQuestionElement(questionsContainer));

        saveQuizBtn.addEventListener('click', function() {
            const quizDataToSave = {
                title: document.getElementById('quizTitle').value,
                description: document.getElementById('quizDescription').value,
                questions: collectQuizData()
            };

            saveQuizBtn.disabled = true;
            saveQuizBtn.innerHTML = '<span class="animate-spin material-icons mr-2 text-sm">sync</span> Сохранение...';

            fetch(window.location.href, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(quizDataToSave)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/admin';
                } else {
                    alert(data.message || 'Ошибка при сохранении');
                    saveQuizBtn.disabled = false;
                    saveQuizBtn.innerHTML = '<span class="material-icons mr-2">save</span> Сохранить квиз';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ошибка при сохранении');
                saveQuizBtn.disabled = false;
            });
        });
    }

    function addQuestionElement(container, questionData = null) {
        const questionId = Date.now();
        const questionDiv = document.createElement('div');
        questionDiv.className = 'bg-slate-50 rounded-2xl p-6 border border-slate-100 space-y-4 relative group question-card animate-fade-in';
        
        questionDiv.innerHTML = `
            <div class="flex items-start justify-between gap-4">
                <div class="flex-grow">
                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Текст вопроса</label>
                    <textarea class="w-full px-4 py-3 bg-white border border-slate-200 focus:border-indigo-500 rounded-xl transition-all outline-none text-sm font-medium text-slate-900 question-textarea" 
                        placeholder="Введите вопрос..." rows="2" required>${questionData ? questionData.text : ''}</textarea>
                </div>
                <button type="button" class="mt-6 p-2 text-slate-300 hover:text-rose-500 transition-colors remove-question">
                    <span class="material-icons">delete_outline</span>
                </button>
            </div>
            
            <div class="space-y-3">
                <div class="flex items-center justify-between">
                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest">Варианты ответов</label>
                    <button type="button" class="text-[10px] font-bold text-indigo-600 hover:text-indigo-700 uppercase tracking-widest add-answer">
                        + Добавить ответ
                    </button>
                </div>
                <div class="answers-container space-y-2"></div>
            </div>
        `;

        const answersContainer = questionDiv.querySelector('.answers-container');
        const addAnswerBtn = questionDiv.querySelector('.add-answer');
        const removeQuestionBtn = questionDiv.querySelector('.remove-question');

        addAnswerBtn.addEventListener('click', () => addAnswerElement(answersContainer));
        removeQuestionBtn.addEventListener('click', () => {
            if (confirm('Удалить этот вопрос?')) questionDiv.remove();
        });

        container.appendChild(questionDiv);

        if (questionData && questionData.answers) {
            questionData.answers.forEach(a => addAnswerElement(answersContainer, a));
        } else {
            addAnswerElement(answersContainer);
            addAnswerElement(answersContainer);
        }
    }

    function addAnswerElement(container, answerData = null) {
        const answerDiv = document.createElement('div');
        answerDiv.className = 'flex items-center gap-3 group/answer answer-option';
        
        answerDiv.innerHTML = `
            <div class="flex-grow relative">
                <input type="text" class="w-full pl-4 pr-10 py-2 bg-white border border-slate-200 focus:border-indigo-500 rounded-lg transition-all outline-none text-sm text-slate-700 answer-textarea" 
                    placeholder="Вариант ответа" value="${answerData ? answerData.text : ''}" required>
                <div class="absolute right-2 top-1/2 -translate-y-1/2 flex items-center">
                    <input type="checkbox" class="h-4 w-4 text-emerald-500 border-slate-300 rounded focus:ring-emerald-500 transition cursor-pointer" 
                        ${answerData && answerData.is_correct ? 'checked' : ''} title="Правильный ответ">
                </div>
            </div>
            <button type="button" class="p-1 text-slate-300 hover:text-rose-500 transition-colors opacity-0 group-hover/answer:opacity-100 remove-answer">
                <span class="material-icons text-sm">close</span>
            </button>
        `;

        answerDiv.querySelector('.remove-answer').addEventListener('click', () => answerDiv.remove());
        container.appendChild(answerDiv);
    }

    function collectQuizData() {
        const questions = [];
        document.querySelectorAll('.question-card').forEach((qEl, qIdx) => {
            const answers = [];
            qEl.querySelectorAll('.answer-option').forEach((aEl, aIdx) => {
                answers.push({
                    text: aEl.querySelector('.answer-textarea').value,
                    is_correct: aEl.querySelector('input[type="checkbox"]').checked,
                    order: aIdx + 1
                });
            });
            questions.push({
                text: qEl.querySelector('.question-textarea').value,
                order: qIdx + 1,
                answers: answers
            });
        });
        return questions;
    }
});