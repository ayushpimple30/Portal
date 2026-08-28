import os
from flask import Flask, render_template
from .config import DevelopmentConfig, ProductionConfig
from .extensions import csrf, db, login_manager, migrate

def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.from_object(config_object or (ProductionConfig if os.getenv('FLASK_ENV') == 'production' else DevelopmentConfig))
    db.init_app(app); migrate.init_app(app, db); login_manager.init_app(app); csrf.init_app(app)
    from .models import User
    @login_manager.user_loader
    def load_user(user_id): return db.session.get(User, int(user_id))
    from .main.routes import bp as main_bp
    from .auth.routes import bp as auth_bp
    from .student.routes import bp as student_bp
    from .admin.routes import bp as admin_bp
    app.register_blueprint(main_bp); app.register_blueprint(auth_bp); app.register_blueprint(student_bp); app.register_blueprint(admin_bp)
    for code in (400, 403, 404, 405, 500):
        app.register_error_handler(code, lambda error, c=code: (render_template('errors/error.html', code=c), c))
    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    return app
