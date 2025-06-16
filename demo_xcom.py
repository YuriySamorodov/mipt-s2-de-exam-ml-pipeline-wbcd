#!/usr/bin/env python3
"""
Демонстрация работы XCom интеграции в Airflow DAG.
Показывает, как данные передаются между задачами через XCom.

Автор: Самородов Юрий Сергеевич, МФТИ
"""

import os
import sys

# Добавляем пути к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'etl'))

from datetime import datetime
import pandas as pd
import numpy as np

# Импорты ETL модулей
from etl.data_loader import DataLoader
from etl.data_preprocessor import DataPreprocessor
from etl.model_trainer import ModelTrainer
from etl.metrics_calculator import MetricsCalculator
from config.config_utils import get_logger

logger = get_logger(__name__)


def demo_xcom_pipeline():
    """
    Демонстрирует, как работает передача данных через XCom в реальном пайплайне.
    """
    print(" === ДЕМОНСТРАЦИЯ XCOM ИНТЕГРАЦИИ ===")
    
    # Имитируем контекст Airflow XCom
    xcom_data = {}
    
    def xcom_push(key, value):
        """Имитация XCom push"""
        xcom_data[key] = value
        print(f" XCom PUSH: {key} -> {type(value).__name__}")
    
    def xcom_pull(key):
        """Имитация XCom pull"""
        value = xcom_data.get(key)
        print(f" XCom PULL: {key} -> {type(value).__name__ if value is not None else 'None'}")
        return value
    
    try:
        # === ЭТАП 1: ЗАГРУЗКА И ВАЛИДАЦИЯ ДАННЫХ ===
        print("\n1⃣ === ЗАГРУЗКА И ВАЛИДАЦИЯ ДАННЫХ ===")
        
        loader = DataLoader()
        df = loader.load_data()
        print(f" Загружено данных: {df.shape}")
        
        # Анализируем данные
        analysis = loader.analyze_data(df)
        is_valid, issues = loader.validate_data(df)
        
        # Подготавливаем данные для XCom
        raw_data_dict = {
            'data': df.to_dict('records'),
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'shape': df.shape,
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        # Передаем через XCom
        xcom_push('raw_data', raw_data_dict)
        xcom_push('data_analysis', analysis)
        xcom_push('validation_results', {'is_valid': is_valid, 'issues': issues})
        
        print(f" Размер данных в XCom: {len(str(raw_data_dict))} символов")
        
        # === ЭТАП 2: ПРЕДОБРАБОТКА ДАННЫХ ===
        print("\n2⃣ === ПРЕДОБРАБОТКА ДАННЫХ ===")
        
        # Получаем данные из XCom
        raw_data_from_xcom = xcom_pull('raw_data')
        if raw_data_from_xcom is None:
            raise ValueError("Данные не найдены в XCom!")
        
        # Восстанавливаем DataFrame
        df_restored = pd.DataFrame(raw_data_from_xcom['data'])
        df_restored = df_restored.astype(raw_data_from_xcom['dtypes'])
        print(f" Восстановлены данные из XCom: {df_restored.shape}")
        
        # Предобрабатываем
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test = preprocessor.preprocess_pipeline(df_restored)
        
        # Подготавливаем обработанные данные для XCom
        processed_data = {
            'X_train': X_train.tolist(),
            'X_test': X_test.tolist(),
            'y_train': y_train.tolist(),
            'y_test': y_test.tolist(),
            'feature_names': X_train.columns.tolist() if hasattr(X_train, 'columns') else None,
            'train_shape': X_train.shape,
            'test_shape': X_test.shape
        }
        
        # Передаем через XCom
        xcom_push('processed_data', processed_data)
        xcom_push('preprocessing_metadata', {
            'train_samples': len(y_train),
            'test_samples': len(y_test),
            'feature_count': X_train.shape[1]
        })
        
        print(f" Обучающая выборка: {X_train.shape}")
        print(f" Тестовая выборка: {X_test.shape}")
        
        # === ЭТАП 3: ОБУЧЕНИЕ МОДЕЛИ ===
        print("\n3⃣ === ОБУЧЕНИЕ МОДЕЛИ ===")
        
        # Получаем обработанные данные из XCom
        processed_data_from_xcom = xcom_pull('processed_data')
        if processed_data_from_xcom is None:
            raise ValueError("Обработанные данные не найдены в XCom!")
        
        # Восстанавливаем данные
        X_train_restored = np.array(processed_data_from_xcom['X_train'])
        X_test_restored = np.array(processed_data_from_xcom['X_test'])
        y_train_restored = np.array(processed_data_from_xcom['y_train'])
        y_test_restored = np.array(processed_data_from_xcom['y_test'])
        
        print(f" Восстановлены обработанные данные из XCom")
        print(f"   - X_train: {X_train_restored.shape}")
        print(f"   - y_train: {len(y_train_restored)} образцов")
        
        # Обучаем модель
        trainer = ModelTrainer()
        training_results = trainer.train_model_from_data(
            X_train_restored, y_train_restored,
            use_hyperparameter_tuning=False
        )
        
        # Сохраняем модель и передаем данные через XCom
        model_path = "results/models/demo_xcom_model.joblib"
        trainer.save_model(model_path)
        
        training_xcom_data = {
            'model_path': model_path,
            'model_type': type(trainer.get_model()).__name__,
            'training_results': training_results,
            'cv_score': training_results.get('baseline_cv', {}).get('mean_cv_score')
        }
        
        xcom_push('training_results', training_xcom_data)
        xcom_push('test_data', {
            'X_test': X_test_restored.tolist(),
            'y_test': y_test_restored.tolist()
        })
        
        print(f" Модель обучена: {type(trainer.get_model()).__name__}")
        print(f" Модель сохранена: {model_path}")
        
        # === ЭТАП 4: ОЦЕНКА МОДЕЛИ ===
        print("\n4⃣ === ОЦЕНКА МОДЕЛИ ===")
        
        # Получаем данные модели и тестовые данные из XCom
        training_data_from_xcom = xcom_pull('training_results')
        test_data_from_xcom = xcom_pull('test_data')
        
        if training_data_from_xcom is None or test_data_from_xcom is None:
            raise ValueError("Данные модели или тестовые данные не найдены в XCom!")
        
        # Восстанавливаем тестовые данные
        X_test_final = np.array(test_data_from_xcom['X_test'])
        y_test_final = np.array(test_data_from_xcom['y_test'])
        
        # Загружаем модель
        import joblib
        model = joblib.load(training_data_from_xcom['model_path'])
        
        # Оцениваем модель
        calculator = MetricsCalculator()
        metrics = calculator.evaluate_model(model, X_test_final, y_test_final)
        
        # Подготавливаем метрики для XCom
        evaluation_xcom_data = {
            'basic_metrics': metrics.get('basic_metrics', {}),
            'probability_metrics': metrics.get('probability_metrics', {}),
            'model_info': {
                'model_type': training_data_from_xcom['model_type'],
                'model_path': training_data_from_xcom['model_path']
            }
        }
        
        xcom_push('evaluation_metrics', evaluation_xcom_data)
        
        basic_metrics = metrics.get('basic_metrics', {})
        print(f" Точность: {basic_metrics.get('accuracy', 0):.4f}")
        print(f" F1-score: {basic_metrics.get('f1_score', 0):.4f}")
        print(f" Precision: {basic_metrics.get('precision', 0):.4f}")
        print(f" Recall: {basic_metrics.get('recall', 0):.4f}")
        
        # === ЭТАП 5: СБОРКА РЕЗУЛЬТАТОВ ===
        print("\n5⃣ === СБОРКА РЕЗУЛЬТАТОВ ===")
        
        # Собираем все данные из XCom
        all_xcom_keys = list(xcom_data.keys())
        print(f" Доступные XCom ключи: {all_xcom_keys}")
        
        # Создаем итоговый отчет
        final_results = {
            'pipeline_execution': {
                'timestamp': datetime.now().isoformat(),
                'execution_mode': 'XCom Demo'
            },
            'data_summary': {
                'original_shape': raw_data_from_xcom['shape'],
                'validation_passed': xcom_pull('validation_results')['is_valid']
            },
            'preprocessing_summary': xcom_pull('preprocessing_metadata'),
            'training_summary': {
                'model_type': training_data_from_xcom['model_type'],
                'cv_score': training_data_from_xcom['cv_score']
            },
            'evaluation_summary': evaluation_xcom_data['basic_metrics'],
            'xcom_integration': {
                'total_xcom_keys': len(all_xcom_keys),
                'xcom_keys': all_xcom_keys,
                'data_flow_success': True
            }
        }
        
        xcom_push('final_results', final_results)
        
        print(" === XCom ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО ===")
        print(f" Итоговые результаты сохранены в XCom")
        print(f" XCom ключей использовано: {len(all_xcom_keys)}")
        
        # Демонстрируем размеры данных в XCom
        print("\n === СТАТИСТИКА XCOM ===")
        for key, value in xcom_data.items():
            size = len(str(value))
            print(f"   {key}: {size:,} символов ({type(value).__name__})")
        
        return final_results
        
    except Exception as e:
        logger.error(f" Ошибка в демонстрации XCom: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        results = demo_xcom_pipeline()
        print(f"\n Демонстрация XCom завершена успешно!")
    except Exception as e:
        print(f"\n Ошибка: {e}")
        sys.exit(1)
