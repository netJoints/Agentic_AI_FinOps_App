# ============================================
# app.py - Main Application (FIXED)
# ============================================
"""
FinOps AI Multi-Agent System
Main Flask application entry point.

Author: Shahzad Ali
Version: 2.0.0
"""
from dotenv import load_dotenv
load_dotenv()

# CRITICAL: Import log handler FIRST, before anything else that logs
from services.logs_handler import log_handler

from flask import Flask
from flask_cors import CORS
import logging
import sys

from config import Config
from routes import api_bp, views_bp


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        log_handler
    ]
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config) -> Flask:
    """
    Application factory pattern.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for API access
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)
    
    # Add the logs route HERE
    @app.route('/api/logs', methods=['GET'])
    def get_logs():
        """Get recent logs"""
        from flask import request, jsonify
        limit = request.args.get('limit', type=int, default=100)
        logs = log_handler.get_logs(limit)
        return jsonify({'logs': logs})
    
    # Log registered routes
    logger.info("📋 Registered routes:")
    for rule in app.url_map.iter_rules():
        logger.info(f"   {rule.methods} {rule.rule}")
    
    return app


def print_banner():
    """Print startup banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🏦  FinOps AI Multi-Agent System  🏦                          ║
║                                                                  ║
║   Powered by Amazon Bedrock AgentCore                           ║
║   Real-time Financial Data via Yahoo Finance                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def check_prerequisites():
    """Check that prerequisites are available."""
    issues = []
    
    # Check yfinance
    try:
        import yfinance
        logger.info("✅ yfinance available")
    except ImportError:
        issues.append("yfinance not installed (pip install yfinance)")
    
    # Check pybritive
    import subprocess
    try:
        result = subprocess.run(["pybritive", "--version"], capture_output=True, timeout=5)
        if result.returncode == 0:
            logger.info("✅ pybritive available")
        else:
            issues.append("pybritive not working properly")
    except FileNotFoundError:
        issues.append("pybritive not installed (pip install pybritive)")
    except subprocess.TimeoutExpired:
        issues.append("pybritive timeout")
    
    # Check boto3
    try:
        import boto3
        logger.info("✅ boto3 available")
    except ImportError:
        issues.append("boto3 not installed (pip install boto3)")
    
    # Check agent configuration
    config = Config()
    configured = config.get_all_configured_agents()
    if configured:
        logger.info(f"✅ Configured agents: {', '.join(configured)}")
    else:
        issues.append("No agents configured - update config.py with agent IDs")
    
    return issues


if __name__ == '__main__':
    print_banner()
    # Test log to verify handler is working
    logger.info("🎯 TEST LOG - App starting up!")
    
    # Check prerequisites
    logger.info("🔍 Checking prerequisites...")
    issues = check_prerequisites()
    
    if issues:
        logger.warning("⚠️ Some issues found:")
        for issue in issues:
            logger.warning(f"   - {issue}")
        logger.warning("The app will start but some features may not work.")
    else:
        logger.info("✅ All prerequisites satisfied")
    
    # Create and run app
    logger.info(f"🚀 Starting server on http://{Config.HOST}:{Config.PORT}")
    
    app = create_app()
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )


