document.addEventListener('DOMContentLoaded', function() {
    const quizContainer = document.getElementById('quizContainer');
    const questionProgress = document.getElementById('questionProgress');
    const prevBtn = document.getElementById('prevQuestionBtn');
    const nextBtn = document.getElementById('nextQuestionBtn');
    const submitBtn = document.getElementById('submitQuizBtn');
    
    let currentQuestion = 0;
    const userAnswers = {};
    
    // Initialize quiz
    function initQuiz() {
        showQuestion(currentQuestion);
        updateProgress();
        updateButtons();
    }
    
    // Show question
    function showQuestion(index) {
        if (index < 0 || index >= questions.length) return;
        
        currentQuestion = index;
        const question = questions[index];
        
        quizContainer.innerHTML = `
            <div class="card question-card">
                <div class="card-content">
                    <h3>Question ${index + 1}</h3>
                    <p>${question.text}</p>
                    
                    <div class="answers-list">
                        ${question.answers.map(a => `
                            <label class="answer-option">
                                <input type="checkbox" name="q-${question.id}" value="${a.id}">
                                <span>${a.text}</span>
                            </label>
                        `).join('')}
                    </div>
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
    
    // Update progress
    function updateProgress() {
        questionProgress.innerHTML = `
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${(currentQuestion + 1) / questions.length * 100}%"></div>
                </div>
                <p>Question ${currentQuestion + 1} of ${questions.length}</p>
            </div>
        `;
    }
    
    // Update buttons
    function updateButtons() {
        prevBtn.disabled = currentQuestion === 0;
        nextBtn.disabled = currentQuestion === questions.length - 1;
        submitBtn.style.display = currentQuestion === questions.length - 1 ? 'block' : 'none';
    }
    
    // Save answers
    function saveAnswers() {
        const question = questions[currentQuestion];
        const inputs = document.querySelectorAll(`input[name="q-${question.id}"]:checked`);
        
        userAnswers[question.id] = Array.from(inputs).map(i => parseInt(i.value));
    }
    
    // Events
    prevBtn.addEventListener('click', function() {
        saveAnswers();
        currentQuestion--;
        showQuestion(currentQuestion);
    });
    
    nextBtn.addEventListener('click', function() {
        saveAnswers();
        currentQuestion++;
        showQuestion(currentQuestion);
    });
    
    submitBtn.addEventListener('click', function() {
        saveAnswers();
        
        fetch(`/quizzes/${quizId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userAnswers)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success === false) {
                throw new Error(data.message);
            }
            sessionStorage.setItem('quizResults', JSON.stringify(data));
            window.location.href = `/quizzes/${quizId}/result`;
        })
        .catch(error => {
            console.error('Error:', error);
            showMaterialToast('Error submitting quiz', 'error');
        });
    });
    
    function showMaterialToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }, 100);
    }
    
    // Start quiz
    initQuiz();
});