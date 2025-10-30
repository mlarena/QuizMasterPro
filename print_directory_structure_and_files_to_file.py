import os
import sys

def read_entire_file(file_path):
    """
    Читает всё содержимое файла
    """
    try:
        # Пробуем разные кодировки для чтения файлов
        encodings = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        return "[бинарный файл или нечитаемый формат]"
    except Exception as e:
        return f"[ошибка чтения файла: {str(e)}]"

def should_exclude(item_path, excluded_dirs, excluded_files):
    """
    Проверяет, нужно ли исключить файл или папку
    """
    name = os.path.basename(item_path)
    
    # Проверка исключенных папок
    if os.path.isdir(item_path) and name in excluded_dirs:
        return True
    
    # Проверка исключенных файлов
    if os.path.isfile(item_path):
        # Проверка точного совпадения
        if name in excluded_files:
            return True
        # Проверка по шаблону (например, *.log)
        for pattern in excluded_files:
            if '*' in pattern:
                ext = pattern.replace('*', '')
                if name.endswith(ext):
                    return True
    return False

def print_directory_structure(path, indent="", output_file=None, is_last=True, is_root=True):
    """
    Рекурсивно выводит структуру папок и содержимое файлов
    """
    if not os.path.exists(path):
        message = f"Path '{path}' does not exist."
        print(message)
        if output_file:
            output_file.write(message + '\n')
        return

    # Исключаем каталоги
    excluded_dirs = {"__pycache__", "venv", "migrations", "logs", ".git", ".idea", 
                    "node_modules", "bin", "obj", "SRTM", ".vscode", "__pycache__"}
    # Исключаем файлы
    excluded_files = {".gitignore", ".env", ".env.local", "config.py", "settings.py", 
                     "*.log", "*.pyc", "*.pyo", "*.pyd", "quizmaster.db", "info.txt", 
                     "info_q.md", "promt.txt", "requirements.txt", "Dockerfile",
                     "*.db", "*.sqlite", "*.sqlite3", "*.jpg", "*.png", "*.gif"}

    # Проверяем, не исключен ли текущий элемент
    if should_exclude(path, excluded_dirs, excluded_files):
        return

    # Для файлов
    if os.path.isfile(path):
        filename = os.path.basename(path)
        
        # Определяем отступы для визуального представления
        if is_root:
            prefix = "|--- "
        else:
            prefix = "|- " if is_last else "|- "
        
        line = indent + prefix + filename
        print(line)
        if output_file:
            output_file.write(line + '\n')
        
        # Выводим содержимое файла
        content = read_entire_file(path)
        content_indent = indent + (" " * 4)  # Увеличиваем отступ для содержимого
        
        if content.strip():  # Выводим содержимое только если файл не пустой
            print(content_indent + "|")
            if output_file:
                output_file.write(content_indent + "|\n")
            
            for line_content in content.splitlines():
                content_line = content_indent + "| " + line_content
                print(content_line)
                if output_file:
                    output_file.write(content_line + '\n')
        
        return

    # Для папок
    if is_root:
        line = indent + "|--- " + os.path.basename(path) + "/"
    else:
        line = indent + "|- " + os.path.basename(path) + "/"
    
    print(line)
    if output_file:
        output_file.write(line + '\n')

    try:
        # Получаем список всех элементов в папке и сортируем (сначала папки, потом файлы)
        items = os.listdir(path)
        items.sort()
        
        # Разделяем папки и файлы
        dirs = [item for item in items if os.path.isdir(os.path.join(path, item))]
        files = [item for item in items if os.path.isfile(os.path.join(path, item))]
        
        # Сортируем и объединяем
        sorted_items = sorted(dirs) + sorted(files)
        
        # Фильтруем исключенные элементы
        filtered_items = []
        for item in sorted_items:
            item_path = os.path.join(path, item)
            if not should_exclude(item_path, excluded_dirs, excluded_files):
                filtered_items.append(item)
        
        # Обрабатываем каждый элемент
        for i, item in enumerate(filtered_items):
            item_path = os.path.join(path, item)
            is_last_item = (i == len(filtered_items) - 1)
            
            # Увеличиваем отступ для вложенных элементов
            new_indent = indent + (" " * 4)
            
            print_directory_structure(
                item_path, 
                new_indent, 
                output_file, 
                is_last_item, 
                is_root=False
            )
            
    except PermissionError:
        error_msg = indent + "  [доступ запрещен]"
        print(error_msg)
        if output_file:
            output_file.write(error_msg + '\n')
    except Exception as e:
        error_msg = indent + f"  [ошибка: {str(e)}]"
        print(error_msg)
        if output_file:
            output_file.write(error_msg + '\n')

if __name__ == "__main__":
    # Можно указать путь как аргумент командной строки или использовать по умолчанию
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
    else:
        directory_path = "C:\\dev\\FloodSimulationApp"
    
    # Проверяем существование пути
    if not os.path.exists(directory_path):
        print(f"Ошибка: путь '{directory_path}' не существует!")
        sys.exit(1)
    
    print(f"Анализируем структуру: {directory_path}")
    
    # Открываем файл для записи
    with open("structure_and_files.txt", "w", encoding="utf-8") as output_file:
        # Сохраняем оригинальный stdout для возможности одновременного вывода на экран
        original_stdout = sys.stdout
        
        # Перенаправляем вывод одновременно в файл и на экран
        class DualOutput:
            def __init__(self, file, console):
                self.file = file
                self.console = console
            
            def write(self, message):
                self.console.write(message)
                self.file.write(message)
            
            def flush(self):
                self.console.flush()
                self.file.flush()
        
        # Устанавливаем двойной вывод
        dual_output = DualOutput(output_file, original_stdout)
        sys.stdout = dual_output
        
        try:
            print("Структура проекта и содержимое файлов:")
            print("=" * 50)
            print_directory_structure(directory_path)
            print("=" * 50)
            print("Вывод завершен. Результат сохранен в structure_and_files.txt")
        finally:
            # Восстанавливаем оригинальный stdout
            sys.stdout = original_stdout