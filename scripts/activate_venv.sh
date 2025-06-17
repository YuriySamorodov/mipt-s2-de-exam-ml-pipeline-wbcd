#!/bin/bash
# Общий скрипт для активации виртуального окружения
# Используется другими скриптами проекта

set -e

# Определяем путь к проекту
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

# Проверяем существование виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    echo "Виртуальное окружение не найдено в $VENV_DIR"
    echo "Создайте его командой: make setup"
    echo "Или выполните: python3 -m venv venv && ./venv/bin/pip install -r config/requirements.txt"
    exit 1
fi

# Активируем виртуальное окружение
source "$VENV_DIR/bin/activate"

# Проверяем, что активация прошла успешно
if [ "$VIRTUAL_ENV" != "$VENV_DIR" ]; then
    echo "Не удалось активировать виртуальное окружение"
    exit 1
fi

echo "Виртуальное окружение активировано: $VIRTUAL_ENV"

# Добавляем путь к проекту в PYTHONPATH
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Экспортируем переменные для использования в других скриптах
export PROJECT_DIR
export VENV_DIR
export VENV_PYTHON="$VENV_DIR/bin/python"
export VENV_PIP="$VENV_DIR/bin/pip"
