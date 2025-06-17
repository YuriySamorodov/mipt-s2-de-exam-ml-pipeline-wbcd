#!/usr/bin/env python3
"""
Скрипт для удаления всех эмодзи из файлов проекта
"""

import os
import re
from pathlib import Path
import argparse

# Паттерн для поиска эмодзи
EMOJI_PATTERN = re.compile(
"["
"\U0001F600-\U0001F64F" # emoticons
"\U0001F300-\U0001F5FF" # symbols & pictographs
"\U0001F680-\U0001F6FF" # transport & map symbols
"\U0001F1E0-\U0001F1FF" # flags (iOS)
"\U00002600-\U000026FF" # miscellaneous symbols
"\U00002700-\U000027BF" # dingbats
"\U0001F900-\U0001F9FF" # Supplemental Symbols and Pictographs
"\U0001FA70-\U0001FAFF" # Symbols and Pictographs Extended-A
"\U00002B05-\U00002B07" # directional arrows
"\U000025AA-\U000025AB" # black/white small squares
"\U000025B6-\U000025C0" # play/pause symbols
"\U0001F170-\U0001F251" # enclosed characters
"]+", flags=re.UNICODE
)

# Дополнительные специфичные эмодзи, которые могут не попасть в основной паттерн
SPECIFIC_EMOJIS = [
# Технические символы
"", "", "", "", "", "", "", "", "", "", "", "", 
"", "", "", "", "", "", "", "", "️", "", "️", "",
"️", "", "", "", "", "", "", "", "", "", "️", "️",
"", "", "", "", "", "", "", "", "", "", "", "️",
"", "", "", "", "", "", "", "", "", "", "‍"
]

def clean_emoji_from_text(text):
"""Удаляет эмодзи из текста"""
# Сначала удаляем специфичные эмодзи
for emoji in SPECIFIC_EMOJIS:
text = text.replace(emoji, "")

# Затем используем регулярное выражение для остальных
text = EMOJI_PATTERN.sub("", text)

# Удаляем лишние пробелы, которые могли остаться после удаления эмодзи
text = re.sub(r" +", " ", text) # множественные пробелы заменяем одним
text = re.sub(r"^ ", "", text, flags=re.MULTILINE) # пробелы в начале строк

return text

def should_skip_file(file_path):
"""Проверяет, нужно ли пропустить файл"""
skip_patterns = [
".git",
"__pycache__",
".pyc",
".pyo",
".egg-info",
"node_modules",
"venv",
".env",
"logs",
".db",
".sqlite",
".pkl",
".jpg", ".jpeg", ".png", ".gif", ".bmp",
".mp4", ".avi", ".mov",
".zip", ".tar", ".gz",
"remove_emojis.py" # не обрабатываем сам скрипт
]

file_str = str(file_path)
for pattern in skip_patterns:
if pattern in file_str:
return True

return False

def process_file(file_path, dry_run=False):
"""Обрабатывает один файл"""
try:
# Читаем файл с разными кодировками
encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
content = None
used_encoding = None

for encoding in encodings:
try:
with open(file_path, 'r', encoding=encoding) as f:
content = f.read()
used_encoding = encoding
break
except UnicodeDecodeError:
continue

if content is None:
print(f"Не удалось прочитать файл: {file_path}")
return False

# Проверяем, есть ли эмодзи в файле
original_length = len(content)
has_emojis = False

# Проверяем специфичные эмодзи
for emoji in SPECIFIC_EMOJIS:
if emoji in content:
has_emojis = True
break

# Проверяем через регулярное выражение
if not has_emojis and EMOJI_PATTERN.search(content):
has_emojis = True

if not has_emojis:
return False

# Удаляем эмодзи
cleaned_content = clean_emoji_from_text(content)

if cleaned_content == content:
return False

print(f"Обрабатывается: {file_path}")
print(f" Размер до: {original_length} символов")
print(f" Размер после: {len(cleaned_content)} символов")
print(f" Удалено символов: {original_length - len(cleaned_content)}")

if not dry_run:
# Записываем обратно
with open(file_path, 'w', encoding=used_encoding) as f:
f.write(cleaned_content)
print(f" Сохранено с кодировкой: {used_encoding}")
else:
print(f" (пробный запуск - файл не изменен)")

return True

except Exception as e:
print(f"Ошибка при обработке {file_path}: {e}")
return False

def main():
parser = argparse.ArgumentParser(description="Удаление эмодзи из файлов проекта")
parser.add_argument("--dry-run", action="store_true", help="Пробный запуск без изменения файлов")
parser.add_argument("--path", default=".", help="Путь к директории для обработки")
args = parser.parse_args()

root_path = Path(args.path).resolve()

print(f"Начинаем удаление эмодзи из проекта: {root_path}")
if args.dry_run:
print("РЕЖИМ ПРОБНОГО ЗАПУСКА - файлы не будут изменены")
print()

processed_files = 0
total_files = 0

# Обрабатываем все файлы в проекте
for file_path in root_path.rglob("*"):
if file_path.is_file() and not should_skip_file(file_path):
total_files += 1
if process_file(file_path, args.dry_run):
processed_files += 1
print()

print(f"=== ИТОГИ ===")
print(f"Всего файлов проверено: {total_files}")
print(f"Файлов с эмодзи обработано: {processed_files}")

if args.dry_run:
print("\nЭто был пробный запуск. Для реального удаления эмодзи запустите:")
print(f"python {__file__} --path {root_path}")
else:
print("\nВсе эмодзи успешно удалены из проекта!")

if __name__ == "__main__":
main()
