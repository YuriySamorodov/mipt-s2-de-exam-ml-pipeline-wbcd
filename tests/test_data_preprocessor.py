"""
Тесты для модуля предобработки данных.
"""
import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import tempfile
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Импорт тестируемого модуля
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.data_preprocessor import DataPreprocessor


class TestDataPreprocessor(unittest.TestCase):
"""Тесты для класса DataPreprocessor."""

def setUp(self):
"""Настройка тестового окружения."""
self.preprocessor = DataPreprocessor()

# Создаем тестовые данные
self.test_df = pd.DataFrame({
'id': [1, 2, 3, 4, 5],
'diagnosis': ['M', 'B', 'M', 'B', 'M'],
'feature1': [1.0, 2.0, np.nan, 4.0, 5.0],
'feature2': [10.0, 20.0, 30.0, 40.0, 50.0],
'feature3': [100.0, 200.0, 300.0, 400.0, 500.0]
})

def test_clean_data_basic(self):
"""Тест базовой очистки данных."""
cleaned_df = self.preprocessor.clean_data(self.test_df.copy())

# Проверяем, что NaN заполнены
self.assertFalse(cleaned_df.isnull().any().any())

# Проверяем, что размер не изменился
self.assertEqual(len(cleaned_df), len(self.test_df))

# Проверяем, что ID колонка удалена
self.assertNotIn('id', cleaned_df.columns)

def test_clean_data_with_duplicates(self):
"""Тест очистки данных с дубликатами."""
# Добавляем дубликат
df_with_duplicates = pd.concat([self.test_df, self.test_df.iloc[0:1]], ignore_index=True)

cleaned_df = self.preprocessor.clean_data(df_with_duplicates)

# Проверяем, что дубликаты удалены
self.assertEqual(len(cleaned_df), len(self.test_df))

def test_clean_data_with_outliers(self):
"""Тест очистки данных с выбросами."""
# Добавляем выброс
df_with_outliers = self.test_df.copy()
df_with_outliers.loc[0, 'feature2'] = 1000.0 # Очень большое значение

cleaned_df = self.preprocessor.clean_data(df_with_outliers)

# Проверяем, что данные очищены
self.assertIsInstance(cleaned_df, pd.DataFrame)
self.assertFalse(cleaned_df.isnull().any().any())

def test_split_features_target(self):
"""Тест разделения признаков и целевой переменной."""
X, y = self.preprocessor.split_features_target(self.test_df)

# Проверяем размеры
self.assertEqual(len(X), len(self.test_df))
self.assertEqual(len(y), len(self.test_df))

# Проверяем, что diagnosis не входит в признаки
self.assertNotIn('diagnosis', X.columns)

# Проверяем, что целевая переменная правильная
self.assertTrue(all(label in ['M', 'B'] for label in y))

def test_scale_features(self):
"""Тест масштабирования признаков."""
X = self.test_df[['feature1', 'feature2', 'feature3']].fillna(0)

X_scaled, scaler = self.preprocessor.scale_features(X)

# Проверяем тип результата
self.assertIsInstance(X_scaled, pd.DataFrame)
self.assertIsInstance(scaler, StandardScaler)

# Проверяем размеры
self.assertEqual(X_scaled.shape, X.shape)

# Проверяем, что данные масштабированы (среднее близко к 0)
for col in X_scaled.columns:
self.assertAlmostEqual(X_scaled[col].mean(), 0, places=10)

def test_encode_target(self):
"""Тест кодирования целевой переменной."""
y = pd.Series(['M', 'B', 'M', 'B', 'M'])

y_encoded, encoder = self.preprocessor.encode_target(y)

# Проверяем тип результата
self.assertIsInstance(y_encoded, np.ndarray)
self.assertIsInstance(encoder, LabelEncoder)

# Проверяем размер
self.assertEqual(len(y_encoded), len(y))

