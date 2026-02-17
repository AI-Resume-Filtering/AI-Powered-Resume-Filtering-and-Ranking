from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from .config import Config
from .extensions import init_mongo
from .routes import register_blueprints
from .utils.logging import configure_logging


def create_app():
    load_dotenv()
    configure_logging()

    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for frontend access
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    init_mongo(app)
    register_blueprints(app)

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"success": False, "message": "Endpoint not found. Use /api/health or /api/..."}), 404

    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.exception("Unhandled error")
        return jsonify({"success": False, "message": "Internal server error"}), 500

    return app
