from os import environ

import click
from flask import Flask, request, g
from werkzeug.utils import import_string
import flask_babel

from fogstone import views

__all__ = ["create_app"]


def configure_views(app: Flask):
    app.add_url_rule("/", "index", views.index)
    app.add_url_rule("/<path:raw_path>", "content", views.content)
    app.add_url_rule("/search", "search", views.search)


def configure_i18n(app: Flask):
    babel = flask_babel.Babel(app)

    @babel.localeselector
    def get_locale():
        if not request:
            if hasattr(g, 'locale'):
                return g.locale
            raise RuntimeError('Babel is used outside of request context, please set g.locale')
        locales = app.config['LOCALES'].keys()
        locale = request.cookies.get('locale')
        if locale in locales:
            return locale
        return request.accept_languages.best_match(locales)

    @app.before_request
    def before_request():
        g.locale = flask_babel.get_locale()


def create_app() -> Flask:
    try:
        settings_key = environ["FOGSTONE_SETTINGS"]
    except KeyError:
        settings_key = "fogstone.settings.Config"
        click.echo(click.style(f"FOGSTONE_SETTINGS is empty, assuming {settings_key}", fg="yellow"))

    config_object = import_string(settings_key)
    app = Flask(
        __name__,
        template_folder=config_object.TEMPLATE_FOLDER.as_posix(),
        static_folder=config_object.STATIC_FOLDER.as_posix(),
    )
    app.config.from_object(settings_key)
    configure_views(app)
    configure_i18n(app)

    return app
