"""
Тесты для модуля расчета метрик.
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

from etl.metrics_calculator import MetricsCalculator


class TestMetricsCalculator(unittest.TestCase):
    """Тесты для класса MetricsCalculator."""
    
    def setUp(self):
        """Настройка тестового окружения."""
        self.calculator = MetricsCalculator()
        
        # Создаем тестовые данные
        self.y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 0])
        self.y_pred = np.array([1, 0, 1, 0, 0, 1, 0, 1, 1, 0])
        self.y_pred_proba = np.array([0.9, 0.1, 0.8, 0.4, 0.2, 0.7, 0.3, 0.6, 0.85, 0.15])
        
        # Создаем мок модели
        self.mock_model = MagicMock()
        self.mock_model.predict.return_value = self.y_pred
        self.mock_model.predict_proba.return_value = np.column_stack([
            1 - self.y_pred_proba, self.y_pred_proba
        ])
    
    def test_calculate_classification_metrics(self):
        """Тест расчета метрик классификации."""
        metrics = self.calculator.calculate_classification_metrics(self.y_true, self.y_pred)
        
        # Проверяем наличие всех основных метрик
        expected_metrics = [
            'accuracy', 'precision', 'recall', 'f1_score',
            'roc_auc', 'confusion_matrix', 'classification_report'
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
        
        # Проверяем типы метрик
        self.assertIsInstance(metrics['accuracy'], float)
        self.assertIsInstance(metrics['precision'], float)
        self.assertIsInstance(metrics['recall'], float)
        self.assertIsInstance(metrics['f1_score'], float)
        
        # Проверяем диапазоны метрик
        self.assertGreaterEqual(metrics['accuracy'], 0.0)
        self.assertLessEqual(metrics['accuracy'], 1.0)
        self.assertGreaterEqual(metrics['precision'], 0.0)
        self.assertLessEqual(metrics['precision'], 1.0)
        self.assertGreaterEqual(metrics['recall'], 0.0)
        self.assertLessEqual(metrics['recall'], 1.0)
        self.assertGreaterEqual(metrics['f1_score'], 0.0)
        self.assertLessEqual(metrics['f1_score'], 1.0)
    
    def test_calculate_classification_metrics_with_proba(self):
        """Тест расчета метрик с вероятностями."""
        metrics = self.calculator.calculate_classification_metrics(
            self.y_true, self.y_pred, self.y_pred_proba
        )
        
        # Проверяем, что ROC AUC рассчитан
        self.assertIn('roc_auc', metrics)
        self.assertIsInstance(metrics['roc_auc'], float)
        self.assertGreaterEqual(metrics['roc_auc'], 0.0)
        self.assertLessEqual(metrics['roc_auc'], 1.0)
    
    def test_evaluate_model(self):
        """Тест оценки модели."""
        X_test = np.random.random((10, 5))
        
        metrics = self.calculator.evaluate_model(
            self.mock_model, X_test, self.y_true
        )
        
        # Проверяем, что метрики рассчитаны
        self.assertIsInstance(metrics, dict)
        self.assertIn('accuracy', metrics)
        
        # Проверяем, что методы модели были вызваны
        self.mock_model.predict.assert_called_once_with(X_test)
    
    def test_calculate_feature_importance_metrics(self):
        """Тест расчета метрик важности признаков."""
        feature_importance = pd.DataFrame({
            'feature': ['feature1', 'feature2', 'feature3'],
            'importance': [0.5, 0.3, 0.2]
        })
        
        metrics = self.calculator.calculate_feature_importance_metrics(feature_importance)
        
        # Проверяем структуру результата
        self.assertIn('total_features', metrics)
        self.assertIn('top_features', metrics)
        self.assertIn('importance_distribution', metrics)
        
        # Проверяем значения
        self.assertEqual(metrics['total_features'], 3)
        self.assertIn('feature1', str(metrics['top_features']))
    
    def test_calculate_cross_validation_metrics(self):
        """Тест расчета метрик кросс-валидации."""
        cv_scores = np.array([0.8, 0.85, 0.82, 0.87, 0.83])
        
        cv_metrics = self.calculator.calculate_cross_validation_metrics(cv_scores)
        
        # Проверяем структуру результата
        expected_keys = ['mean_score', 'std_score', 'min_score', 'max_score', 'scores']
        for key in expected_keys:
            self.assertIn(key, cv_metrics)
        
        # Проверяем значения
        self.assertAlmostEqual(cv_metrics['mean_score'], 0.834, places=3)
        self.assertGreater(cv_metrics['std_score'], 0)
        self.assertEqual(cv_metrics['min_score'], 0.8)
        self.assertEqual(cv_metrics['max_score'], 0.87)
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    def test_create_confusion_matrix_plot(self, mock_figure, mock_savefig):
        """Тест создания графика матрицы ошибок."""
        confusion_matrix = np.array([[4, 1], [2, 3]])
        
        self.calculator.create_confusion_matrix_plot(
            confusion_matrix, 'test_plot.png'
        )
        
        # Проверяем, что matplotlib функции были вызваны
        mock_figure.assert_called_once()
        mock_savefig.assert_called_once_with('test_plot.png', dpi=300, bbox_inches='tight')
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    def test_create_roc_curve_plot(self, mock_figure, mock_savefig):
        """Тест создания графика ROC кривой."""
        self.calculator.create_roc_curve_plot(
            self.y_true, self.y_pred_proba, 'test_roc.png'
        )
        
        # Проверяем, что matplotlib функции были вызваны
        mock_figure.assert_called_once()
        mock_savefig.assert_called_once_with('test_roc.png', dpi=300, bbox_inches='tight')
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    def test_create_feature_importance_plot(self, mock_figure, mock_savefig):
        """Тест создания графика важности признаков."""
        feature_importance = pd.DataFrame({
            'feature': ['feature1', 'feature2', 'feature3'],
            'importance': [0.5, 0.3, 0.2]
        })
        
        self.calculator.create_feature_importance_plot(
            feature_importance, 'test_importance.png'
        )
        
        # Проверяем, что matplotlib функции были вызваны
        mock_figure.assert_called_once()
        mock_savefig.assert_called_once_with(
            'test_importance.png', dpi=300, bbox_inches='tight'
        )
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    def test_create_learning_curve_plot(self, mock_figure, mock_savefig):
        """Тест создания графика кривой обучения."""
        train_sizes = np.array([10, 20, 30, 40, 50])
        train_scores = np.array([[0.7, 0.75, 0.8], [0.72, 0.77, 0.82],
                                [0.74, 0.79, 0.84], [0.76, 0.81, 0.86],
                                [0.78, 0.83, 0.88]])
        test_scores = np.array([[0.68, 0.73, 0.78], [0.7, 0.75, 0.8],
                               [0.72, 0.77, 0.82], [0.74, 0.79, 0.84],
                               [0.76, 0.81, 0.86]])
        
        self.calculator.create_learning_curve_plot(
            train_sizes, train_scores, test_scores, 'test_learning.png'
        )
        
        # Проверяем, что matplotlib функции были вызваны
        mock_figure.assert_called_once()
        mock_savefig.assert_called_once_with(
            'test_learning.png', dpi=300, bbox_inches='tight'
        )
    
    def test_generate_comprehensive_report(self):
        """Тест генерации комплексного отчета."""
        metrics = {
            'accuracy': 0.85,
            'precision': 0.82,
            'recall': 0.88,
            'f1_score': 0.85,
            'roc_auc': 0.90
        }
        
        feature_importance = pd.DataFrame({
            'feature': ['feature1', 'feature2'],
            'importance': [0.6, 0.4]
        })
        
        cv_metrics = {
            'mean_score': 0.834,
            'std_score': 0.025
        }
        
        report = self.calculator.generate_comprehensive_report(
            metrics, feature_importance, cv_metrics
        )
        
        # Проверяем структуру отчета
        self.assertIn('model_performance', report)
        self.assertIn('feature_analysis', report)
        self.assertIn('cross_validation', report)
        self.assertIn('summary', report)
        
        # Проверяем содержимое
        self.assertEqual(report['model_performance']['accuracy'], 0.85)
        self.assertEqual(report['cross_validation']['mean_score'], 0.834)
    
    def test_calculate_business_metrics(self):
        """Тест расчета бизнес-метрик."""
        # Для медицинской диагностики
        metrics = self.calculator.calculate_business_metrics(
            self.y_true, self.y_pred, domain='medical'
        )
        
        # Проверяем специфические медицинские метрики
        self.assertIn('sensitivity', metrics)  # Чувствительность
        self.assertIn('specificity', metrics)  # Специфичность
        self.assertIn('false_positive_rate', metrics)
        self.assertIn('false_negative_rate', metrics)
        
        # Проверяем диапазоны
        for metric_name in ['sensitivity', 'specificity']:
            self.assertGreaterEqual(metrics[metric_name], 0.0)
            self.assertLessEqual(metrics[metric_name], 1.0)
    
    def test_save_metrics_report(self):
        """Тест сохранения отчета метрик."""
        metrics = {'accuracy': 0.85, 'precision': 0.82}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            self.calculator.save_metrics_report(metrics, temp_file)
            
            # Проверяем, что файл создан
            self.assertTrue(os.path.exists(temp_file))
            
            # Проверяем содержимое
            with open(temp_file, 'r') as f:
                import json
                saved_metrics = json.load(f)
                self.assertEqual(saved_metrics['accuracy'], 0.85)
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_compare_models_metrics(self):
        """Тест сравнения метрик моделей."""
        model_results = {
            'model_a': {'accuracy': 0.85, 'f1_score': 0.82},
            'model_b': {'accuracy': 0.88, 'f1_score': 0.86},
            'model_c': {'accuracy': 0.82, 'f1_score': 0.79}
        }
        
        comparison = self.calculator.compare_models_metrics(model_results)
        
        # Проверяем структуру сравнения
        self.assertIsInstance(comparison, pd.DataFrame)
        self.assertIn('model', comparison.columns)
        self.assertIn('accuracy', comparison.columns)
        self.assertIn('f1_score', comparison.columns)
        
        # Проверяем количество моделей
        self.assertEqual(len(comparison), 3)


if __name__ == '__main__':
    unittest.main()
