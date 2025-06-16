"""
Тесты для модуля загрузки данных.
"""
import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import tempfile
import os

# Импорт тестируемого модуля
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.data_loader import DataLoader


class TestDataLoader(unittest.TestCase):
    """Тесты для класса DataLoader."""
    
    def setUp(self):
        """Настройка тестового окружения."""
        self.loader = DataLoader()
        
        # Создаем тестовые данные
        self.test_data = [
            "842302,M,17.99,10.38,122.8,1001,0.1184,0.2776,0.3001,0.1471,0.2419,0.07871,1.095,0.9053,8.589,153.4,0.006399,0.04904,0.05373,0.01587,0.03003,0.006193,25.38,17.33,184.6,2019,0.1622,0.6656,0.7119,0.2654,0.4601,0.1189",
            "842517,M,20.57,17.77,132.9,1326,0.08474,0.07864,0.0869,0.07017,0.1812,0.05667,0.5435,0.7339,3.398,74.08,0.005225,0.01308,0.0186,0.0134,0.01389,0.003532,24.99,23.41,158.8,1956,0.1238,0.1866,0.2416,0.186,0.275,0.08902",
            "8510426,B,13.54,14.36,87.46,566.3,0.09779,0.08129,0.06664,0.04781,0.1885,0.05766,0.2699,0.7886,2.058,23.56,0.008462,0.0146,0.02387,0.01315,0.0198,0.0023,15.11,19.26,99.7,711.2,0.144,0.1773,0.239,0.1288,0.2977,0.07259"
        ]
    
    def test_load_data_success(self):
        """Тест успешной загрузки данных."""
        # Создаем временный файл с тестовыми данными
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            for line in self.test_data:
                f.write(line + '\n')
            temp_file = f.name
        
        try:
            # Тестируем загрузку
            df = self.loader.load_data(temp_file)
            
            # Проверяем результат
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(len(df), 3)
            self.assertEqual(len(df.columns), 32)  # 32 колонки в датасете
            self.assertIn('diagnosis', df.columns)
            self.assertIn('id', df.columns)
            
        finally:
            # Удаляем временный файл
            os.unlink(temp_file)
    
    def test_load_data_file_not_found(self):
        """Тест обработки отсутствующего файла."""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_data('non_existent_file.csv')
    
    def test_analyze_data(self):
        """Тест анализа данных."""
        # Создаем тестовый DataFrame
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'diagnosis': ['M', 'B', 'M'],
            'feature1': [1.0, 2.0, 3.0],
            'feature2': [4.0, np.nan, 6.0]
        })
        
        analysis = self.loader.analyze_data(df)
        
        # Проверяем результат анализа
        self.assertIn('shape', analysis)
        self.assertIn('columns', analysis)
        self.assertIn('missing_values', analysis)
        self.assertIn('target_distribution', analysis)
        
        self.assertEqual(analysis['shape'], (3, 4))
        self.assertEqual(analysis['missing_values']['feature2'], 1)
        self.assertEqual(analysis['target_distribution']['M'], 2)
        self.assertEqual(analysis['target_distribution']['B'], 1)
    
    def test_validate_data_success(self):
        """Тест успешной валидации данных."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'diagnosis': ['M', 'B', 'M'],
            'feature1': [1.0, 2.0, 3.0]
        })
        
        is_valid, issues = self.loader.validate_data(df)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)
    
    def test_validate_data_empty_dataset(self):
        """Тест валидации пустого датасета."""
        df = pd.DataFrame()
        
        is_valid, issues = self.loader.validate_data(df)
        
        self.assertFalse(is_valid)
        self.assertIn("Датасет пустой", issues)
    
    def test_validate_data_missing_columns(self):
        """Тест валидации при отсутствии обязательных колонок."""
        df = pd.DataFrame({
            'feature1': [1.0, 2.0, 3.0]
        })
        
        is_valid, issues = self.loader.validate_data(df)
        
        self.assertFalse(is_valid)
        self.assertTrue(any("Отсутствуют обязательные колонки" in issue for issue in issues))
    
    def test_validate_data_duplicate_ids(self):
        """Тест валидации при дублированных ID."""
        df = pd.DataFrame({
            'id': [1, 1, 2],
            'diagnosis': ['M', 'B', 'M'],
            'feature1': [1.0, 2.0, 3.0]
        })
        
        is_valid, issues = self.loader.validate_data(df)
        
        self.assertFalse(is_valid)
        self.assertTrue(any("дублированных ID" in issue for issue in issues))
    
    def test_validate_data_invalid_diagnosis(self):
        """Тест валидации при неверных значениях диагноза."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'diagnosis': ['M', 'X', 'B'],  # X - неверное значение
            'feature1': [1.0, 2.0, 3.0]
        })
        
        is_valid, issues = self.loader.validate_data(df)
        
        self.assertFalse(is_valid)
        self.assertTrue(any("Неизвестные значения в diagnosis" in issue for issue in issues))
    
    @patch('etl.data_loader.ensure_dir')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_save_analysis_report(self, mock_json_dump, mock_open, mock_ensure_dir):
        """Тест сохранения отчета анализа."""
        analysis = {
            'shape': (100, 32),
            'missing_values': {'feature1': 0},
            'dtypes': {'feature1': 'float64'}
        }
        
        self.loader.save_analysis_report(analysis, 'test_report.json')
        
        # Проверяем, что функции были вызваны
        mock_ensure_dir.assert_called_once()
        mock_open.assert_called_once_with('test_report.json', 'w', encoding='utf-8')
        mock_json_dump.assert_called_once()
    
    def test_get_default_columns(self):
        """Тест получения стандартных имен колонок."""
        columns = self.loader._get_default_columns(32)
        
        self.assertEqual(len(columns), 32)
        self.assertEqual(columns[0], 'id')
        self.assertEqual(columns[1], 'diagnosis')
        self.assertIn('radius_mean', columns)
        self.assertIn('texture_mean', columns)
        
        # Тест для количества колонок меньше стандартного
        columns_short = self.loader._get_default_columns(5)
        self.assertEqual(len(columns_short), 5)
        
        # Тест для количества колонок больше стандартного
        columns_long = self.loader._get_default_columns(35)
        self.assertEqual(len(columns_long), 35)
        self.assertIn('feature_32', columns_long)


if __name__ == '__main__':
    unittest.main()
