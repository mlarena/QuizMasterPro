document.addEventListener('DOMContentLoaded', function() {
    const quizContainer = document.getElementById('quizContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const prevBtn = document.getElementById('prevQuestionBtn');
    const nextBtn = document.getElementById('nextQuestionBtn');
    const submitBtn = document.getElementById('submitQuizBtn');
    
    const quizId = window.quizConfig.id;
    const questions = window.quizConfig.questions;
    
    let currentQuestion = 0;
    const userAnswers = {};
    
    function initQuiz() {
        if (!questions || questions.length === 0) {
            quizContainer.innerHTML = '<p class="text-center text-slate-500 py-10">Вопросы не найдены.</p>';
            return;
        }
        showQuestion(currentQuestion);
    }
    
    function showQuestion(index) {
        if (index < 0 || index >= questions.length) return;
        
        currentQuestion = index;
        const question = questions[index];
        
        quizContainer.innerHTML = `
            <div class="space-y-8 animate-fade-in">
                <div class="space-y-2">
                    <span class="text-indigo-600 font-bold text-sm uppercase tracking-widest">Вопрос ${index + 1} из ${questions.length}</span>
                    <h3 class="text-2xl font-bold text-slate-900 leading-tight">${question.text}</h3>
                </div>
                
                <div class="grid grid-cols-1 gap-3">
                    ${question.answers.map(a => `
                        <label class="group relative flex items-center p-4 cursor-pointer rounded-2xl border-2 border-slate-100 hover:border-indigo-200 hover:bg-indigo-50/30 transition-all">
                            <div class="flex items-center h-5">
                                <input type="checkbox" name="q-${question.id}" value="${a.id}" 
                                    class="h-5 w-5 text-indigo-600 border-slate-300 rounded-lg focus:ring-indigo-500 transition cursor-pointer">
                            </div>
                            <div class="ml-4 text-sm font-medium text-slate-700 group-hover:text-indigo-900 transition-colors">
                                ${a.text}
                            </div>
                        </label>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Restore selected answers
        if (userAnswers[question.id]) {
            userAnswers[question.id].forEach(aId => {
                const input = document.querySelector(`input[value="${aId}"]`);
                if (input) input.checked = true;
            });
        }
        
        updateProgress();
        updateButtons();
    }
    
    function updateProgress() {
        const percent = Math.round(((currentQuestion + 1) / questions.length) * 100);
        if (progressBar) progressBar.style.width = `${percent}%`;
        if (progressText) progressText.textContent = `${percent}%`;
    }
    
    function updateButtons() {
        const isLast = currentQuestion === questions.length - 1;
        
        // Prev button visibility
        if (currentQuestion === 0) {
            prevBtn.classList.add('opacity-0', 'pointer-events-none');
        } else {
            prevBtn.classList.remove('opacity-0', 'pointer-events-none');
        }
        
        // Next vs Submit
        if (isLast) {
            nextBtn.classList.add('hidden');
            submitBtn.classList.remove('hidden');
        } else {
            nextBtn.classList.remove('hidden');
            submitBtn.classList.add('hidden');
        }
    }
    
    function saveAnswers() {
        const question = questions[currentQuestion];
        const inputs = document.querySelectorAll(`input[name="q-${question.id}"]:checked`);
        userAnswers[question.id] = Array.from(inputs).map(i => parseInt(i.value));
    }
    
    prevBtn.addEventListener('click', function() {
        saveAnswers();
        showQuestion(currentQuestion - 1);
    });
    
    nextBtn.addEventListener('click', function() {
        saveAnswers();
        showQuestion(currentQuestion + 1);
    });
    
    submitBtn.addEventListener('click', function() {
        saveAnswers();
        
        // Показываем состояние загрузки
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="animate-spin material-icons mr-2 text-sm">sync</span> Отправка...';
        
        fetch(`/quizzes/${quizId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userAnswers)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success === false) throw new Error(data.message);
            window.location.href = `/quizzes/${quizId}/result`;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при отправке теста. Попробуйте еще раз.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Завершить <span class="material-icons ml-2">check_circle</span>';
        });
    });
    
    initQuiz();
});