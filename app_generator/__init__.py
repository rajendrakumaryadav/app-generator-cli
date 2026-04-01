"""PyForge CLI package."""

from importlib.metadata import metadata

try:
	_meta = metadata("app-generator-cli")
except Exception:
	_meta = metadata("pyforge-cli")
__version__ = _meta["Version"]
__author__ = _meta["Author-email"]
