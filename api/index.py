"""
Hilltop Tea — Vercel WSGI Entry Point.

Exports the Flask application for Vercel's Python runtime.
"""
import os
import sys

# Add the parent directory to the path so we can import from the app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run import app

# Vercel expects the WSGI app to be available at module level
# The app is already created in run.py and imported above
