"""
Конфигурация для pytest.
"""
import sys
import os

# Добавляем корневую папку проекта в Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'etl'))
sys.path.insert(0, os.path.join(project_root, 'config'))
