from .upload import register_upload_callbacks
from .analysis import register_analysis_callbacks
from .preprocessing import register_preprocessing_callbacks
from .download import register_download_callbacks
from .auth import register_auth_callbacks

def register_callbacks(app):
    register_upload_callbacks(app)
    register_analysis_callbacks(app)
    register_preprocessing_callbacks(app)
    register_download_callbacks(app)
    register_auth_callbacks(app)
