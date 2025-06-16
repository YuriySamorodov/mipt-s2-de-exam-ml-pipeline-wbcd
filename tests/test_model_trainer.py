"""
Тесты для модуля обучения модели.
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

from etl.model_trainer import ModelTrainer


class TestModelTrainer(unittest.TestCase):
    """Тесты для класса ModelTrainer."""
    
    def setUp(self):
        """Настройка тестового окружения."""
        self.trainer = ModelTrainer()
        
        # Создаем тестовые данные для обучения
        np.random.seed(42)
        self.X_train = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 100),
            'feature2': np.random.normal(0, 1, 100),
            'feature3': np.random.normal(0, 1, 100)
        })
        self.y_train = np.random.choice([0, 1], 100)
        
        self.X_test = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 30),
            'feature2': np.random.normal(0, 1, 30),
            'feature3': np.random.normal(0, 1, 30)
        })
        self.y_test = np.random.choice([0, 1], 30)
    
    def test_init_models(self):
        """Тест инициализации моделей."""
        models = self.trainer._init_models()
        
        # Проверяем, что словарь моделей не пустой
        self.assertIsInstance(models, dict)
        self.assertGreater(len(models), 0)
        
        # Проверяем наличие основных моделей
        expected_models = ['random_forest', 'gradient_boosting', 'svm']
        for model_name in expected_models:
            self.assertIn(model_name, models)
    
    @patch('etl.model_trainer.cross_val_score')
    def test_train_single_model(self, mock_cv_score):
        """Тест обучения одной модели."""
        from sklearn.ensemble import RandomForestClassifier
        
        # Настраиваем мок для cross_val_score
        mock_cv_score.return_value = np.array([0.8, 0.85, 0.82, 0.87, 0.83])
        
        model = RandomForestClassifier(random_state=42)
        result = self.trainer._train_single_model(
            'test_model', model, self.X_train, self.y_train
        )
        
        # Проверяем структуру результата
        self.assertIn('model', result)
        self.assertIn('cv_scores', result)
        self.assertIn('mean_cv_score', result)
        self.assertIn('std_cv_score', result)
        
        # Проверяем, что модель обучена
        self.assertIsNotNone(result['model'])
        
        # Проверяем метрики кросс-валидации
        self.assertAlmostEqual(result['mean_cv_score'], 0.834, places=3)
    
    def test_train_models(self):
        """Тест обучения всех моделей."""
        results = self.trainer.train_models(self.X_train, self.y_train)
        
        # Проверяем, что результаты не пустые
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0)
        
        # Проверяем структуру результатов для каждой модели
        for model_name, result in results.items():
            self.assertIn('model', result)
            self.assertIn('cv_scores', result)
            self.assertIn('mean_cv_score', result)
            self.assertIn('std_cv_score', result)
    
    def test_select_best_model(self):
        """Тест выбора лучшей модели."""
        # Создаем результаты обучения
        training_results = {
            'model_a': {
                'model': MagicMock(),
                'mean_cv_score': 0.85,
                'std_cv_score': 0.02
            },
            'model_b': {
                'model': MagicMock(),
                'mean_cv_score': 0.90,  # Лучшая модель
                'std_cv_score': 0.03
            },
            'model_c': {
                'model': MagicMock(),
                'mean_cv_score': 0.82,
                'std_cv_score': 0.01
            }
        }
        
        best_model_name, best_model_info = self.trainer.select_best_model(training_results)
        
        # Проверяем, что выбрана правильная модель
        self.assertEqual(best_model_name, 'model_b')
        self.assertEqual(best_model_info['mean_cv_score'], 0.90)
    
    def test_select_best_model_empty_results(self):
        """Тест выбора лучшей модели при пустых результатах."""
        with self.assertRaises(ValueError):
            self.trainer.select_best_model({})
    
    @patch('etl.model_trainer.GridSearchCV')
    def test_hyperparameter_tuning(self, mock_grid_search):
        """Тест настройки гиперпараметров."""
        from sklearn.ensemble import RandomForestClassifier
        
        # Настраиваем мок
        mock_grid_instance = MagicMock()
        mock_grid_instance.best_estimator_ = RandomForestClassifier()
        mock_grid_instance.best_params_ = {'n_estimators': 100}
        mock_grid_instance.best_score_ = 0.90
        mock_grid_search.return_value = mock_grid_instance
        
        model = RandomForestClassifier()
        param_grid = {'n_estimators': [50, 100]}
        
        best_model, best_params, best_score = self.trainer.hyperparameter_tuning(
            model, param_grid, self.X_train, self.y_train
        )
        
        # Проверяем результаты
        self.assertIsNotNone(best_model)
        self.assertEqual(best_params, {'n_estimators': 100})
        self.assertEqual(best_score, 0.90)
        
        # Проверяем, что GridSearchCV был вызван
        mock_grid_search.assert_called_once()
    
    def test_get_feature_importance(self):
        """Тест получения важности признаков."""
        # Создаем мок модели с feature_importances_
        mock_model = MagicMock()
        mock_model.feature_importances_ = np.array([0.3, 0.5, 0.2])
        
        feature_names = ['feature1', 'feature2', 'feature3']
        
        importance_df = self.trainer.get_feature_importance(mock_model, feature_names)
        
        # Проверяем результат
        self.assertIsInstance(importance_df, pd.DataFrame)
        self.assertEqual(len(importance_df), 3)
        self.assertIn('feature', importance_df.columns)
        self.assertIn('importance', importance_df.columns)
        
        # Проверяем, что отсортировано по убыванию важности
        self.assertTrue(importance_df['importance'].is_monotonic_decreasing)
    
    def test_get_feature_importance_no_attribute(self):
        """Тест получения важности признаков для модели без этого атрибута."""
        mock_model = MagicMock()
        del mock_model.feature_importances_  # Удаляем атрибут
        
        feature_names = ['feature1', 'feature2', 'feature3']
        
        importance_df = self.trainer.get_feature_importance(mock_model, feature_names)
        
        # Проверяем, что возвращается None
        self.assertIsNone(importance_df)
    
    @patch('etl.model_trainer.joblib.dump')
    def test_save_model(self, mock_dump):
        """Тест сохранения модели."""
        mock_model = MagicMock()
        model_info = {
            'model': mock_model,
            'mean_cv_score': 0.85,
            'params': {'n_estimators': 100}
        }
        
        self.trainer.save_model(model_info, 'test_model', 'test_path')
        
        # Проверяем, что joblib.dump был вызван
        mock_dump.assert_called_once()
    
    def test_full_training_pipeline(self):
        """Тест полного пайплайна обучения."""
        result = self.trainer.train_and_select_best_model(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        
        # Проверяем структуру результата
        expected_keys = [
            'best_model_name', 'best_model', 'training_results',
            'feature_importance', 'model_comparison'
        ]
        
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Проверяем типы результатов
        self.assertIsInstance(result['training_results'], dict)
        self.assertIsInstance(result['model_comparison'], pd.DataFrame)
    
    def test_create_model_comparison_report(self):
        """Тест создания отчета сравнения моделей."""
        training_results = {
            'model_a': {
                'mean_cv_score': 0.85,
                'std_cv_score': 0.02
            },
            'model_b': {
                'mean_cv_score': 0.90,
                'std_cv_score': 0.03
            }
        }
        
        comparison_df = self.trainer._create_model_comparison_report(training_results)
        
        # Проверяем структуру
        self.assertIsInstance(comparison_df, pd.DataFrame)
        self.assertEqual(len(comparison_df), 2)
        self.assertIn('model', comparison_df.columns)
        self.assertIn('mean_cv_score', comparison_df.columns)
        self.assertIn('std_cv_score', comparison_df.columns)
        
        # Проверяем, что отсортировано по убыванию mean_cv_score
        self.assertTrue(comparison_df['mean_cv_score'].is_monotonic_decreasing)
    
    def test_get_model_params(self):
        """Тест получения параметров модели."""
        from sklearn.ensemble import RandomForestClassifier
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        params = self.trainer._get_model_params(model)
        
        # Проверяем, что параметры получены
        self.assertIsInstance(params, dict)
        self.assertIn('n_estimators', params)
        self.assertEqual(params['n_estimators'], 100)
    
    def test_validate_training_data(self):
        """Тест валидации тренировочных данных."""
        # Валидные данные
        is_valid, issues = self.trainer._validate_training_data(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)
        
        # Невалидные данные - разные размеры
        y_wrong_size = np.array([0, 1])  # Неправильный размер
        is_valid, issues = self.trainer._validate_training_data(
            self.X_train, y_wrong_size, self.X_test, self.y_test
        )
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)


if __name__ == '__main__':
    unittest.main()
