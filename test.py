import dash
from dash import dcc, html, Input, Output, State, ctx
import pandas as pd
import pymysql
import hashlib

# Конфиг подключения
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "KAgdeckeywukMe0",
    "database": "analizeprog",
    "port": 3306,
    "connect_timeout": 5
}

# Функция хеширования пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Сохранение пользователя в БД
def register_user(name, email, password, role, group_id):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, group_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, hash_password(password), role, group_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Получение всех пользователей
def get_users():
    conn = pymysql.connect(**DB_CONFIG)
    df = pd.read_sql("SELECT id, name, email, role, group_id, registered_at FROM users", conn)
    conn.close()
    return df

# Инициализация Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Регистрация пользователя"),

    html.Div([
        html.Label("Имя"),
        dcc.Input(id="input-name", type="text", placeholder="Иван", debounce=True),
        html.Label("Email"),
        dcc.Input(id="input-email", type="email", placeholder="ivan@example.com", debounce=True),
        html.Label("Пароль"),
        dcc.Input(id="input-password", type="password", placeholder="Пароль", debounce=True),
        html.Label("Роль"),
        dcc.Dropdown(id="input-role", options=[
            {"label": "Студент", "value": "student"},
            {"label": "Преподаватель", "value": "teacher"},
        ], placeholder="Выберите роль"),
        html.Label("Группа"),
        dcc.Input(id="input-group", type="number", placeholder="101"),
        html.Button("Зарегистрировать", id="register-button", n_clicks=0),
        html.Div(id="register-msg", style={"marginTop": "10px", "color": "green"})
    ], style={"display": "grid", "gap": "10px", "maxWidth": "400px"}),

    html.Hr(),

    html.H3("Список пользователей"),
    html.Button("Обновить список", id="refresh-button", n_clicks=0),
    html.Div(id="user-table")
])

@app.callback(
    Output("register-msg", "children"),
    Input("register-button", "n_clicks"),
    State("input-name", "value"),
    State("input-email", "value"),
    State("input-password", "value"),
    State("input-role", "value"),
    State("input-group", "value"),
    prevent_initial_call=True
)
def handle_register(n_clicks, name, email, password, role, group_id):
    if not all([name, email, password, role]):
        return "⚠️ Заполните все обязательные поля."
    try:
        register_user(name, email, password, role, group_id)
        return "✅ Пользователь успешно зарегистрирован!"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@app.callback(
    Output("user-table", "children"),
    Input("refresh-button", "n_clicks"),
    prevent_initial_call=True
)
def update_user_table(n_clicks):
    df = get_users()
    return html.Table([
        html.Thead(html.Tr([html.Th(col) for col in df.columns])),
        html.Tbody([
            html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
            for i in range(len(df))
        ])
    ], style={"border": "1px solid black", "borderCollapse": "collapse", "width": "100%"})

if __name__ == "__main__":
    app.run(debug=True)
