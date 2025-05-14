from preprocessing.data_loader import load_data
from preprocessing.duplicate_handler import remove_duplicates
from preprocessing.missing_values import handle_missing_values
from preprocessing.outlier_detection import replace_outliers
from preprocessing.feature_engineering import encode_categorical
from utils.logger import log
from utils.report_writer import write_report
from utils.data_visualization import plot_distributions, plot_correlation_matrix, plot_outliers

def preprocess_data(df, column_options=None, outlier_threshold=1.5):
    """Полный цикл предобработки данных с логированием, отчётами и визуализацией"""

    log("Начало предобработки данных")

    if df is None:
        log("Ошибка загрузки данных!")
        return None

    initial_shape = df.shape
    log(f"Загружено {initial_shape[0]} строк, {initial_shape[1]} столбцов")

    # Удаление дубликатов
    df = remove_duplicates(df)

    # Обработка пропусков
    if column_options:
        df = handle_missing_values(df, column_options)
    
    # # Генерация графиков для распределений после обработки пропусков
    # plot_distributions(df)

    final_shape = df.shape
    log(f"Обработано! Итоговый размер данных после обработки пропусков: {final_shape[0]} строк, {final_shape[1]} столбцов")
    
    # Запись промежуточного отчёта
    stats = {
        "Исходное количество строк": initial_shape[0],
        "Исходное количество столбцов": initial_shape[1],
        "Конечное количество строк после пропусков": final_shape[0],
        "Конечное количество столбцов после пропусков": final_shape[1]
    }
    write_report(stats)

    # Возврат обработанных данных после пропусков для дальнейшей работы с выбросами
    return df


def preprocess_outliers(df, outlier_threshold={}):
    """Обработка выбросов после обработки пропусков"""

    log("Обработка выбросов")

    initial_shape = df.shape

    # Удаление выбросов
    df = remove_outliers(df, threshold=outlier_threshold)

    # Генерация графиков для выбросов
    plot_outliers(df, list(outlier_threshold.keys()))

    final_shape = df.shape
    log(f"Обработано! Итоговый размер данных после обработки выбросов: {final_shape[0]} строк, {final_shape[1]} столбцов")

    # Запись отчёта
    stats = {
        "Исходное количество строк": initial_shape[0],
        "Исходное количество столбцов": initial_shape[1],
        "Конечное количество строк после выбросов": final_shape[0],
        "Конечное количество столбцов после выбросов": final_shape[1]
    }
    write_report(stats)

    # Возврат окончательных данных после обработки выбросов
    return df