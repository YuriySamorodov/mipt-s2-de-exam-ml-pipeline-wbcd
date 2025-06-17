#!/usr/bin/env python3
"""
Скрипт для исправления форматирования после удаления эмодзи
"""
import re
from pathlib import Path

def clean_formatting(text):
"""Исправляет форматирование после удаления эмодзи"""

# Удаляем лишние пробелы в заголовках
text = re.sub(r'^(#{1,6})\s+(\w)', r'\1 \2', text, flags=re.MULTILINE)

# Исправляем пустые заголовки
text = re.sub(r'^(#{1,6})\s*$', r'\1 Раздел', text, flags=re.MULTILINE)

# Удаляем лишние пробелы в начале строк с |
text = re.sub(r'^\|\s+\*\*', r'| **', text, flags=re.MULTILINE)

# Удаляем двойные пробелы
text = re.sub(r' +', ' ', text)

# Удаляем пробелы в конце строк
text = re.sub(r' +$', '', text, flags=re.MULTILINE)

return text

def process_file(file_path):
"""Обрабатывает один файл"""
try:
with open(file_path, 'r', encoding='utf-8') as f:
original_content = f.read()

cleaned_content = clean_formatting(original_content)

if cleaned_content != original_content:
with open(file_path, 'w', encoding='utf-8') as f:
f.write(cleaned_content)
print(f"Исправлен: {file_path}")
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

print("Исправление форматирования после удаления эмодзи...")

# Обрабатываем только markdown файлы
for file_path in project_root.rglob('*.md'):
# Исключаем служебные директории
if any(part.startswith('.') or part in ['venv', '__pycache__', 'node_modules', 'temp'] 
for part in file_path.parts):
continue

if process_file(file_path):
processed_count += 1

print(f"\nИсправлено файлов: {processed_count}")
print("Готово!")

if __name__ == "__main__":
main()
