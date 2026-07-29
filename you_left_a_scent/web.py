"""Backward-compatible ASGI entry point for the web app."""

from .webapp.app import app

__all__ = ["app"]
