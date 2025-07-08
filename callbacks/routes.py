# callbacks/auth_login.py
from dash import Input, Output, no_update
from pages import dashboard, preprocessing, register, login, profile, test


def register_routes_callbacks(app):
    @app.callback(
    Output("page-content", "children"),
    Output("url", "pathname", allow_duplicate=True),
    Input("url", "pathname"),
    Input("current-user", "data"),
    prevent_initial_call="initial_duplicate"
    )
    def route_pages(path, user):
        protected = ["/dashboard", "/preprocessing"]
        # Нельзя пускать на защищенные страницы без авторизации
        if path in protected and not user:
            if path != "/login":
                return login.layout, "/login"
            return login.layout, no_update

        if path == "/dashboard":
            return dashboard.layout, path
        elif path == "/preprocessing":
            return preprocessing.layout, path
        elif path == "/register":
            return register.layout, path
        elif path == "/login":
            return login.layout, no_update
        elif path == "/profile" and user:
            return profile.layout, path
        elif 'test' in path and user:
            return test.layout, path
        
        # fallback
        if not user:
            if path != "/login":
                return login.layout, "/login"
            return login.layout, no_update
        return dashboard.layout, "/dashboard"  # например, дефолт для авторизованных