import os
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure required data, upload, and output directories exist seamlessly
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    # Register blueprints/routes
    from app.routes import api_bp
    app.register_blueprint(api_bp)

    return app