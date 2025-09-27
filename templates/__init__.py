# templates/__init__.py
"""
HTML шаблоны приложения
"""
from .main_app import get_main_app_template, get_root_page_template
from .category_app import get_category_app_template

__all__ = ["get_main_app_template", "get_root_page_template", "get_category_app_template"]