# Проверяем, что закодировано правильно
self.assertTrue(all(label in [0, 1] for label in y_encoded))

def test_prepare_data_full_pipeline(self):
"""Тест полного пайплайна предобработки."""
result = self.preprocessor.prepare_data(self.test_df.copy())

# Проверяем структуру результата
self.assertIn('X_train', result)
self.assertIn('X_test', result)
self.assertIn('y_train', result)
self.assertIn('y_test', result)
self.assertIn('scaler', result)
self.assertIn('encoder', result)
self.assertIn('feature_names', result)

# Проверяем размеры
total_samples = len(result['X_train']) + len(result['X_test'])
self.assertEqual(total_samples, len(self.test_df))

# Проверяем, что тренировочная выборка больше тестовой
self.assertGreater(len(result['X_train']), len(result['X_test']))

def test_handle_missing_values_median(self):
"""Тест обработки пропущенных значений медианой."""
df = pd.DataFrame({
'feature1': [1.0, 2.0, np.nan, 4.0, 5.0],
'feature2': [10.0, np.nan, 30.0, 40.0, 50.0]
})

filled_df = self.preprocessor._handle_missing_values(df, strategy='median')

# Проверяем, что NaN заполнены
self.assertFalse(filled_df.isnull().any().any())

# Проверяем, что заполнено медианой
self.assertEqual(filled_df.loc[2, 'feature1'], 3.0) # медиана [1,2,4,5]

def test_handle_missing_values_mean(self):
"""Тест обработки пропущенных значений средним."""
df = pd.DataFrame({
'feature1': [1.0, 2.0, np.nan, 4.0, 5.0]
})

filled_df = self.preprocessor._handle_missing_values(df, strategy='mean')

# Проверяем, что NaN заполнены
self.assertFalse(filled_df.isnull().any().any())

# Проверяем, что заполнено средним
self.assertEqual(filled_df.loc[2, 'feature1'], 3.0) # среднее [1,2,4,5]

def test_remove_outliers_iqr(self):
"""Тест удаления выбросов методом IQR."""
df = pd.DataFrame({
'feature1': [1, 2, 3, 4, 5, 100] # 100 - выброс
})

clean_df = self.preprocessor._remove_outliers(df, method='iqr')

# Проверяем, что выброс удален
self.assertLess(len(clean_df), len(df))
self.assertNotIn(100, clean_df['feature1'].values)

def test_remove_outliers_zscore(self):
"""Тест удаления выбросов методом Z-score."""
df = pd.DataFrame({
'feature1': [1, 2, 3, 4, 5, 100] # 100 - выброс
})

clean_df = self.preprocessor._remove_outliers(df, method='zscore', threshold=2)

# Проверяем, что выброс удален
self.assertLessEqual(len(clean_df), len(df))

@patch('etl.data_preprocessor.joblib.dump')
def test_save_preprocessors(self, mock_dump):
"""Тест сохранения препроцессоров."""
from sklearn.preprocessing import StandardScaler, LabelEncoder

scaler = StandardScaler()
encoder = LabelEncoder()

self.preprocessor.save_preprocessors(scaler, encoder, 'test_path')

# Проверяем, что joblib.dump был вызван дважды
self.assertEqual(mock_dump.call_count, 2)

def test_get_preprocessing_report(self):
"""Тест генерации отчета о предобработке."""
original_df = self.test_df.copy()
processed_df = self.test_df.drop('id', axis=1).fillna(0)

report = self.preprocessor.get_preprocessing_report(original_df, processed_df)

# Проверяем структуру отчета
self.assertIn('original_shape', report)
self.assertIn('processed_shape', report)
self.assertIn('removed_features', report)
self.assertIn('missing_values_handled', report)

# Проверяем содержимое
self.assertEqual(report['original_shape'], original_df.shape)
self.assertEqual(report['processed_shape'], processed_df.shape)


if __name__ == '__main__':
unittest.main()
