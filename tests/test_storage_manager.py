"""
Тесты для модуля управления хранилищем.
"""
import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
import json

# Импорт тестируемого модуля
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.storage_manager import StorageManager


class TestStorageManager(unittest.TestCase):
    """Тесты для класса StorageManager."""
    
    def setUp(self):
        """Настройка тестового окружения."""
        self.storage = StorageManager()
        
        # Создаем тестовые данные
        self.test_metrics = {
            'accuracy': 0.85,
            'precision': 0.82,
            'recall': 0.88,
            'f1_score': 0.85
        }
        
        self.test_model_info = {
            'model_name': 'random_forest',
            'best_params': {'n_estimators': 100},
            'cv_score': 0.834,
            'timestamp': '2024-01-01 12:00:00'
        }
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('etl.storage_manager.ensure_dir')
    def test_save_metrics(self, mock_ensure_dir, mock_json_dump, mock_file):
        """Тест сохранения метрик."""
        filepath = 'test_metrics.json'
        
        self.storage.save_metrics(self.test_metrics, filepath)
        
        # Проверяем, что функции были вызваны
        mock_ensure_dir.assert_called_once()
        mock_file.assert_called_once_with(filepath, 'w', encoding='utf-8')
        mock_json_dump.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('etl.storage_manager.ensure_dir')
    def test_save_model_info(self, mock_ensure_dir, mock_json_dump, mock_file):
        """Тест сохранения информации о модели."""
        filepath = 'test_model_info.json'
        
        self.storage.save_model_info(self.test_model_info, filepath)
        
        # Проверяем, что функции были вызваны
        mock_ensure_dir.assert_called_once()
        mock_file.assert_called_once_with(filepath, 'w', encoding='utf-8')
        mock_json_dump.assert_called_once()
    
    @patch('pandas.DataFrame.to_csv')
    @patch('etl.storage_manager.ensure_dir')
    def test_save_dataframe(self, mock_ensure_dir, mock_to_csv):
        """Тест сохранения DataFrame."""
        df = pd.DataFrame({
            'feature': ['A', 'B', 'C'],
            'importance': [0.5, 0.3, 0.2]
        })
        filepath = 'test_dataframe.csv'
        
        self.storage.save_dataframe(df, filepath)
        
        # Проверяем, что функции были вызваны
        mock_ensure_dir.assert_called_once()
        mock_to_csv.assert_called_once_with(filepath, index=False, encoding='utf-8')
    
    @patch('etl.storage_manager.joblib.dump')
    @patch('etl.storage_manager.ensure_dir')
    def test_save_model(self, mock_ensure_dir, mock_joblib_dump):
        """Тест сохранения модели."""
        mock_model = MagicMock()
        filepath = 'test_model.joblib'
        
        self.storage.save_model(mock_model, filepath)
        
        # Проверяем, что функции были вызваны
        mock_ensure_dir.assert_called_once()
        mock_joblib_dump.assert_called_once_with(mock_model, filepath)
    
    @patch('etl.storage_manager.joblib.load')
    def test_load_model(self, mock_joblib_load):
        """Тест загрузки модели."""
        mock_model = MagicMock()
        mock_joblib_load.return_value = mock_model
        filepath = 'test_model.joblib'
        
        loaded_model = self.storage.load_model(filepath)
        
        # Проверяем, что модель загружена
        mock_joblib_load.assert_called_once_with(filepath)
        self.assertEqual(loaded_model, mock_model)
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"accuracy": 0.85}')
    @patch('json.load')
    def test_load_metrics(self, mock_json_load, mock_file):
        """Тест загрузки метрик."""
        mock_json_load.return_value = self.test_metrics
        filepath = 'test_metrics.json'
        
        loaded_metrics = self.storage.load_metrics(filepath)
        
        # Проверяем, что метрики загружены
        mock_file.assert_called_once_with(filepath, 'r', encoding='utf-8')
        mock_json_load.assert_called_once()
        self.assertEqual(loaded_metrics, self.test_metrics)
    
    def test_load_metrics_file_not_found(self):
        """Тест загрузки метрик при отсутствии файла."""
        with self.assertRaises(FileNotFoundError):
            self.storage.load_metrics('non_existent_file.json')
    
    @patch('pandas.read_csv')
    def test_load_dataframe(self, mock_read_csv):
        """Тест загрузки DataFrame."""
        mock_df = pd.DataFrame({'col': [1, 2, 3]})
        mock_read_csv.return_value = mock_df
        filepath = 'test_dataframe.csv'
        
        loaded_df = self.storage.load_dataframe(filepath)
        
        # Проверяем, что DataFrame загружен
        mock_read_csv.assert_called_once_with(filepath, encoding='utf-8')
        self.assertEqual(loaded_df.equals(mock_df), True)
    
    @patch('etl.storage_manager.boto3')
    def test_upload_to_s3(self, mock_boto3):
        """Тест загрузки файла в S3."""
        # Настраиваем мок
        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client
        
        local_file = 'test_file.json'
        bucket = 'test-bucket'
        s3_key = 'models/test_file.json'
        
        self.storage.upload_to_s3(local_file, bucket, s3_key)
        
        # Проверяем, что S3 клиент был создан и файл загружен
        mock_boto3.client.assert_called_once_with('s3')
        mock_s3_client.upload_file.assert_called_once_with(local_file, bucket, s3_key)
    
    @patch('etl.storage_manager.boto3')
    def test_download_from_s3(self, mock_boto3):
        """Тест скачивания файла из S3."""
        # Настраиваем мок
        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client
        
        bucket = 'test-bucket'
        s3_key = 'models/test_file.json'
        local_file = 'downloaded_file.json'
        
        self.storage.download_from_s3(bucket, s3_key, local_file)
        
        # Проверяем, что S3 клиент был создан и файл скачан
        mock_boto3.client.assert_called_once_with('s3')
        mock_s3_client.download_file.assert_called_once_with(bucket, s3_key, local_file)
    
    @patch('etl.storage_manager.storage')
    def test_upload_to_gcs(self, mock_storage):
        """Тест загрузки файла в Google Cloud Storage."""
        # Настраиваем мок
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        local_file = 'test_file.json'
        bucket = 'test-bucket'
        gcs_path = 'models/test_file.json'
        
        self.storage.upload_to_gcs(local_file, bucket, gcs_path)
        
        # Проверяем, что GCS клиент был создан и файл загружен
        mock_storage.Client.assert_called_once()
        mock_client.bucket.assert_called_once_with(bucket)
        mock_bucket.blob.assert_called_once_with(gcs_path)
        mock_blob.upload_from_filename.assert_called_once_with(local_file)
    
    @patch('etl.storage_manager.storage')
    def test_download_from_gcs(self, mock_storage):
        """Тест скачивания файла из Google Cloud Storage."""
        # Настраиваем мок
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        bucket = 'test-bucket'
        gcs_path = 'models/test_file.json'
        local_file = 'downloaded_file.json'
        
        self.storage.download_from_gcs(bucket, gcs_path, local_file)
        
        # Проверяем, что GCS клиент был создан и файл скачан
        mock_storage.Client.assert_called_once()
        mock_client.bucket.assert_called_once_with(bucket)
        mock_bucket.blob.assert_called_once_with(gcs_path)
        mock_blob.download_to_filename.assert_called_once_with(local_file)
    
    def test_create_backup_filename(self):
        """Тест создания имени файла резервной копии."""
        original_file = 'model.joblib'
        backup_name = self.storage.create_backup_filename(original_file)
        
        # Проверяем формат имени
        self.assertTrue(backup_name.startswith('model_backup_'))
        self.assertTrue(backup_name.endswith('.joblib'))
        self.assertIn('_', backup_name)
    
    @patch('shutil.copy2')
    @patch('etl.storage_manager.ensure_dir')
    def test_create_local_backup(self, mock_ensure_dir, mock_copy):
        """Тест создания локальной резервной копии."""
        source_file = 'test_model.joblib'
        backup_dir = 'backups/'
        
        backup_path = self.storage.create_local_backup(source_file, backup_dir)
        
        # Проверяем, что файл скопирован
        mock_ensure_dir.assert_called_once_with(backup_dir)
        mock_copy.assert_called_once()
        
        # Проверяем формат пути
        self.assertTrue(backup_path.startswith(backup_dir))
    
    def test_get_storage_summary(self):
        """Тест получения сводки по хранилищу."""
        # Создаем тестовые данные в временных файлах
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем тестовые файлы
            model_file = os.path.join(temp_dir, 'model.joblib')
            metrics_file = os.path.join(temp_dir, 'metrics.json')
            
            with open(model_file, 'w') as f:
                f.write('test model data')
            
            with open(metrics_file, 'w') as f:
                json.dump(self.test_metrics, f)
            
            # Получаем сводку
            summary = self.storage.get_storage_summary(temp_dir)
            
            # Проверяем структуру сводки
            self.assertIn('total_files', summary)
            self.assertIn('file_types', summary)
            self.assertIn('total_size_mb', summary)
            
            # Проверяем количество файлов
            self.assertEqual(summary['total_files'], 2)
    
    def test_cleanup_old_files(self):
        """Тест очистки старых файлов."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем тестовые файлы
            old_file = os.path.join(temp_dir, 'old_model.joblib')
            new_file = os.path.join(temp_dir, 'new_model.joblib')
            
            # Создаем файлы с разным временем создания
            with open(old_file, 'w') as f:
                f.write('old model')
            with open(new_file, 'w') as f:
                f.write('new model')
            
            # Устанавливаем время создания для старого файла
            old_time = os.path.getctime(old_file) - 86400 * 8  # 8 дней назад
            os.utime(old_file, (old_time, old_time))
            
            # Очищаем файлы старше 7 дней
            removed_files = self.storage.cleanup_old_files(temp_dir, days=7)
            
            # Проверяем, что старый файл удален
            self.assertEqual(len(removed_files), 1)
            self.assertFalse(os.path.exists(old_file))
            self.assertTrue(os.path.exists(new_file))
    
    @patch('etl.storage_manager.ensure_dir')
    def test_save_experiment_results(self, mock_ensure_dir):
        """Тест сохранения результатов эксперимента."""
        experiment_data = {
            'experiment_id': 'exp_001',
            'model_name': 'random_forest',
            'metrics': self.test_metrics,
            'parameters': {'n_estimators': 100}
        }
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json_dump:
                experiment_dir = 'experiments/'
                
                saved_path = self.storage.save_experiment_results(
                    experiment_data, experiment_dir
                )
                
                # Проверяем, что директория создана
                mock_ensure_dir.assert_called()
                
                # Проверяем, что файл сохранен
                mock_file.assert_called()
                mock_json_dump.assert_called_once_with(
                    experiment_data, mock_file(), indent=2, ensure_ascii=False
                )
                
                # Проверяем формат пути
                self.assertTrue(saved_path.startswith(experiment_dir))
                self.assertTrue(saved_path.endswith('.json'))


if __name__ == '__main__':
    unittest.main()
