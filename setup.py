#!/usr/bin/env python3
import os
import sys
from subprocess import call

def create_project_structure():
    """Создает структуру папок и файлов проекта"""
    dirs = [
        'app',
        'app/static/css',
        'app/static/js',
        'app/templates',
        'app/templates/auth',
        'app/templates/admin',
        'app/templates/quiz',
        'app/routes',
        'logs',
        'migrations',
        'scripts'
    ]
    
    files = [
        'app/__init__.py',
        'app/config.py',
        'app/logger.py',
        'app/models.py',
        'app/routes/__init__.py',
        'app/routes/admin_routes.py',
        'app/routes/auth_routes.py',
        'app/routes/quiz_routes.py',
        'app/static/css/material.css',
        'app/static/js/admin.js',
        'app/static/js/auth.js',
        'app/static/js/quiz.js',
        'app/templates/base.html',
        'app/templates/auth/login.html',
        'app/templates/admin/create_quiz.html',
        'app/templates/admin/edit_quiz.html',
        'app/templates/admin/manage_questions.html',
        'app/templates/quiz/list.html',
        'app/templates/quiz/take.html',
        'app/templates/quiz/result.html',
        'logs/quizmaster.log',
        'logs/errors.log',
        'requirements.txt',
        'run.py'
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    for file in files:
        open(file, 'a').close()
        print(f"Created file: {file}")
    
    # Установка зависимостей
    call(['pip', 'install', '-r', 'requirements.txt'])
    
    print("\nProject structure created successfully!")
    print("Run the application with: python run.py")

if __name__ == "__main__":
    create_project_structure()