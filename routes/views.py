# ============================================
# routes/views.py
# ============================================
"""
Web views for the FinOps AI Multi-Agent System.
"""
from flask import render_template
from . import views_bp


@views_bp.route('/')
def home():
    """Main page - renders the dashboard UI."""
    return render_template('index.html')


@views_bp.route('/health')
def health_page():
    """Simple health check page."""
    return "OK", 200
