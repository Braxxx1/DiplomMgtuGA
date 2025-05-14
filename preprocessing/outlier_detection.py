import numpy as np

def replace_outliers(df, threshold={}):
    """Заменяет выбросы на граничные значения на основе межквартильного размаха (IQR)"""
    for col in threshold:
        # Расчёт квартилей и IQR для каждого столбца
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold[col] * IQR
        upper_bound = Q3 + threshold[col] * IQR

        # Подсчёт количества выбросов
        outliers_below = (df[col] < lower_bound).sum()
        outliers_above = (df[col] > upper_bound).sum()
        total_outliers = outliers_below + outliers_above

        # Замена выбросов на граничные значения
        df[col] = df[col].clip(lower=int(lower_bound), upper=int(upper_bound))

        # Выводим информацию о количестве обработанных выбросов
        print(f"Обработано {total_outliers} выбросов в столбце {col} (нижних: {outliers_below}, верхних: {outliers_above})")

    return df
