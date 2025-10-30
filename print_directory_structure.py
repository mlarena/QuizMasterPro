import os

def print_directory_structure(path, indent=""):
    if not os.path.exists(path):
        print(f"Path '{path}' does not exist.")
        return

    if os.path.isfile(path):
        print(indent + "|--- " + os.path.basename(path))
        return

    # Исключаем каталоги __pycache__ и venv
    if os.path.basename(path) in ["__pycache__", "venv", "migrations", "logs"]:
        return

    print(indent + "|--- " + os.path.basename(path) + "/")
    indent += "|    "

    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            print_directory_structure(item_path, indent)
        else:
            print(indent + "|- " + item)



if __name__ == "__main__":
     #directory_path = input("Enter the directory path: ")
    directory_path = "C:\\git\\QuizMasterPro"
    print_directory_structure(directory_path)


