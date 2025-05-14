def handle_missing_values(df, column_options):
    df = df.copy()
    for col, strategy in column_options.items():
        if strategy == "mean":
            df[col] = df[col].fillna(df[col].mean())
        elif strategy == "median":
            df[col] = df[col].fillna(df[col].median())
        elif strategy == "drop":
            df = df.dropna(subset=[col])
        elif strategy == "fill_zero":
            df[col] = df[col].fillna(0)
    return df

