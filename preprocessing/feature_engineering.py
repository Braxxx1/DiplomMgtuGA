from sklearn.preprocessing import LabelEncoder
import pandas as pd


def encode_categorical(df):
    """Кодирует категориальные переменные с помощью Label Encoding"""
    le = LabelEncoder()
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = le.fit_transform(df[col])
    print("Категориальные переменные закодированы")
    return df


def apply_encoding_methods(df, encoding_choices):
    df = df.copy()
    for col, method in encoding_choices.items():
        if method == "One-Hot Encoding":
            dummies = pd.get_dummies(df[col], prefix=col)
            df = df.drop(columns=[col])
            df = pd.concat([df, dummies], axis=1)
        elif method == "Label Encoding":
            encoder = LabelEncoder()
            df[col] = encoder.fit_transform(df[col].astype(str))
        # "Не обрабатывать" — ничего не делаем
    return df
