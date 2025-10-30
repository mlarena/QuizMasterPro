document.addEventListener('DOMContentLoaded', function() {
    const questionsContainer = document.getElementById('questionsContainer');
    const addQuestionBtn = document.getElementById('addQuestionBtn');
    const saveQuizBtn = document.getElementById('saveQuizBtn');
    const questionCard = document.querySelector('.question-card');

    if (questionsContainer && addQuestionBtn && saveQuizBtn) { // Create or full edit mode with multiple questions
        // Load existing quiz data if available
        if (quizData.questions && quizData.questions.length > 0) {
            quizData.questions.forEach(q => addQuestionElement(questionsContainer, q));
            document.getElementById('quizTitle').value = quizData.title;
            document.getElementById('quizDescription').value = quizData.description;
        } else {
            addQuestionElement(questionsContainer);
        }

        // Add new question
        addQuestionBtn.addEventListener('click', function() {
            addQuestionElement(questionsContainer);
        });

        // Save quiz
        saveQuizBtn.addEventListener('click', function() {
            const quizDataToSave = {
                title: document.getElementById('quizTitle').value,
                description: document.getElementById('quizDescription').value,
                questions: collectQuizData()
            };

            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(quizDataToSave)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMaterialToast('Quiz saved successfully!', 'success');
                    setTimeout(() => window.location.href = '/admin', 1000);
                } else {
                    showMaterialToast(data.message || 'Error saving quiz', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMaterialToast('Error saving quiz', 'error');
            });
        });
    } else if (questionCard) { // Edit single question mode
        addQuestionElement(questionCard, quizData); // Use existing question-card as container
        const addAnswerBtn = questionCard.querySelector('.btn-secondary'); // Add answer button in template
        if (addAnswerBtn) {
            addAnswerBtn.addEventListener('click', function() {
                addAnswerElement(questionCard.querySelector('.answers-container'));
            });
        }
    }

    function addQuestionElement(container, questionData = null) {
        if (container.classList.contains('question-card')) { // Single question mode
            // Логика для одного вопроса
            const answersContainer = container.querySelector('.answers-container');
            const questionInput = container.querySelector('.question-textarea');
            if (questionData) {
                questionInput.value = questionData.text;
            }

            // Add answers
            if (questionData && questionData.answers && questionData.answers.length > 0) {
                questionData.answers.forEach(a => addAnswerElement(answersContainer, a));
            } else {
                addAnswerElement(answersContainer);
                addAnswerElement(answersContainer);
            }
            return; // Exit, no need to create new div
        }

        // Multiple questions mode
        const questionDiv = document.createElement('div');
        questionDiv.className = 'card question-card';
        
        const cardContent = document.createElement('div');
        cardContent.className = 'card-content';
        
        const questionHeader = document.createElement('div');
        questionHeader.className = 'flex';
        
        const questionInput = document.createElement('textarea');
        questionInput.placeholder = 'Question text';
        questionInput.required = true;
        questionInput.className = 'form-control question-textarea';
        questionInput.rows = 4;
        questionInput.style.width = '100%';
        
        if (questionData) {
            questionInput.value = questionData.text;
        }
        
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'btn btn-error btn-sm ml-2';
        deleteBtn.innerHTML = '<i class="material-icons">delete</i>';
        deleteBtn.addEventListener('click', function() {
            if (confirm('Delete this question?')) {
                questionDiv.remove();
            }
        });
        
        questionHeader.appendChild(questionInput);
        questionHeader.appendChild(deleteBtn);
        
        const answersContainer = document.createElement('div');
        answersContainer.className = 'answers-container mt-2';
        
        const addAnswerBtn = document.createElement('button');
        addAnswerBtn.type = 'button';
        addAnswerBtn.className = 'btn btn-secondary btn-sm';
        addAnswerBtn.textContent = 'Add answer';
        addAnswerBtn.addEventListener('click', function() {
            addAnswerElement(answersContainer);
        });
        
        cardContent.appendChild(questionHeader);
        cardContent.appendChild(answersContainer);
        cardContent.appendChild(addAnswerBtn);
        questionDiv.appendChild(cardContent);
        container.appendChild(questionDiv);
        
        // Add answers
        if (questionData && questionData.answers && questionData.answers.length > 0) {
            questionData.answers.forEach(a => addAnswerElement(answersContainer, a));
        } else {
            addAnswerElement(answersContainer);
            addAnswerElement(answersContainer);
        }
    }

    function addAnswerElement(container, answerData = null) {
        const answerDiv = document.createElement('div');
        answerDiv.className = 'answer-option';
        
        const answerInput = document.createElement('textarea');
        answerInput.placeholder = 'Answer text';
        answerInput.required = true;
        answerInput.className = 'form-control answer-textarea';
        answerInput.rows = 4;
        answerInput.style.width = '100%';
        
        const correctCheckbox = document.createElement('input');
        correctCheckbox.type = 'checkbox';
        correctCheckbox.id = `correct-${Date.now()}`;
        
        const correctLabel = document.createElement('label');
        correctLabel.htmlFor = correctCheckbox.id;
        correctLabel.textContent = 'Correct';
        
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'btn btn-error btn-sm ml-2';
        deleteBtn.innerHTML = '<i class="material-icons">clear</i>';
        deleteBtn.addEventListener('click', function() {
            answerDiv.remove();
        });
        
        const answerControls = document.createElement('div');
        answerControls.className = 'flex flex-center';
        answerControls.appendChild(correctCheckbox);
        answerControls.appendChild(correctLabel);
        answerControls.appendChild(deleteBtn);
        
        if (answerData) {
            answerInput.value = answerData.text;
            correctCheckbox.checked = answerData.is_correct;
        }
        
        answerDiv.appendChild(answerInput);
        answerDiv.appendChild(answerControls);
        container.appendChild(answerDiv);
    }

    function collectQuizData() {
        const questions = [];
        const questionElements = document.querySelectorAll('.question-card');
        
        questionElements.forEach((qEl, qIdx) => {
            const questionInput = qEl.querySelector('.question-textarea');
            const answerElements = qEl.querySelectorAll('.answer-option');
            
            const answers = [];
            answerElements.forEach((aEl, aIdx) => {
                const answerInput = aEl.querySelector('.answer-textarea');
                const correctCheckbox = aEl.querySelector('input[type="checkbox"]');
                
                answers.push({
                    text: answerInput.value,
                    is_correct: correctCheckbox.checked,
                    order: aIdx + 1
                });
            });
            
            questions.push({
                text: questionInput.value,
                order: qIdx + 1,
                answers: answers
            });
        });
        
        return questions;
    }

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
});