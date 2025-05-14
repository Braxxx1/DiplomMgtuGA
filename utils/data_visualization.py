import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Создаём папку для графиков
if not os.path.exists("reports/plots"):
    os.makedirs("reports/plots")

import os
import matplotlib.pyplot as plt
import seaborn as sns

def plot_distributions(df, columns):
    # Убедимся, что папка для сохранения существует
    plot_dir = "reports/plots/distributions"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    for col in columns:
        plt.figure(figsize=(6, 4))
        sns.histplot(df[col], kde=True, bins=30)
        plt.title(f"Распределение: {col}")
        
        # Сохраняем график в папку
        plt.savefig(f"{plot_dir}/{'_'.join(col.split())}_distribution.png")
        plt.close()
    
    print("Гистограммы сохранены в reports/plots/distributions")



def plot_correlation_matrix(df):
    """Создаёт корреляционную матрицу"""
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Корреляционная матрица")
    plt.savefig("reports/plots/correlation_matrix.png")
    plt.close()
    print("Корреляционная матрица сохранена в reports/plots/")


def plot_outliers(df, columns):
    """Генерирует boxplot для числовых признаков"""
    plot_dir = "reports/plots/outliers"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    num_cols = df.select_dtypes(include=["number"]).columns
    for col in columns:
        plt.figure(figsize=(6, 4))
        sns.boxplot(x=df[col])
        plt.title(f"Выбросы в: {col}")
        plt.savefig(f"{plot_dir}/{'_'.join(col.split())}_outliers.png")
        plt.close()
    print(f"Графики выбросов сохранены в {plot_dir}")


