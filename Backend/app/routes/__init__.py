from .health_routes import health_bp
from .company_routes import company_bp
from .job_routes import job_bp
from .application_routes import application_bp
from .admin_routes import admin_bp
from .feedback_routes import feedback_bp


def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(company_bp, url_prefix="/api")
    app.register_blueprint(job_bp, url_prefix="/api")
    app.register_blueprint(application_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api")
    app.register_blueprint(feedback_bp, url_prefix="/api")
