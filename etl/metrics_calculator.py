"""
Модуль для расчета и анализа метрик модели машинного обучения.

Автор: Самородов Юрий Сергеевич, МФТИ
"""
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Optional, List
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    roc_curve, precision_recall_curve
)

# Настройка matplotlib для работы без GUI (важно делать до импорта pyplot)
import matplotlib
matplotlib.use('Agg')  # Использует backend без GUI
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import sys
from datetime import datetime

# Добавляем корневую папку в путь для импорта конфигурации
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.config_utils import Config, get_logger, ensure_dir
except ImportError:
    def get_logger(name: str):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)


logger = get_logger(__name__)


class MetricsCalculator:
    """Класс для расчета и анализа метрик модели."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Инициализация калькулятора метрик.
        
        Args:
            config: Объект конфигурации
        """
        self.config = config or Config()
        self.metrics_history = []
        self.class_names = ["Доброкачественная", "Злокачественная"]
        
        # Настройка matplotlib для русского языка
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
        plt.rcParams.update({'font.size': 10})
    
    def calculate_basic_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Рассчитывает основные метрики классификации.
        
        Args:
            y_true: Истинные метки
            y_pred: Предсказанные метки
            
        Returns:
            Словарь с основными метриками
        """
        logger.info("Расчет основных метрик классификации")
        
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average='weighted')),
            "recall": float(recall_score(y_true, y_pred, average='weighted')),
            "f1_score": float(f1_score(y_true, y_pred, average='weighted')),
            "precision_macro": float(precision_score(y_true, y_pred, average='macro')),
            "recall_macro": float(recall_score(y_true, y_pred, average='macro')),
            "f1_score_macro": float(f1_score(y_true, y_pred, average='macro'))
        }
        
        # Рассчитываем AUC, если есть вероятности
        try:
            if len(np.unique(y_true)) == 2:  # Бинарная классификация
                metrics["precision_binary"] = float(precision_score(y_true, y_pred))
                metrics["recall_binary"] = float(recall_score(y_true, y_pred))
                metrics["f1_score_binary"] = float(f1_score(y_true, y_pred))
        except Exception as e:
            logger.warning(f"Ошибка при расчете бинарных метрик: {str(e)}")
        
        logger.info("Основные метрики:")
        for metric_name, value in metrics.items():
            logger.info(f"  {metric_name}: {value:.4f}")
        
        return metrics
    
    def calculate_probabilistic_metrics(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> Dict[str, float]:
        """
        Рассчитывает метрики, основанные на вероятностях.
        
        Args:
            y_true: Истинные метки
            y_pred_proba: Предсказанные вероятности
            
        Returns:
            Словарь с метриками на основе вероятностей
        """
        logger.info("Расчет метрик на основе вероятностей")
        
        metrics = {}
        
        try:
            # Для бинарной классификации
            if len(np.unique(y_true)) == 2 and y_pred_proba.shape[1] == 2:
                # Используем вероятности для положительного класса
                y_proba_pos = y_pred_proba[:, 1]
                
                metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba_pos))
                
                # Рассчитываем кривые ROC и Precision-Recall
                fpr, tpr, _ = roc_curve(y_true, y_proba_pos)
                metrics["roc_curve"] = {
                    "fpr": fpr.tolist(),
                    "tpr": tpr.tolist()
                }
                
                precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_proba_pos)
                metrics["precision_recall_curve"] = {
                    "precision": precision_curve.tolist(),
                    "recall": recall_curve.tolist()
                }
                
            # Для многоклассовой классификации
            elif len(np.unique(y_true)) > 2:
                metrics["roc_auc_ovr"] = float(roc_auc_score(y_true, y_pred_proba, multi_class='ovr'))
                metrics["roc_auc_ovo"] = float(roc_auc_score(y_true, y_pred_proba, multi_class='ovo'))
        
        except Exception as e:
            logger.warning(f"Ошибка при расчете вероятностных метрик: {str(e)}")
        
        if metrics:
            logger.info("Вероятностные метрики:")
            for metric_name, value in metrics.items():
                if isinstance(value, float):
                    logger.info(f"  {metric_name}: {value:.4f}")
        
        return metrics
    
    def calculate_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """
        Рассчитывает матрицу ошибок и связанные метрики.
        
        Args:
            y_true: Истинные метки
            y_pred: Предсказанные метки
            
        Returns:
            Словарь с матрицей ошибок и метриками
        """
        logger.info("Расчет матрицы ошибок")
        
        cm = confusion_matrix(y_true, y_pred)
        
        # Нормализованная матрица ошибок
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        # Детальные метрики для каждого класса
        report = classification_report(y_true, y_pred, output_dict=True)
        
        result = {
            "confusion_matrix": cm.tolist(),
            "confusion_matrix_normalized": cm_normalized.tolist(),
            "classification_report": report,
            "true_negatives": int(cm[0, 0]) if cm.shape == (2, 2) else None,
            "false_positives": int(cm[0, 1]) if cm.shape == (2, 2) else None,
            "false_negatives": int(cm[1, 0]) if cm.shape == (2, 2) else None,
            "true_positives": int(cm[1, 1]) if cm.shape == (2, 2) else None
        }
        
        # Рассчитываем специфичность и чувствительность для бинарной классификации
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            result["sensitivity"] = float(tp / (tp + fn))  # Recall/True Positive Rate
            result["specificity"] = float(tn / (tn + fp))  # True Negative Rate
            result["false_positive_rate"] = float(fp / (fp + tn))
            result["false_negative_rate"] = float(fn / (fn + tp))
        
        logger.info(f"Матрица ошибок рассчитана. Форма: {cm.shape}")
        if cm.shape == (2, 2):
            logger.info(f"  Истинно положительные: {result['true_positives']}")
            logger.info(f"  Истинно отрицательные: {result['true_negatives']}")
            logger.info(f"  Ложно положительные: {result['false_positives']}")
            logger.info(f"  Ложно отрицательные: {result['false_negatives']}")
            logger.info(f"  Чувствительность: {result['sensitivity']:.4f}")
            logger.info(f"  Специфичность: {result['specificity']:.4f}")
        
        return result
    
    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray, 
                            output_path: str = "results/confusion_matrix.png"):
        """
        Создает и сохраняет визуализацию матрицы ошибок.
        
        Args:
            y_true: Истинные метки
            y_pred: Предсказанные метки
            output_path: Путь для сохранения графика
        """
        logger.info("Создание визуализации матрицы ошибок")
        
        try:
            ensure_dir(os.path.dirname(output_path))
            
            # Создаем матрицу ошибок
            cm = confusion_matrix(y_true, y_pred)
            
            # Создаем subplot
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Абсолютные значения
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax1)
            ax1.set_title('Матрица ошибок (абсолютные значения)')
            ax1.set_ylabel('Истинные метки')
            ax1.set_xlabel('Предсказанные метки')
            
            # Нормализованные значения
            cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            sns.heatmap(cm_normalized, annot=True, fmt='.2f', cmap='Blues', ax=ax2)
            ax2.set_title('Матрица ошибок (нормализованная)')
            ax2.set_ylabel('Истинные метки')
            ax2.set_xlabel('Предсказанные метки')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Матрица ошибок сохранена: {output_path}")
            
        except Exception as e:
            logger.warning(f"Не удалось создать визуализацию матрицы ошибок: {e}")
            logger.info("Продолжаем выполнение без визуализации")
    
    def plot_roc_curve(self, y_true: np.ndarray, y_pred_proba: np.ndarray,
                      output_path: str = "results/roc_curve.png"):
        """
        Создает и сохраняет ROC-кривую.
        
        Args:
            y_true: Истинные метки
            y_pred_proba: Предсказанные вероятности
            output_path: Путь для сохранения графика
        """
        logger.info("Создание ROC-кривой")
        
        try:
            ensure_dir(os.path.dirname(output_path))
            
            if len(np.unique(y_true)) != 2 or y_pred_proba.shape[1] != 2:
                logger.warning("ROC-кривая доступна только для бинарной классификации")
                return
            
            # Используем вероятности для положительного класса
            y_proba_pos = y_pred_proba[:, 1]
            
            # Рассчитываем ROC-кривую
            fpr, tpr, _ = roc_curve(y_true, y_proba_pos)
            roc_auc = roc_auc_score(y_true, y_proba_pos)
            
            # Создаем график
            plt.figure(figsize=(8, 6))
            plt.plot(fpr, tpr, color='darkorange', lw=2, 
                    label=f'ROC кривая (AUC = {roc_auc:.2f})')
            plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
                    label='Случайный классификатор')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('Ложноположительная частота (1 - Специфичность)')
            plt.ylabel('Истинноположительная частота (Чувствительность)')
            plt.title('ROC-кривая')
            plt.legend(loc="lower right")
            plt.grid(True, alpha=0.3)
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"ROC-кривая сохранена: {output_path}")
            
        except Exception as e:
            logger.warning(f"Не удалось создать ROC-кривую: {e}")
            logger.info("Продолжаем выполнение без визуализации")
    
    def plot_precision_recall_curve(self, y_true: np.ndarray, y_pred_proba: np.ndarray,
                                   output_path: str = "results/precision_recall_curve.png"):
        """
        Создает и сохраняет кривую Precision-Recall.
        
        Args:
            y_true: Истинные метки
            y_pred_proba: Предсказанные вероятности
            output_path: Путь для сохранения графика
        """
        logger.info("Создание кривой Precision-Recall")
        
        ensure_dir(os.path.dirname(output_path))
        
        if len(np.unique(y_true)) != 2 or y_pred_proba.shape[1] != 2:
            logger.warning("Кривая Precision-Recall доступна только для бинарной классификации")
            return
        
        # Используем вероятности для положительного класса
        y_proba_pos = y_pred_proba[:, 1]
        
        # Рассчитываем кривую Precision-Recall
        precision, recall, _ = precision_recall_curve(y_true, y_proba_pos)
        
        # Создаем график
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, color='blue', lw=2)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Полнота (Recall)')
        plt.ylabel('Точность (Precision)')
        plt.title('Кривая Precision-Recall')
        plt.grid(True, alpha=0.3)
        
        # Добавляем базовую линию (для случайного классификатора)
        baseline = np.sum(y_true) / len(y_true)
        plt.axhline(y=baseline, color='red', linestyle='--', 
                   label=f'Случайный классификатор (Precision = {baseline:.2f})')
        plt.legend()
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Кривая Precision-Recall сохранена: {output_path}")
    
    def evaluate_model(self, model, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Полная оценка модели на тестовых данных.
        
        Args:
            model: Обученная модель
            X_test: Тестовые признаки
            y_test: Тестовые метки
            
        Returns:
            Словарь со всеми метриками
        """
        logger.info("Начало полной оценки модели")
        
        # Предсказания
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)
        
        # Рассчитываем все метрики
        evaluation_results = {
            "timestamp": datetime.now().isoformat(),
            "test_samples": len(y_test),
            "basic_metrics": self.calculate_basic_metrics(y_test, y_pred),
            "probabilistic_metrics": self.calculate_probabilistic_metrics(y_test, y_pred_proba),
            "confusion_matrix_data": self.calculate_confusion_matrix(y_test, y_pred)
        }
        
        # Создаем визуализации
        self.plot_confusion_matrix(y_test, y_pred)
        self.plot_roc_curve(y_test, y_pred_proba)
        self.plot_precision_recall_curve(y_test, y_pred_proba)
        
        # Сохраняем в историю
        self.metrics_history.append(evaluation_results)
        
        logger.info("Полная оценка модели завершена")
        logger.info(f"Основные метрики на тестовых данных:")
        for metric, value in evaluation_results["basic_metrics"].items():
            logger.info(f"  {metric}: {value:.4f}")
        
        return evaluation_results
    
    def save_metrics(self, metrics: Dict[str, Any], output_path: str = "results/metrics.json"):
        """
        Сохраняет метрики в JSON файл.
        
        Args:
            metrics: Словарь с метриками
            output_path: Путь для сохранения
        """
        ensure_dir(os.path.dirname(output_path))
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Метрики сохранены: {output_path}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении метрик: {str(e)}")
            raise
    
    def generate_evaluation_report(self, metrics: Dict[str, Any], 
                                 output_path: str = "results/evaluation_report.md"):
        """
        Генерирует отчет об оценке модели в формате Markdown.
        
        Args:
            metrics: Словарь с метриками
            output_path: Путь для сохранения отчета
        """
        logger.info("Генерация отчета об оценке модели")
        
        ensure_dir(os.path.dirname(output_path))
        
        report = f"""# Отчет об оценке модели

**Дата и время оценки:** {metrics.get('timestamp', 'Не указано')}
**Количество тестовых образцов:** {metrics.get('test_samples', 'Не указано')}

## Основные метрики

"""
        
        basic_metrics = metrics.get('basic_metrics', {})
        for metric, value in basic_metrics.items():
            report += f"- **{metric}:** {value:.4f}\n"
        
        report += "\n## Вероятностные метрики\n\n"
        prob_metrics = metrics.get('probabilistic_metrics', {})
        for metric, value in prob_metrics.items():
            if isinstance(value, float):
                report += f"- **{metric}:** {value:.4f}\n"
        
        report += "\n## Матрица ошибок\n\n"
        cm_data = metrics.get('confusion_matrix_data', {})
        if 'true_positives' in cm_data:
            report += f"""
- **Истинно положительные:** {cm_data['true_positives']}
- **Истинно отрицательные:** {cm_data['true_negatives']}
- **Ложно положительные:** {cm_data['false_positives']}
- **Ложно отрицательные:** {cm_data['false_negatives']}
- **Чувствительность:** {cm_data.get('sensitivity', 0):.4f}
- **Специфичность:** {cm_data.get('specificity', 0):.4f}
"""
        
        report += "\n## Интерпретация результатов\n\n"
        
        accuracy = basic_metrics.get('accuracy', 0)
        if accuracy >= 0.9:
            report += "Модель показывает отличные результаты (точность ≥ 90%).\n"
        elif accuracy >= 0.8:
            report += "Модель показывает хорошие результаты (точность ≥ 80%).\n"
        elif accuracy >= 0.7:
            report += "Модель показывает удовлетворительные результаты (точность ≥ 70%).\n"
        else:
            report += "Модель требует доработки (точность < 70%).\n"
        
        f1_score = basic_metrics.get('f1_score', 0)
        if f1_score >= 0.8:
            report += "F1-мера показывает хороший баланс между точностью и полнотой.\n"
        else:
            report += "F1-мера указывает на дисбаланс между точностью и полнотой.\n"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Отчет об оценке сохранен: {output_path}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении отчета: {str(e)}")
            raise


