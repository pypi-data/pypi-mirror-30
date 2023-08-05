from pathlib import Path


class Config(object):
    LOCALES = {
        "en": "English",
        "ru": "Русский",
    }
    DEBUG = False
    SECRET_KEY = "kjmhg345bjknhg7jhKGM98KNJKv1nMKJH3YNG2bjvn326jmh"

    SITE_TITLE = "FogStone"
    CONTENT_DIR = Path(__file__).parent / Path("data")
    TEMPLATE_FOLDER = Path("templates")
    STATIC_FOLDER = Path("static")
