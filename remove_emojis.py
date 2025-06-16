#!/usr/bin/env python3
"""
Скрипт для удаления эмодзи из всех файлов проекта.
"""

import os
import re
from pathlib import Path

def remove_emojis_from_text(text):
    """Удаляет эмодзи из текста и заменяет их на текстовые эквиваленты."""
    
    replacements = {
        '': '',
        'ОШИБКА: ': 'ОШИБКА: ',
        '': '',
        '': '',
        'ПРЕДУПРЕЖДЕНИЕ: ': 'ПРЕДУПРЕЖДЕНИЕ: ',
        'ТАЙМ-АУТ: ': 'ТАЙМ-АУТ: ',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '## ': '## ',
        '### ': '### ',
        '### ': '### ',
        '## ': '## ',
        '## ': '## ',
    }
    
    result = text
    for emoji, replacement in replacements.items():
        result = result.replace(emoji, replacement)
    
    return result

def process_file(file_path):
    """Обрабатывает один файл."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = remove_emojis_from_text(content)
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Обновлен: {file_path}")
            return True
    except Exception as e:
        print(f"Ошибка при обработке {file_path}: {e}")
    
    return False

def main():
    """Основная функция."""
    project_root = Path('.')
    
    # Файлы для обработки
    file_patterns = ['*.py', '*.md']
    
    updated_files = []
    
    for pattern in file_patterns:
        for file_path in project_root.rglob(pattern):
            # Пропускаем файлы в venv и других служебных директориях
            if any(part.startswith('.') or part in ['venv', '__pycache__', 'node_modules'] 
                   for part in file_path.parts):
                continue
            
            if process_file(file_path):
                updated_files.append(str(file_path))
    
    print(f"\nОбработано файлов: {len(updated_files)}")
    for file_path in updated_files:
        print(f"  - {file_path}")

if __name__ == '__main__':
    main()
