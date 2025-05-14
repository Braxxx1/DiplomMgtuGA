def remove_duplicates(df):
    """Удаляет дубликаты в данных"""
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    print(f"Удалено {before - after} дубликатов")
    return df
