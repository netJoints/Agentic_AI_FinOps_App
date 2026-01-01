# ============================================
# routes/views.py
# ============================================
"""
Web views for the application
"""
from flask import render_template
from . import views_bp


@views_bp.route('/')
def home():
    """Main page"""
    return render_template('index.html')
