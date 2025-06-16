#!/usr/bin/env python3
"""
Эффективный скрипт для удаления всех эмодзи из файлов проекта
"""
import os
import re
import sys
from pathlib import Path

def remove_emojis_from_text(text):
    """Удаляет все эмодзи из текста используя расширенный regex"""
    # Комплексный regex для всех эмодзи
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"  # dingbats
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+", flags=re.UNICODE)
    
    return emoji_pattern.sub('', text)

def should_process_file(file_path):
    """Определяет, нужно ли обрабатывать файл"""
    # Исключаем служебные директории
    excluded_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', 'node_modules', 'temp'}
    excluded_files = {'remove_emojis_new.py'}
    
    path_parts = Path(file_path).parts
    
    # Проверяем исключенные директории
    if any(excluded_dir in path_parts for excluded_dir in excluded_dirs):
        return False
    
    # Проверяем исключенные файлы
    if Path(file_path).name in excluded_files:
        return False
    
    # Обрабатываем текстовые файлы
    extensions = {'.md', '.txt', '.yml', '.yaml', '.py', '.sh', '.cfg', '.conf', '.json'}
    return Path(file_path).suffix.lower() in extensions

def process_file(file_path):
    """Обрабатывает один файл"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        cleaned_content = remove_emojis_from_text(original_content)
        
        # Записываем только если содержимое изменилось
        if cleaned_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"Обработан: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Ошибка при обработке {file_path}: {e}")
        return False

def main():
    """Основная функция"""
    project_root = Path('.')
    processed_count = 0
    
    print("Удаление эмодзи из файлов проекта...")
    
    # Рекурсивно обходим все файлы
    for file_path in project_root.rglob('*'):
        if file_path.is_file() and should_process_file(file_path):
            if process_file(file_path):
                processed_count += 1
    
    print(f"\nОбработано файлов: {processed_count}")
    print("Готово!")

if __name__ == "__main__":
    main()
