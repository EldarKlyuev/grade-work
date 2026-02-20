"""Конфигурация Sphinx для grade-work документации."""
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Информация о проекте -----------------------------------------------------
project = "grade-work"
copyright = "2026, grade-work team"
author = "grade-work team"
release = "0.1.0"

# -- Основные настройки -------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "ru"

# -- Настройки HTML вывода ----------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    "navigation_depth": 4,
    "titles_only": False,
}

# -- Настройки autodoc --------------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# -- Настройки napoleon -------------------------------------------------------
napoleon_google_docstring = False
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True

# -- Настройки typehints ------------------------------------------------------
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True

# -- Intersphinx mapping ------------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/20/", None),
    "fastapi": ("https://fastapi.tiangolo.com/", None),
}
