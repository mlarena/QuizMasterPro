import sqlite3
from datetime import datetime

def parse_questions_file_simple(filename):
    """
    Упрощенный парсер без регулярных выражений
    """
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    quiz_title = lines[0].strip()
    questions = []
    current_question = None
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        
        # Вопрос (начинается с цифры и точки)
        if line and line[0].isdigit() and '.' in line:
            if current_question:
                questions.append(current_question)
            
            dot_pos = line.find('.')
            try:
                question_num = int(line[:dot_pos].strip())
                question_text = line[dot_pos+1:].strip()
                current_question = {
                    'number': question_num,
                    'text': question_text,
                    'answers': []
                }
            except ValueError:
                continue
                
        # Ответ (начинается с a), b), c), d))
        elif current_question and line and len(line) >= 2 and line[0].lower() in 'abcd' and line[1] in ')':
            answer_letter = line[0].lower()
            answer_text = line[2:].strip()
            current_question['answers'].append({
                'letter': answer_letter,
                'text': answer_text,
                'is_correct': False
            })
                
        # Правильный ответ
        elif current_question and 'правильный ответ:' in line.lower():
            for char in line.lower():
                if char in 'abcd':
                    for answer in current_question['answers']:
                        if answer['letter'] == char:
                            answer['is_correct'] = True
                    break
    
    if current_question:
        questions.append(current_question)
    
    return quiz_title, questions

# Настройки
db_path = 'C:\\dev\\_QuizMasterPro\\quizmaster.db'
input_file = 'C:\\dev\\_QuizMasterPro\\zquiz\\z_22.txt'

print("Загрузка вопросов...")

try:
    quiz_title, questions = parse_questions_file_simple(input_file)
    print(f"Тест: {quiz_title}")
    print(f"Вопросов: {len(questions)}")
    
    # Подключаемся к базе
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем тест
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    cursor.execute('''
        INSERT INTO quiz (title, description, created_at, created_by, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', (quiz_title, '', created_at, 1, True))
    
    quiz_id = cursor.lastrowid
    print(f"Создан тест ID: {quiz_id}")
    
    # Добавляем вопросы и ответы
    for q in questions:
        cursor.execute('''
            INSERT INTO question (quiz_id, text, "order")
            VALUES (?, ?, ?)
        ''', (quiz_id, q['text'], q['number']))
        
        question_id = cursor.lastrowid
        
        # Добавляем ответы
        order = 1
        for answer in q['answers']:
            cursor.execute('''
                INSERT INTO answer (question_id, text, is_correct, "order")
                VALUES (?, ?, ?, ?)
            ''', (question_id, answer['text'], answer['is_correct'], order))
            order += 1
        
        print(f"Добавлен вопрос {q['number']} с {len(q['answers'])} ответами")
    
    conn.commit()
    conn.close()
    
    print(f"Готово! Добавлено {len(questions)} вопросов.")
    
except Exception as e:
    print(f"Ошибка: {e}")

input("Нажмите Enter...")