import os

# Создаём папку для отчётов
if not os.path.exists("reports"):
    os.makedirs("reports")

def write_report(stats):
    """Записывает сводный отчёт о предобработке"""
    report_path = "reports/summary_report.txt"
    with open(report_path, "w") as file:
        file.write("### Отчёт о предобработке данных ###\n\n")
        for key, value in stats.items():
            file.write(f"{key}: {value}\n")
    print(f"Отчёт сохранён в {report_path}")
