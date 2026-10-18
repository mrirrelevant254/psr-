"""Vercel serverless entry point."""
import os
import sys

# Add the parent directory to the path so Vercel can find your 'app' folder
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app

# Create the app specifically for Vercel
app = create_app()