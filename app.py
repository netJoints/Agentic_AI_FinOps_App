# ============================================
# app.py - Main application
# Shahzad Ali | FinOps AI Multi-Agent System | September 2025
# ============================================
"""
Main Flask application - FinOps AI Multi-Agent System
"""
from flask import Flask
from flask_cors import CORS
from config import Config
from routes import api_bp, views_bp
from services.startup import StartupManager
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)
    
    return app


if __name__ == '__main__':
    print("🚀 Starting Finance AI Multi-Agent System...")
    print("📋 Initializing AWS credentials and agents...")
    
    # Run startup tasks
    startup = StartupManager(
        britive_profile=Config.BRITIVE_PROFILE,
        britive_tenant=Config.BRITIVE_TENANT
    )
    
    if not startup.run_startup_tasks():
        print("❌ Startup failed! Please check logs.")
        exit(1)
    
    print("💰 Using Yahoo Finance (yfinance) - FREE & Unlimited!")
    print(f"\n✅ Starting server on http://localhost:{Config.PORT}\n")
    
    app = create_app()
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )