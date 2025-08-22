import os

import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from albumy.extensions import login_manager, db, moment, bootstrap, csrf, mail, dropzone, avatars
from albumy.settings import Config
from albumy.models import Role, Guest

from blueprints.main import bp as main_bp
from blueprints.auth import bp as auth_bp


def create_app(Config_name=None):

    app = Flask(__name__)

    if Config_name is None:
        Config_name = os.getenv('FlASK_CONFIG')

    app.config.from_object(Config[Config_name])

    def register_extensions(app):
        login_manager.init_app(app)
        db.init_app(app)
        moment.init_app(app)
        bootstrap.init_app(app)
        csrf.init_app(app)
        mail.init_app(app)
        dropzone.init_app(app)
        avatars.init_app(app)

    def register_errors(app):
        @app.errorhandler(CSRFError)
        def bad_request(e):
            return render_template('errors/400.html', description=e.description), 400

        @app.errorhandler(500)
        def error_handler(e):
            return render_template('errors/500.html', description=e), 500

        @app.errorhandler(404)
        def error_not_found(e):
            return render_template('errors/500.html', description=e), 404

        @app.errorhandler(401)
        def error_not_found(e):
            return render_template('errors/500.html', description=e), 401

    def register_command(app):
        @app.shell_context_processor
        def make_shell_context():
            return dict(db=db)

        @app.cli.command()
        def init():
            """Initialize database"""
            click.echo('Initializing database ')
            db.drop_all()
            db.create_all()
            click.echo('Initialize role permission')
            Role.init_role_permission()
            click.echo('Initialize Done!')

    def register_blueprint(app):
       app.register_blueprint(main_bp)
       app.register_blueprint(auth_bp, url_prefix='/auth')

    register_extensions(app)
    register_errors(app)
    register_blueprint(app)
    register_command(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login firstly'
    login_manager.login_message_category = 'warning'
    login_manager.anonymous_user = Guest

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
