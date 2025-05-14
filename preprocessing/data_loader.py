import pandas as pd

def load_data(file_path):
    """Загружает данные из CSV или Excel."""
    try:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Поддерживаются только CSV и Excel")
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return None
