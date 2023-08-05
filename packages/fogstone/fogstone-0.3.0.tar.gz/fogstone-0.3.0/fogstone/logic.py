import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import current_app

from fogstone.models import Meta, Page, Hierarchy

PATH_REGEX = re.compile("^[\w_-]+$")
SPEC_SYMBOL_REGEX = re.compile("[\W_-]")
LOCAL_ROOT = Path(".")


def construct_path(raw_path: str) -> Optional[Path]:
    raw_chunks = [c for c in raw_path.split("/") if c]
    if not all(PATH_REGEX.match(chunk) for chunk in raw_chunks):
        return None
    naive_path = (current_app.config["CONTENT_DIR"] / Path(*raw_chunks)).resolve()

    if naive_path.exists():
        return naive_path

    naive_path = naive_path.with_suffix(".md")

    if naive_path.exists():
        return naive_path


def make_link(path: Path) -> str:
    if path == LOCAL_ROOT or path == current_app.config["CONTENT_DIR"]:
        return "/"
    else:
        return ("/" / path.relative_to(current_app.config["CONTENT_DIR"])).with_suffix('').as_posix()


def title_from_path(path: Path) -> str:
    return SPEC_SYMBOL_REGEX.sub(" ", path.stem).capitalize()


def mtime_from_path(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")


def read_hierarchy(path: Path, recursive=False) -> Hierarchy:
    title = title_from_path(path)
    link = make_link(path)
    children = [
        read_hierarchy(p, recursive=recursive)
        for p in path.glob("*")
        if (True if recursive else p.is_file())
        and p.stem.lower() != "index"
    ]
    return Hierarchy(title=title, link=link, children=children)


def read_file(path: Path) -> Page:
    raw_content = path.read_text("utf-8")
    html = current_app.MD.convert(raw_content)
    meta = Meta(
        title=current_app.MD.Meta.get("title", [title_from_path(path)])[0],
        description=current_app.MD.Meta.get("description", [None])[0],
        authors=current_app.MD.Meta.get("authors", []),
        date=current_app.MD.Meta.get("date", [mtime_from_path(path)])[0]
    )
    return Page(content=html, meta=meta, link=make_link(path))


def read_catalog(path: Path) -> Page:
    index_path = path / "index.md"

    if index_path.exists():
        return read_file(index_path)
    else:
        return Page(
            meta=Meta(title=title_from_path(path), date=mtime_from_path(path)),
            link=make_link(path),
            hierarchy=read_hierarchy(path)
        )


def read_content(path: Path) -> Page:
    return read_catalog(path) if path.is_dir() else read_file(path)
