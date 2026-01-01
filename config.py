# ============================================
# config.py - Configuration
# ============================================
import os
from datetime import timedelta

class Config:
    """Application configuration"""
    
    # Flask settings
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5011
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # AWS settings
    AWS_REGION = 'us-west-2'
    AWS_ACCOUNT_ID = '513826297540'
    
    # Britive settings
    BRITIVE_PROFILE = "aws_standalone_app_513826297540/513826297540 (aws_standalone_app_513826297540_environment)/FinOps Agentic AI Agent"
    BRITIVE_TENANT = "agentic-ai"
    
    # AgentCore Agent Configuration
    # Populated from .bedrock_agentcore.yaml
    AGENTS = {
        "supervisor": {
            "agent_id": os.environ.get("SUPERVISOR_AGENT_ID", "finops_supervisor_ai_agent-QJhB67D4O4"),
            "agent_arn": "arn:aws:bedrock-agentcore:us-west-2:513826297540:runtime/finops_supervisor_ai_agent-QJhB67D4O4",
            "session_id": "74514430-a5c6-4a86-b00f-48760d6cb8d3"
        },
        "fraud_detection": {
            "agent_id": os.environ.get("FRAUD_AGENT_ID", "finops_fraud_ai_agent-cTzcGF6lW7"),
            "agent_arn": "arn:aws:bedrock-agentcore:us-west-2:513826297540:runtime/finops_fraud_ai_agent-cTzcGF6lW7",
            "session_id": "8cb2450a-32d0-4eea-b306-e78d4eee9f68"
        },
        "compliance": {
            "agent_id": os.environ.get("COMPLIANCE_AGENT_ID", "finops_compliance_ai_agent-lCD0fT7TCE"),
            "agent_arn": "arn:aws:bedrock-agentcore:us-west-2:513826297540:runtime/finops_compliance_ai_agent-lCD0fT7TCE",
            "session_id": "20d20a9d-de17-4801-be95-fe32b91e342b"
        },
        "risk_analysis": {
            "agent_id": os.environ.get("RISK_AGENT_ID", "finops_risk_ai_agent-W2U22y3F6H"),
            "agent_arn": "arn:aws:bedrock-agentcore:us-west-2:513826297540:runtime/finops_risk_ai_agent-W2U22y3F6H",
            "session_id": "4d58b052-baf6-4f9f-b1ea-a9961baa06ae"
        }
    }
    
    # Execution Role
    BEDROCK_EXECUTION_ROLE = "arn:aws:iam::513826297540:role/service-role/AmazonBedrockAgentCoreRuntimeServiceRole-shahzad"
    
    # API Keys (optional - yfinance is free!)
    API_KEYS = {
        "finnhub": os.environ.get("FINNHUB_API_KEY", "demo"),
        "twelve_data": os.environ.get("TWELVE_DATA_API_KEY", "demo")
    }
    
    # Data refresh intervals
    DASHBOARD_REFRESH_INTERVAL = 30  # seconds
    
    # Transaction settings
    DEFAULT_TRANSACTION_COUNT = 10
    FRAUD_THRESHOLD = 0.7


# ============================================
# Project Structure
# ============================================
"""
finops_app/
├── app.py                      # Main Flask application
├── config.py                   # Configuration and constants
├── services/
│   ├── __init__.py
│   ├── financial_data.py       # Financial data fetching service
│   ├── britive_client.py       # Britive credential management
│   └── agentcore_client.py     # AgentCore agent invocation
├── routes/
│   ├── __init__.py
│   ├── api.py                  # API endpoints
│   └── views.py                # Web views
├── templates/
│   └── index.html              # HTML template
├── static/
│   ├── css/
│   │   └── styles.css          # Styles
│   └── js/
│       └── main.js             # Frontend JavaScript
└── requirements.txt            # Dependencies
"""