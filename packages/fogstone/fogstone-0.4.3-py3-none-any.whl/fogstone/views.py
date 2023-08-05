from flask import render_template, abort, request, current_app
from flask_babel import gettext

from fogstone.logic import construct_path, read_content, read_hierarchy, locate_page


def content(raw_path):
    path = construct_path(raw_path)
    if path is None:
        abort(404)

    page = read_content(path)

    hierarchy = read_hierarchy(current_app.config["CONTENT_DIR"], recursive=True)
    sidebar = locate_page(hierarchy, page)

    return render_template(
        "page.html",
        site_title=current_app.config["SITE_TITLE"],
        page_title=page.meta.title,
        page=page,
        sidebar=sidebar,
    )


def index():
    path = construct_path("/index")
    if path is None:
        abort(404)

    page = read_content(path)

    return render_template(
        "page.html",
        site_title=current_app.config["SITE_TITLE"],
        page_title=page.meta.title,
        page=page,
    )


def search():
    search_request = request.args.get("q")

    sidebar = read_hierarchy(current_app.config["CONTENT_DIR"], recursive=True)

    return render_template(
        "search.html",
        site_title=current_app.config["SITE_TITLE"],
        page_title=gettext("Search"),
        sidebar=sidebar,
        results=[],
        search=search_request
    )
