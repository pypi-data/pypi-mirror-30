from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel


class Meta(BaseModel):
    title: str
    description: Optional[str] = None
    authors: List[str] = []
    date: Optional[str] = None


class Hierarchy(BaseModel):
    title: str
    link: str
    children: List = []


class Page(BaseModel):
    meta: Meta
    content: str = ""
    excerpt: Optional[str] = None
    hierarchy: Optional[Hierarchy] = None
    link: str = "#"


class Config(BaseModel):
    locale: str
    site_title: str
    copyright: Optional[str] = None
    content_dir: Path
