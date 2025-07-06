from .analysis import register_analysis_callbacks
from .auth import register_auth_callbacks
from .download import register_download_callbacks
from .preprocessing import register_preprocessing_callbacks
from .upload import register_upload_callbacks
from .auth_login import register_login_callbacks
from .profileCall import register_profile_callbacks
from .routes import register_routes_callbacks


def register_callbacks(app):
    register_upload_callbacks(app)
    register_analysis_callbacks(app)
    register_preprocessing_callbacks(app)
    register_download_callbacks(app)
    register_auth_callbacks(app)
    register_login_callbacks(app)
    register_profile_callbacks(app)
    register_routes_callbacks(app)