import re
from os import environ
from typing import Callable

import click
from flask import Flask, Config, request, g
from werkzeug.utils import import_string
import flask_babel

from markdown import Markdown
from pyembed.markdown import PyEmbedMarkdown
from markdown.extensions.toc import TocExtension
import unicodedata
from transliterate.decorators import transliterate_function


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


def get_slugify(config: Config) -> Callable[[str, str], str]:
    def func(value: str, separator: str):
        value = unicodedata.normalize("NFKD", value)
        value = re.sub(r"[^\w\s-]", "", value).strip().lower()
        return re.sub(r"[%s\s]+" % separator, separator, value)

    if config["TRANSLIT_PERMALINKS"]:
        return transliterate_function(
            language_code=config["TRANSLIT_CODE"],
            reversed=config["TRANSLIT_REVERSE"]
        )(func)
    else:
        return func


def configure_md(app: Flask):
    app.MD = Markdown(extensions=[
        "markdown.extensions.meta",
        "markdown.extensions.extra",
        "markdown.extensions.sane_lists",
        "markdown.extensions.toc",
        PyEmbedMarkdown(),
        TocExtension(
            baselevel=2,
            permalink=True,
            slugify=get_slugify(app.config),
            separator="_"
        )
    ])


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
    configure_md(app)

    return app
