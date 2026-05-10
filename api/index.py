"""
Hilltop Tea — Vercel WSGI Entry Point.

Exports the Flask app for Vercel's Python runtime.
"""
import os

# Set environment for Vercel
os.environ.setdefault('FLASK_ENV', 'production')

from run import app

# Vercel expects the app to be available at module level
__all__ = ['app']
