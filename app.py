import os

from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from albumy.extensions import  db, moment, bootstrap, csrf
from albumy.settings import Config

from blueprints.main import bp as main_bp


def create_app(Config_name=None):

    app = Flask(__name__)

    if Config_name is None:
        Config_name = os.getenv('FlASK_CONFIG')

    app.config.from_object(Config[Config_name])

    def register_extensions(app):
        # login_manager.init_app(app)
        db.init_app(app)
        moment.init_app(app)
        bootstrap.init_app(app)
        csrf.init_app(app)
    def register_errors(app):
        @app.errorhandler(CSRFError)
        def bad_request(e):
            return render_template('errors/400.html', desctription=e.deiscription), 400

        @app.errorhandler(500)
        def error_handler(e):
            return render_template('errors/500.html', description=e), 500

        @app.errorhandler(404)
        def error_not_found(e):
            return render_template('errors/500.html'), 404

    def register_blueprint(app):
       app.register_blueprint(main_bp)

    register_extensions(app)
    register_errors(app)
    register_blueprint(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
