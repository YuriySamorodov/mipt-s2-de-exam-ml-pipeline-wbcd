"""
Модуль для предобработки данных.

Автор: Самородов Юрий Сергеевич, МФТИ
"""
import pandas as pd
import numpy as np
import logging
from typing import Tuple, List, Optional, Dict, Any
from sklearn.preprocessing import StandardScaler, LabelEncoder, RobustScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from scipy import stats
import os
import sys
import joblib

# Добавляем корневую папку в путь для импорта конфигурации
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.config_utils import Config, get_logger, ensure_dir
except ImportError:
    def get_logger(name: str):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)


logger = get_logger(__name__)


class DataPreprocessor:
    """Класс для предобработки данных Wisconsin Breast Cancer."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Инициализация препроцессора.
        
        Args:
            config: Объект конфигурации
        """
        self.config = config or Config()
        self.data_config = self.config.get_data_config()
        self.scaler = StandardScaler()
        self.robust_scaler = RobustScaler()  # Для данных с выбросами
        self.minmax_scaler = MinMaxScaler()  # Альтернативный скейлер
        self.label_encoder = LabelEncoder()
        self.feature_selector = None
        self.pca = None
        self.feature_columns = []
        self.engineered_features = []
        self.outlier_method = "iqr"  # iqr, zscore, isolation_forest
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Очищает данные от проблемных значений.
        
        Args:
            df: Исходный DataFrame
            
        Returns:
            Очищенный DataFrame
        """
        logger.info("Начало очистки данных")
        
        df_clean = df.copy()
        
        # Удаляем дубликаты
        initial_rows = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        removed_duplicates = initial_rows - len(df_clean)
        if removed_duplicates > 0:
            logger.info(f"Удалено дубликатов: {removed_duplicates}")
        
        # Удаляем строки с пустыми ID или diagnosis
        critical_columns = ["id", "diagnosis"]
        for col in critical_columns:
            if col in df_clean.columns:
                before_count = len(df_clean)
                df_clean = df_clean.dropna(subset=[col])
                after_count = len(df_clean)
                if before_count != after_count:
                    logger.info(f"Удалено строк с пустыми {col}: {before_count - after_count}")
        
        # Обработка пропущенных значений в числовых колонках
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df_clean[col].isnull().sum() > 0:
                # Заполняем медианой
                median_value = df_clean[col].median()
                df_clean[col].fillna(median_value, inplace=True)
                logger.info(f"Заполнены пропуски в {col} медианой: {median_value}")
        
        logger.info(f"Очистка данных завершена. Осталось строк: {len(df_clean)}")
        return df_clean
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Подготавливает признаки для обучения модели.
        
        Args:
            df: DataFrame с данными
            
        Returns:
            DataFrame с подготовленными признаками
        """
        logger.info("Начало подготовки признаков")
        
        df_processed = df.copy()
        
        # Исключаем ID из признаков
        if "id" in df_processed.columns:
            df_processed = df_processed.drop("id", axis=1)
        
        # Кодируем целевую переменную
        if "diagnosis" in df_processed.columns:
            # M (Malignant) = 1, B (Benign) = 0
            diagnosis_mapping = {"M": 1, "B": 0}
            df_processed["diagnosis_encoded"] = df_processed["diagnosis"].map(diagnosis_mapping)
            
            if df_processed["diagnosis_encoded"].isnull().sum() > 0:
                logger.warning("Найдены неизвестные значения в diagnosis")
            
            # Сохраняем оригинальную колонку для анализа
            # df_processed = df_processed.drop("diagnosis", axis=1)
        
        # Выбираем только числовые признаки
        feature_columns = [col for col in df_processed.columns 
                          if col not in ["diagnosis", "diagnosis_encoded"] and 
                          df_processed[col].dtype in [np.int64, np.float64]]
        
        self.feature_columns = feature_columns
        logger.info(f"Выбрано признаков для обучения: {len(feature_columns)}")
        
        return df_processed
    
    def scale_features(self, X_train: pd.DataFrame, X_test: pd.DataFrame = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Нормализует признаки с помощью StandardScaler.
        
        Args:
            X_train: Обучающая выборка
            X_test: Тестовая выборка (опционально)
            
        Returns:
            Tuple с нормализованными данными
        """
        logger.info("Начало нормализации признаков")
        
        # Обучаем скейлер на обучающих данных
        X_train_scaled = self.scaler.fit_transform(X_train)
        logger.info(f"Скейлер обучен на {X_train.shape[0]} образцах")
        
        X_test_scaled = None
        if X_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            logger.info(f"Тестовые данные нормализованы: {X_test.shape[0]} образцов")
        
        return X_train_scaled, X_test_scaled
    
    def split_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Разделяет данные на обучающую и тестовую выборки.
        
        Args:
            df: DataFrame с подготовленными данными
            
        Returns:
            Tuple (X_train, X_test, y_train, y_test)
        """
        logger.info("Начало разделения данных")
        
        # Определяем признаки и целевую переменную
        target_column = "diagnosis_encoded" if "diagnosis_encoded" in df.columns else "diagnosis"
        feature_columns = [col for col in df.columns if col not in ["diagnosis", "diagnosis_encoded"]]
        
        X = df[feature_columns]
        y = df[target_column]
        
        # Если целевая переменная категориальная, кодируем её
        if y.dtype == 'object':
            y = self.label_encoder.fit_transform(y)
        
        # Параметры разделения
        test_size = self.data_config.get("test_size", 0.2)
        random_state = self.data_config.get("random_state", 42)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y  # Сохраняем пропорции классов
        )
        
        logger.info(f"Данные разделены:")
        logger.info(f"  Обучающая выборка: {X_train.shape[0]} образцов")
        logger.info(f"  Тестовая выборка: {X_test.shape[0]} образцов")
        logger.info(f"  Признаков: {X_train.shape[1]}")
        
        # Проверяем распределение классов
        train_distribution = pd.Series(y_train).value_counts().to_dict()
        test_distribution = pd.Series(y_test).value_counts().to_dict()
        logger.info(f"  Распределение в обучающей выборке: {train_distribution}")
        logger.info(f"  Распределение в тестовой выборке: {test_distribution}")
        
        return X_train, X_test, y_train, y_test
    
    def save_preprocessor(self, output_dir: str = "results/preprocessors/"):
        """
        Сохраняет обученные препроцессоры.
        
        Args:
            output_dir: Директория для сохранения
        """
        ensure_dir(output_dir)
        
        try:
            # Сохраняем скейлер
            scaler_path = os.path.join(output_dir, "scaler.joblib")
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"Скейлер сохранен: {scaler_path}")
            
            # Сохраняем энкодер (если использовался)
            if hasattr(self.label_encoder, 'classes_'):
                encoder_path = os.path.join(output_dir, "label_encoder.joblib")
                joblib.dump(self.label_encoder, encoder_path)
                logger.info(f"Энкодер сохранен: {encoder_path}")
            
            # Сохраняем список признаков
            features_path = os.path.join(output_dir, "feature_columns.joblib")
            joblib.dump(self.feature_columns, features_path)
            logger.info(f"Список признаков сохранен: {features_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении препроцессоров: {str(e)}")
            raise
    
    def load_preprocessor(self, input_dir: str = "results/preprocessors/"):
        """
        Загружает сохраненные препроцессоры.
        
        Args:
            input_dir: Директория с сохраненными препроцессорами
        """
        try:
            # Загружаем скейлер
            scaler_path = os.path.join(input_dir, "scaler.joblib")
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                logger.info(f"Скейлер загружен: {scaler_path}")
            
            # Загружаем энкодер
            encoder_path = os.path.join(input_dir, "label_encoder.joblib")
            if os.path.exists(encoder_path):
                self.label_encoder = joblib.load(encoder_path)
                logger.info(f"Энкодер загружен: {encoder_path}")
            
            # Загружаем список признаков
            features_path = os.path.join(input_dir, "feature_columns.joblib")
            if os.path.exists(features_path):
                self.feature_columns = joblib.load(features_path)
                logger.info(f"Список признаков загружен: {features_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке препроцессоров: {str(e)}")
            raise
    
    def detect_outliers(self, df: pd.DataFrame, method: str = "iqr") -> Dict[str, List[int]]:
        """
        Обнаруживает выбросы в данных различными методами.
        
        Args:
            df: DataFrame для анализа
            method: Метод обнаружения ('iqr', 'zscore', 'isolation_forest')
            
        Returns:
            Словарь с индексами выбросов для каждой колонки
        """
        outliers = {}
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        numeric_columns = [col for col in numeric_columns if col != "id"]
        
        for col in numeric_columns:
            if method == "iqr":
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outlier_indices = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index.tolist()
                
            elif method == "zscore":
                z_scores = np.abs(stats.zscore(df[col].dropna()))
                outlier_indices = df.iloc[np.where(z_scores > 3)[0]].index.tolist()
                
            elif method == "isolation_forest":
                try:
                    from sklearn.ensemble import IsolationForest
                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    outlier_pred = iso_forest.fit_predict(df[[col]].dropna())
                    outlier_indices = df.iloc[np.where(outlier_pred == -1)[0]].index.tolist()
                except ImportError:
                    logger.warning("IsolationForest недоступен, используется IQR метод")
                    return self.detect_outliers(df, method="iqr")
            
            if outlier_indices:
                outliers[col] = outlier_indices
                logger.info(f"Найдено выбросов в {col} ({method}): {len(outlier_indices)}")
        
        return outliers
    
    def handle_outliers(self, df: pd.DataFrame, method: str = "cap", 
                       detection_method: str = "iqr") -> pd.DataFrame:
        """
        Обрабатывает выбросы в данных.
        
        Args:
            df: Исходный DataFrame
            method: Метод обработки ('remove', 'cap', 'transform')
            detection_method: Метод обнаружения выбросов
            
        Returns:
            DataFrame с обработанными выбросами
        """
        logger.info(f"Обработка выбросов методом: {method}")
        df_processed = df.copy()
        outliers = self.detect_outliers(df, detection_method)
        
        if method == "remove":
            # Удаляем строки с выбросами
            all_outlier_indices = set()
            for indices in outliers.values():
                all_outlier_indices.update(indices)
            
            df_processed = df_processed.drop(list(all_outlier_indices))
            logger.info(f"Удалено строк с выбросами: {len(all_outlier_indices)}")
            
        elif method == "cap":
            # Ограничиваем выбросы (winsorization)
            for col, indices in outliers.items():
                q1 = df[col].quantile(0.05)
                q99 = df[col].quantile(0.95)
                df_processed[col] = df_processed[col].clip(lower=q1, upper=q99)
            logger.info("Выбросы ограничены квантилями 5% и 95%")
            
        elif method == "transform":
            # Применяем логарифмическую трансформацию к положительным данным
            for col in outliers.keys():
                if df_processed[col].min() > 0:
                    df_processed[col] = np.log1p(df_processed[col])
                    logger.info(f"Применена log трансформация к {col}")
        
        return df_processed
    
    def create_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Создает новые признаки на основе существующих.
        
        Args:
            df: Исходный DataFrame
            
        Returns:
            DataFrame с новыми признаками
        """
        logger.info("Создание новых признаков (Feature Engineering)")
        df_features = df.copy()
        
        # Получаем числовые колонки (исключая id и diagnosis)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        feature_cols = [col for col in numeric_cols if col not in ["id", "diagnosis"]]
        
        if len(feature_cols) >= 30:  # Wisconsin dataset имеет 30 признаков
            # Группируем признаки по типам (mean, se, worst)
            mean_cols = [col for col in feature_cols if col.endswith('_mean')]
            se_cols = [col for col in feature_cols if col.endswith('_se')]
            worst_cols = [col for col in feature_cols if col.endswith('_worst')]
            
            # Если нет суффиксов, создаем группы по позиции
            if not mean_cols:
                mean_cols = feature_cols[:10]
                se_cols = feature_cols[10:20]
                worst_cols = feature_cols[20:30]
            
            # Создаем агрегированные признаки
            if mean_cols:
                df_features['mean_features_sum'] = df[mean_cols].sum(axis=1)
                df_features['mean_features_mean'] = df[mean_cols].mean(axis=1)
                df_features['mean_features_std'] = df[mean_cols].std(axis=1)
                self.engineered_features.extend(['mean_features_sum', 'mean_features_mean', 'mean_features_std'])
            
            if se_cols:
                df_features['se_features_sum'] = df[se_cols].sum(axis=1)
                df_features['se_features_mean'] = df[se_cols].mean(axis=1)
                self.engineered_features.extend(['se_features_sum', 'se_features_mean'])
            
            if worst_cols:
                df_features['worst_features_sum'] = df[worst_cols].sum(axis=1)
                df_features['worst_features_max'] = df[worst_cols].max(axis=1)
                self.engineered_features.extend(['worst_features_sum', 'worst_features_max'])
            
            # Создаем отношения между признаками
            if len(feature_cols) >= 4:
                # Отношения размера (radius, perimeter, area)
                if 'radius_mean' in df.columns and 'perimeter_mean' in df.columns:
                    df_features['radius_perimeter_ratio'] = df['radius_mean'] / (df['perimeter_mean'] + 1e-8)
                    self.engineered_features.append('radius_perimeter_ratio')
                
                if 'area_mean' in df.columns and 'perimeter_mean' in df.columns:
                    df_features['area_perimeter_ratio'] = df['area_mean'] / (df['perimeter_mean'] + 1e-8)
                    self.engineered_features.append('area_perimeter_ratio')
                
                # Создаем композитные индексы
                first_col, second_col = feature_cols[0], feature_cols[1]
                df_features['composite_index_1'] = df[first_col] * df[second_col]
                df_features['composite_index_2'] = df[first_col] / (df[second_col] + 1e-8)
                self.engineered_features.extend(['composite_index_1', 'composite_index_2'])
        
        logger.info(f"Создано новых признаков: {len(self.engineered_features)}")
        return df_features
    
    def select_features(self, X: pd.DataFrame, y: pd.Series, method: str = "univariate", 
                       n_features: int = 20) -> pd.DataFrame:
        """
        Выбирает наиболее важные признаки.
        
        Args:
            X: Матрица признаков
            y: Целевая переменная
            method: Метод отбора ('univariate', 'rfe', 'pca')
            n_features: Количество признаков для отбора
            
        Returns:
            DataFrame с отобранными признаками
        """
        logger.info(f"Отбор признаков методом: {method}")
        
        if method == "univariate":
            # Univariate feature selection
            try:
                selector = SelectKBest(score_func=f_classif, k=min(n_features, X.shape[1]))
                X_selected = selector.fit_transform(X, y)
                selected_features = X.columns[selector.get_support()].tolist()
                self.feature_selector = selector
                
                logger.info(f"Отобрано признаков (univariate): {len(selected_features)}")
                return pd.DataFrame(X_selected, columns=selected_features, index=X.index)
            except ImportError:
                logger.warning("SelectKBest недоступен, пропускаем отбор признаков")
                return X
                
        elif method == "rfe":
            # Recursive Feature Elimination
            try:
                estimator = LogisticRegression(random_state=42, max_iter=1000)
                selector = RFE(estimator, n_features_to_select=min(n_features, X.shape[1]))
                X_selected = selector.fit_transform(X, y)
                selected_features = X.columns[selector.get_support()].tolist()
                self.feature_selector = selector
                
                logger.info(f"Отобрано признаков (RFE): {len(selected_features)}")
                return pd.DataFrame(X_selected, columns=selected_features, index=X.index)
            except ImportError:
                logger.warning("RFE недоступен, пропускаем отбор признаков")
                return X
                
        elif method == "pca":
            # Principal Component Analysis
            try:
                pca = PCA(n_components=min(n_features, X.shape[1]))
                X_pca = pca.fit_transform(X)
                pca_features = [f'PC_{i+1}' for i in range(X_pca.shape[1])]
                self.pca = pca
                
                logger.info(f"PCA компонентов: {X_pca.shape[1]}")
                logger.info(f"Объясненная дисперсия: {pca.explained_variance_ratio_.sum():.3f}")
                return pd.DataFrame(X_pca, columns=pca_features, index=X.index)
            except ImportError:
                logger.warning("PCA недоступен, пропускаем PCA")
                return X
        
        return X
    
    def preprocess_pipeline(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Полный пайплайн предобработки данных.
        
        Args:
            df: Исходный DataFrame
            
        Returns:
            Tuple (X_train_scaled, X_test_scaled, y_train, y_test)
        """
        logger.info("Запуск полного пайплайна предобработки")
        
        # 1. Очистка данных
        df_clean = self.clean_data(df)
        
        # 2. Подготовка признаков
        df_processed = self.prepare_features(df_clean)
        
        # 3. Разделение данных
        X_train, X_test, y_train, y_test = self.split_data(df_processed)
        
        # 4. Нормализация признаков
        X_train_scaled, X_test_scaled = self.scale_features(X_train, X_test)
        
        # 5. Сохранение препроцессоров
        self.save_preprocessor()
        
        logger.info("Пайплайн предобработки завершен успешно")
        
        return X_train_scaled, X_test_scaled, y_train, y_test


def main():
    """Главная функция для тестирования модуля."""
    try:
        # Импортируем загрузчик данных
        from data_loader import DataLoader
        
        # Загружаем данные
        loader = DataLoader()
        df = loader.load_data()
        
        # Инициализируем препроцессор
        preprocessor = DataPreprocessor()
        
        # Запускаем полный пайплайн
        X_train, X_test, y_train, y_test = preprocessor.preprocess_pipeline(df)
        
        print(f"Предобработка завершена успешно!")
        print(f"Обучающая выборка: {X_train.shape}")
        print(f"Тестовая выборка: {X_test.shape}")
        print(f"Целевая переменная (обучение): {len(y_train)}")
        print(f"Целевая переменная (тест): {len(y_test)}")
        
        return X_train, X_test, y_train, y_test
        
    except Exception as e:
        logger.error(f"Ошибка в main: {str(e)}")
        raise


if __name__ == "__main__":
    main()
