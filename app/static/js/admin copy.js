document.addEventListener('DOMContentLoaded', function() {
    addQuestionElement(quizData); // Загружает данные одного вопроса

    const addAnswerBtn = document.querySelector('.btn-secondary'); // Адаптировать селектор если нужно
    addAnswerBtn.addEventListener('click', function() {
        addAnswerElement(document.querySelector('.answers-container'));
    });

    // Функции для добавления/удаления ответов и сбора данных остаются
    function addQuestionElement(questionData = null) {
        // Логика для одного вопроса (без контейнера для нескольких)
        const questionDiv = document.querySelector('.question-card'); // Предполагается, что шаблон имеет один .question-card
        const answersContainer = questionDiv.querySelector('.answers-container');

        const questionInput = questionDiv.querySelector('.question-textarea');
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
        // Адаптировано для одного вопроса
        const questionInput = document.querySelector('.question-textarea');
        const answerElements = document.querySelectorAll('.answer-option');
        
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
        
        return [{ // Возвращаем массив с одним вопросом
            text: questionInput.value,
            order: 1, // Поскольку один вопрос
            answers: answers
        }];
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