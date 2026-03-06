# ============================================
# routes/__init__.py
# ============================================
"""
Routes package for FinOps AI Multi-Agent System.
"""
from flask import Blueprint

# Create blueprints
api_bp = Blueprint('api', __name__, url_prefix='/api')
views_bp = Blueprint('views', __name__)

# Import route handlers (this registers the routes)
from . import api, views

__all__ = ['api_bp', 'views_bp']
