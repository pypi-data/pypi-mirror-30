# -*- coding: utf-8 -*-

"""Main module."""
from .fontawesome import fontawesome
from .fileextensions import extensions


class ftfa:
    def __init__(self, fontversion="v5regular", markup=False, prefa=True):
        self.file_categories = (
            "word",
            "code",
            "video",
            "audio",
            "archive",
            "image",
            "powerpoint",
            "excel",
            "word",
            "pdf",
            "text")
        self.fontversion = fontversion
        self.markup = markup
        self.prefa = prefa

    def getfontawesome(self, filename):
        category = "unknown"
        if '.' in filename:
            file_extension = filename.split('.')[-1]
            for cat in self.file_categories:
                if file_extension in getattr(extensions, cat)().get_types():
                    category = cat
                    break

        fv = getattr(fontawesome, self.fontversion)()
        return fv.get(category, markup=self.markup, prefa=self.prefa)