def main():
    """Главная функция для тестирования модуля."""
    try:
        # Импортируем необходимые модули
        from data_loader import DataLoader
        from data_preprocessor import DataPreprocessor
        from model_trainer import ModelTrainer
        
        # Загружаем и предобрабатываем данные
        loader = DataLoader()
        df = loader.load_data()
        
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test = preprocessor.preprocess_pipeline(df)
        
        # Обучаем модель
        trainer = ModelTrainer()
        trainer.train_full_pipeline(X_train, y_train, use_hyperparameter_tuning=False)
        
        # Оцениваем модель
        calculator = MetricsCalculator()
        metrics = calculator.evaluate_model(trainer.model, X_test, y_test)
        
        # Сохраняем результаты
        calculator.save_metrics(metrics)
        calculator.generate_evaluation_report(metrics)
        
        print(f"Оценка модели завершена успешно!")
        print(f"Точность: {metrics['basic_metrics']['accuracy']:.4f}")
        print(f"F1-мера: {metrics['basic_metrics']['f1_score']:.4f}")
        if 'roc_auc' in metrics['probabilistic_metrics']:
            print(f"ROC AUC: {metrics['probabilistic_metrics']['roc_auc']:.4f}")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Ошибка в main: {str(e)}")
        raise


if __name__ == "__main__":
    main()
