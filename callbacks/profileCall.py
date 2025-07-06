from dash import Input, Output, html, State, dcc
import dash_bootstrap_components as dbc
from callbacks.db import get_connection  # если используешь DB
from datetime import datetime
import pymysql


def register_profile_callbacks(app):
    @app.callback(
        Output("profile-info", "children"),
        Input("current-user", "data")
    )
    def show_profile(user):
        if not user:
            return "Пользователь не авторизован."

        profile_card = dbc.Card([
            dbc.CardBody([
                html.H4(user["name"], className="card-title"),
                html.P(f"Роль: {'Преподаватель' if user['role'] == 'teacher' else 'Студент'}", className="card-text"),
                html.P(f"ID пользователя: {user['id']}", className="card-text"),
            ])
        ])

        # Если студент — просто возвращаем карточку
        if user["role"] != "teacher":
            return profile_card

        # Если преподаватель — добавим форму создания теста
        form = html.Div([
            profile_card,
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.H5("Создание нового теста"),
                    dbc.Label("Название теста:"),
                    dbc.Input(id="test-title", placeholder="Введите название", className="mb-2"),

                    dbc.Label("Описание:"),
                    dbc.Textarea(id="test-desc", placeholder="Описание теста", className="mb-2"),

                    dbc.Label("Группа:"),
                    dcc.Dropdown(id="test-group", className="mb-2"),

                    dbc.Label("Способ проверки:"),
                    dcc.RadioItems(
                        id="test-check-type",
                        options=[
                            {"label": "🧠 Автоматически", "value": "auto"},
                            {"label": "👀 Вручную", "value": "manual"}
                        ],
                        value="auto",
                        labelStyle={"display": "block"},
                        className="mb-3"
                    ),

                    dbc.Button("✅ Создать тест", id="create-test-btn", color="success"),
                    html.Div(id="create-test-msg", className="mt-3")
                ], width=6),

                dbc.Col([
                    html.H5("Добавить вопрос в тест"),
                    dbc.Label("Выберите тест:"),
                    dcc.Dropdown(id="question-test-select", className="mb-2"),

                    dbc.Label("Текст вопроса:"),
                    dbc.Textarea(id="question-text", className="mb-2"),

                    dbc.Label("Правильный ответ (если автопроверка):"),
                    dbc.Input(id="question-answer", type="text", className="mb-2"),

                    dbc.Button("➕ Добавить вопрос", id="add-question-btn", color="primary"),
                    html.Div(id="add-question-msg", className="mt-3")
                ], width=6)
                ])
            ])

        # # Вставляется в register_profile_callbacks, внутрь show_profile()
        # add_question_block = html.Div([
        #     html.Hr(),
        #     html.H5("Добавить вопрос в тест"),
            
        #     dbc.Label("Выберите тест:"),
        #     dcc.Dropdown(id="question-test-select", className="mb-2"),
            
        #     dbc.Label("Текст вопроса:"),
        #     dbc.Textarea(id="question-text", className="mb-2"),
            
        #     dbc.Label("Правильный ответ (если автопроверка):"),
        #     dbc.Input(id="question-answer", type="text", className="mb-2"),
            
        #     dbc.Button("➕ Добавить вопрос", id="add-question-btn", color="primary"),
        #     html.Div(id="add-question-msg", className="mt-2")
        # ])


        # return html.Div([profile_card, form])
        return html.Div([form])

    @app.callback(
        Output("create-test-msg", "children"),
        Input("create-test-btn", "n_clicks"),
        State("test-title", "value"),
        State("test-desc", "value"),
        State("test-group", "value"),
        State("test-check-type", "value"),
        State("current-user", "data"),
        prevent_initial_call=True
    )
    def create_test(_, title, desc, group_id, check_type, user):
        if not all([title, group_id, check_type]) or not user:
            return "⚠️ Заполните все поля"

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tests (title, description, group_id, created_by, check_type, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, desc or "", group_id, user["id"], check_type, datetime.now()))
            conn.commit()
            return "✅ Тест успешно создан!"
        except Exception as e:
            print("Ошибка при создании теста:", e)
            return f"❌ Ошибка: {e}"
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
            
    @app.callback(
    Output("test-group", "options"),
    Input("profile-info", "children"),  # Этот элемент существует в layout
    State("current-user", "data"),
    prevent_initial_call=True
)
    def load_teacher_groups(_, user):
        print(123)
        if not user or user["role"] != "teacher":
            return []

        try:
            conn = get_connection()
            print(23)

            cursor = conn.cursor()  # 🛠 ВАЖНО
            print(44)
            cursor.execute("SELECT id, name FROM student_groups")
            # cursor.execute("SELECT id, name FROM student_groups WHERE teacher_id = %s", (user["id"],))
            print(55)

            rows = cursor.fetchall()
            print(66)
            print([{"label": r["name"], "value": r["id"]} for r in rows])
            return [{"label": r["name"], "value": r["id"]} for r in rows]
        except Exception as e:
            print("Ошибка при загрузке групп преподавателя:", e)
            return []
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass

    @app.callback(
        Output("question-test-select", "options"),
        Input("profile-info", "children"),
        Input("current-user", "data"),
        prevent_initial_call=True
    )
    def load_teacher_tests(_, user):
        if not user or user["role"] != "teacher":
            return []
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title FROM tests WHERE created_by = %s", (user["id"],))
            tests = cursor.fetchall()
            return [{"label": t["title"], "value": t["id"]} for t in tests]
        except Exception as e:
            print("Ошибка при загрузке тестов:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    @app.callback(
        Output("add-question-msg", "children"),
        Input("add-question-btn", "n_clicks"),
        State("question-test-select", "value"),
        State("question-text", "value"),
        State("question-answer", "value"),
        prevent_initial_call=True
    )
    def add_question(n, test_id, text, answer):
        if not test_id or not text:
            return "⚠️ Заполните обязательные поля"
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO questions (test_id, question, answer) VALUES (%s, %s, %s)",
                (test_id, text, answer or "")
            )
            conn.commit()
            return "✅ Вопрос добавлен!"
        except Exception as e:
            print("Ошибка при добавлении вопроса:", e)
            return f"❌ Ошибка: {e}"
        finally:
            cursor.close()
            conn.close()
