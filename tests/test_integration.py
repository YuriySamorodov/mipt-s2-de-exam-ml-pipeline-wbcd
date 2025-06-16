"""
Интеграционные тесты для полного ML пайплайна.
"""
import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import tempfile
import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.data_loader import DataLoader
from etl.data_preprocessor import DataPreprocessor
from etl.model_trainer import ModelTrainer
from etl.metrics_calculator import MetricsCalculator
from etl.storage_manager import StorageManager


class TestMLPipelineIntegration(unittest.TestCase):
    """Интеграционные тесты для ML пайплайна."""
    
    def setUp(self):
        """Настройка тестового окружения."""
        # Создаем тестовые данные в формате Wisconsin Breast Cancer Dataset
        self.test_data_content = [
            "842302,M,17.99,10.38,122.8,1001,0.1184,0.2776,0.3001,0.1471,0.2419,0.07871,1.095,0.9053,8.589,153.4,0.006399,0.04904,0.05373,0.01587,0.03003,0.006193,25.38,17.33,184.6,2019,0.1622,0.6656,0.7119,0.2654,0.4601,0.1189",
            "842517,M,20.57,17.77,132.9,1326,0.08474,0.07864,0.0869,0.07017,0.1812,0.05667,0.5435,0.7339,3.398,74.08,0.005225,0.01308,0.0186,0.0134,0.01389,0.003532,24.99,23.41,158.8,1956,0.1238,0.1866,0.2416,0.186,0.275,0.08902",
            "84300903,M,19.69,21.25,130,1203,0.1096,0.1599,0.1974,0.1279,0.2069,0.05999,0.7456,0.7869,4.585,94.03,0.00615,0.04006,0.03832,0.02058,0.0225,0.004571,23.57,25.53,152.5,1709,0.1444,0.4245,0.4504,0.243,0.3613,0.08758",
            "84348301,M,11.42,20.38,77.58,386.1,0.1425,0.2839,0.2414,0.1052,0.2597,0.09744,0.4956,1.156,3.445,27.23,0.00911,0.07458,0.05661,0.01867,0.05963,0.009208,14.91,26.5,98.87,567.7,0.2098,0.8663,0.6869,0.2575,0.6638,0.173",
            "84358402,M,20.29,14.34,135.1,1297,0.1003,0.1328,0.198,0.1043,0.1809,0.05883,0.7572,0.7813,5.438,94.44,0.01149,0.02461,0.05688,0.01885,0.01756,0.005115,22.54,16.67,152.2,1575,0.1374,0.205,0.4,0.1625,0.2364,0.07678",
            "843786,M,12.45,15.7,82.57,477.1,0.1278,0.17,0.1578,0.08089,0.2087,0.07613,0.3345,0.8902,2.217,27.19,0.00751,0.03345,0.03672,0.01137,0.02165,0.005082,15.47,23.75,103.4,741.6,0.1791,0.5249,0.5355,0.1741,0.3985,0.1244",
            "844359,M,18.25,19.98,119.6,1040,0.09463,0.109,0.1127,0.074,0.1794,0.05742,0.4467,0.7732,3.18,53.91,0.004314,0.01382,0.02254,0.01039,0.01369,0.002179,22.88,27.66,153.2,1606,0.1442,0.2576,0.3784,0.1932,0.3063,0.08368",
            "84458202,M,13.71,20.83,90.2,577.9,0.1189,0.1645,0.09366,0.05985,0.2196,0.07451,0.5835,1.377,3.856,50.96,0.008805,0.03029,0.02488,0.01448,0.01486,0.005412,17.06,28.14,110.6,897,0.1654,0.3682,0.2678,0.1556,0.3196,0.1151",
            "844981,M,13,21.82,87.5,519.8,0.1273,0.1932,0.1859,0.09353,0.235,0.07389,0.3063,1.002,2.406,24.32,0.005731,0.03502,0.03553,0.01226,0.02143,0.003749,15.49,30.73,106.2,739.3,0.1703,0.5401,0.539,0.206,0.4378,0.1072",
            "84501001,M,12.46,24.04,83.97,475.9,0.1186,0.2396,0.2273,0.08543,0.203,0.08243,0.2976,1.599,2.039,23.94,0.007149,0.07013,0.05186,0.01853,0.03344,0.005259,15.09,40.68,97.65,711.4,0.1853,1.058,1.105,0.221,0.4366,0.2075",
            # Добавляем несколько доброкачественных случаев
            "8510426,B,13.54,14.36,87.46,566.3,0.09779,0.08129,0.06664,0.04781,0.1885,0.05766,0.2699,0.7886,2.058,23.56,0.008462,0.0146,0.02387,0.01315,0.0198,0.0023,15.11,19.26,99.7,711.2,0.144,0.1773,0.239,0.1288,0.2977,0.07259",
            "8510653,B,13.08,15.71,85.63,520,0.1075,0.127,0.04568,0.0311,0.1967,0.06811,0.1852,0.7477,1.383,14.67,0.004097,0.01898,0.01698,0.00649,0.01678,0.002425,14.5,20.49,96.09,630.5,0.1312,0.2776,0.189,0.07283,0.3184,0.08183",
            "8510824,B,9.504,12.44,60.34,273.9,0.1024,0.06492,0.02956,0.02076,0.1815,0.06905,0.2773,0.9768,1.909,15.7,0.009606,0.01432,0.01985,0.01421,0.02027,0.002968,10.23,15.66,65.13,314.9,0.1324,0.1148,0.08867,0.06227,0.245,0.07773",
            "851509,B,12.25,17.94,78.61,457.8,0.08748,0.08134,0.04097,0.03265,0.1867,0.06086,0.2273,0.6329,1.52,17.47,0.003595,0.01195,0.01543,0.008476,0.01946,0.002194,13.45,21.9,86.18,555.1,0.1059,0.1267,0.0983,0.05956,0.2685,0.06859",
            "851860,B,11.76,21.6,74.72,427.9,0.08637,0.04966,0.01657,0.01115,0.1495,0.05888,0.4062,1.21,2.635,28.47,0.005857,0.009758,0.01168,0.007445,0.02406,0.001769,12.98,25.72,82.98,516.5,0.1085,0.08615,0.05523,0.03715,0.2433,0.06563"
        ]
        
        # Создаем временный файл с данными
        self.temp_file = None
        self._create_temp_data_file()
        
        # Создаем временную директорию для результатов
        self.temp_dir = tempfile.mkdtemp()
        
        # Инициализируем компоненты пайплайна
        self.loader = DataLoader()
        self.preprocessor = DataPreprocessor()
        self.trainer = ModelTrainer()
        self.metrics_calculator = MetricsCalculator()
        self.storage_manager = StorageManager()
    
    def _create_temp_data_file(self):
        """Создает временный файл с тестовыми данными."""
        fd, self.temp_file = tempfile.mkstemp(suffix='.csv')
        with os.fdopen(fd, 'w') as f:
            for line in self.test_data_content:
                f.write(line + '\n')
    
    def tearDown(self):
        """Очистка после тестов."""
        if self.temp_file and os.path.exists(self.temp_file):
            os.unlink(self.temp_file)
        
        # Очищаем временную директорию
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_data_loading_pipeline(self):
        """Тест пайплайна загрузки данных."""
        # Загружаем данные
        df = self.loader.load_data(self.temp_file)
        
        # Проверяем загрузку
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        self.assertEqual(len(df.columns), 32)  # 32 колонки в датасете
        
        # Анализируем данные
        analysis = self.loader.analyze_data(df)
        self.assertIn('shape', analysis)
        self.assertIn('target_distribution', analysis)
        
        # Валидируем данные
        is_valid, issues = self.loader.validate_data(df)
        self.assertTrue(is_valid, f"Данные не прошли валидацию: {issues}")
    
    def test_preprocessing_pipeline(self):
        """Тест пайплайна предобработки данных."""
        # Загружаем данные
        df = self.loader.load_data(self.temp_file)
        
        # Предобрабатываем
        preprocessed_data = self.preprocessor.prepare_data(df)
        
        # Проверяем структуру результата
        required_keys = ['X_train', 'X_test', 'y_train', 'y_test', 'scaler', 'encoder', 'feature_names']
        for key in required_keys:
            self.assertIn(key, preprocessed_data)
        
        # Проверяем размеры данных
        X_train, X_test = preprocessed_data['X_train'], preprocessed_data['X_test']
        y_train, y_test = preprocessed_data['y_train'], preprocessed_data['y_test']
        
        self.assertEqual(len(X_train), len(y_train))
        self.assertEqual(len(X_test), len(y_test))
        self.assertGreater(len(X_train), len(X_test))  # Тренировочная выборка больше
        
        # Проверяем, что данные масштабированы
        self.assertAlmostEqual(X_train.mean().mean(), 0, places=1)
    
    def test_model_training_pipeline(self):
        """Тест пайплайна обучения модели."""
        # Загружаем и предобрабатываем данные
        df = self.loader.load_data(self.temp_file)
        preprocessed_data = self.preprocessor.prepare_data(df)
        
        X_train = preprocessed_data['X_train']
        y_train = preprocessed_data['y_train']
        X_test = preprocessed_data['X_test']
        y_test = preprocessed_data['y_test']
        
        # Обучаем модели (ограничиваем количество для скорости)
        with patch.object(self.trainer, '_init_models') as mock_init:
            # Используем только одну быструю модель для теста
            from sklearn.tree import DecisionTreeClassifier
            mock_init.return_value = {
                'decision_tree': DecisionTreeClassifier(random_state=42, max_depth=3)
            }
            
            training_results = self.trainer.train_models(X_train, y_train)
        
        # Проверяем результаты обучения
        self.assertIsInstance(training_results, dict)
        self.assertGreater(len(training_results), 0)
        
        # Выбираем лучшую модель
        best_model_name, best_model_info = self.trainer.select_best_model(training_results)
        self.assertIsNotNone(best_model_name)
        self.assertIn('model', best_model_info)
        
        # Проверяем, что модель может делать предсказания
        model = best_model_info['model']
        predictions = model.predict(X_test)
        self.assertEqual(len(predictions), len(y_test))
    
    def test_metrics_calculation_pipeline(self):
        """Тест пайплайна расчета метрик."""
        # Подготавливаем данные
        df = self.loader.load_data(self.temp_file)
        preprocessed_data = self.preprocessor.prepare_data(df)
        
        X_test = preprocessed_data['X_test']
        y_test = preprocessed_data['y_test']
        
        # Создаем простую модель для тестирования
        from sklearn.tree import DecisionTreeClassifier
        model = DecisionTreeClassifier(random_state=42, max_depth=3)
        model.fit(preprocessed_data['X_train'], preprocessed_data['y_train'])
        
        # Рассчитываем метрики
        metrics = self.metrics_calculator.evaluate_model(model, X_test, y_test)
        
        # Проверяем основные метрики
        expected_metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
            self.assertIsInstance(metrics[metric], (int, float))
            self.assertGreaterEqual(metrics[metric], 0.0)
            self.assertLessEqual(metrics[metric], 1.0)
    
    def test_storage_pipeline(self):
        """Тест пайплайна сохранения результатов."""
        # Подготавливаем тестовые данные
        test_metrics = {
            'accuracy': 0.85,
            'precision': 0.82,
            'recall': 0.88,
            'f1_score': 0.85
        }
        
        test_model_info = {
            'model_name': 'test_model',
            'parameters': {'max_depth': 3},
            'cv_score': 0.83
        }
        
        # Пути для сохранения
        metrics_path = os.path.join(self.temp_dir, 'metrics.json')
        model_info_path = os.path.join(self.temp_dir, 'model_info.json')
        
        # Сохраняем данные
        self.storage_manager.save_metrics(test_metrics, metrics_path)
        self.storage_manager.save_model_info(test_model_info, model_info_path)
        
        # Проверяем, что файлы созданы
        self.assertTrue(os.path.exists(metrics_path))
        self.assertTrue(os.path.exists(model_info_path))
        
        # Загружаем и проверяем данные
        loaded_metrics = self.storage_manager.load_metrics(metrics_path)
        loaded_model_info = self.storage_manager.load_metrics(model_info_path)  # Используем тот же метод
        
        self.assertEqual(loaded_metrics['accuracy'], 0.85)
        self.assertEqual(loaded_model_info['model_name'], 'test_model')
    
    def test_full_pipeline_integration(self):
        """Тест полной интеграции всех компонентов пайплайна."""
        # Этап 1: Загрузка данных
        df = self.loader.load_data(self.temp_file)
        self.assertGreater(len(df), 0)
        
        # Этап 2: Предобработка
        preprocessed_data = self.preprocessor.prepare_data(df)
        X_train = preprocessed_data['X_train']
        y_train = preprocessed_data['y_train']
        X_test = preprocessed_data['X_test']
        y_test = preprocessed_data['y_test']
        
        # Этап 3: Обучение модели (используем быструю модель)
        from sklearn.tree import DecisionTreeClassifier
        model = DecisionTreeClassifier(random_state=42, max_depth=3)
        model.fit(X_train, y_train)
        
        # Этап 4: Расчет метрик
        metrics = self.metrics_calculator.evaluate_model(model, X_test, y_test)
        
        # Этап 5: Сохранение результатов
        metrics_path = os.path.join(self.temp_dir, 'final_metrics.json')
        model_path = os.path.join(self.temp_dir, 'final_model.joblib')
        
        self.storage_manager.save_metrics(metrics, metrics_path)
        self.storage_manager.save_model(model, model_path)
        
        # Проверяем конечные результаты
        self.assertTrue(os.path.exists(metrics_path))
        self.assertTrue(os.path.exists(model_path))
        
        # Загружаем и проверяем сохраненные данные
        loaded_metrics = self.storage_manager.load_metrics(metrics_path)
        loaded_model = self.storage_manager.load_model(model_path)
        
        # Проверяем, что загруженная модель работает
        test_predictions = loaded_model.predict(X_test[:5])  # Тестируем на 5 образцах
        self.assertEqual(len(test_predictions), 5)
        
        # Проверяем качество метрик
        self.assertGreaterEqual(loaded_metrics['accuracy'], 0.5)  # Как минимум лучше случайного
        
        print(f"Интеграционный тест завершен успешно!")
        print(f"Accuracy: {loaded_metrics['accuracy']:.3f}")
        print(f"F1-score: {loaded_metrics['f1_score']:.3f}")
    
    def test_pipeline_error_handling(self):
        """Тест обработки ошибок в пайплайне."""
        # Тест с некорректным файлом данных
        with self.assertRaises(FileNotFoundError):
            self.loader.load_data('non_existent_file.csv')
        
        # Тест с пустым DataFrame
        empty_df = pd.DataFrame()
        is_valid, issues = self.loader.validate_data(empty_df)
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        
        # Тест с некорректными размерами данных для обучения
        X_wrong = np.array([[1, 2], [3, 4]])
        y_wrong = np.array([1])  # Неправильный размер
        
        is_valid, issues = self.trainer._validate_training_data(
            X_wrong, y_wrong, X_wrong, y_wrong
        )
        self.assertFalse(is_valid)
    
    def test_pipeline_performance(self):
        """Тест производительности пайплайна."""
        import time
        
        start_time = time.time()
        
        # Выполняем основные этапы пайплайна
        df = self.loader.load_data(self.temp_file)
        preprocessed_data = self.preprocessor.prepare_data(df)
        
        # Используем быструю модель
        from sklearn.tree import DecisionTreeClassifier
        model = DecisionTreeClassifier(random_state=42, max_depth=3)
        model.fit(preprocessed_data['X_train'], preprocessed_data['y_train'])
        
        metrics = self.metrics_calculator.evaluate_model(
            model, preprocessed_data['X_test'], preprocessed_data['y_test']
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Проверяем, что пайплайн выполняется за разумное время (менее 30 секунд)
        self.assertLess(execution_time, 30.0)
        print(f"Время выполнения пайплайна: {execution_time:.2f} секунд")


if __name__ == '__main__':
    unittest.main()
