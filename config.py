# ============================================
# config.py - Configuration (Enhanced - Backwards Compatible)
# ============================================
import os

class Config:
    """Application configuration"""
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5011))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # AWS settings
    AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')
    AWS_ACCOUNT_ID = os.environ.get('AWS_ACCOUNT_ID', '')

    # Britive settings (legacy - maintained for backwards compatibility)
    BRITIVE_PROFILE = os.environ.get('BRITIVE_PROFILE', '')
    BRITIVE_TENANT = os.environ.get('BRITIVE_TENANT', '')
    BRITIVE_REGION = os.environ.get('BRITIVE_REGION', 'us-west-2')

    # NEW: Agent-specific Britive profiles
    # Maps agent names to their specific Britive profiles
    BRITIVE_PROFILES = {
        'supervisor': {
            'profile': os.environ.get('BRITIVE_PROFILE_SUPERVISOR', ''),
            'tenant': os.environ.get('BRITIVE_TENANT', ''),
            'description': 'Supervisor agent - coordinates other agents'
        },
        'fraud_detection': {
            'profile': os.environ.get('BRITIVE_PROFILE_FRAUD', ''),
            'tenant': os.environ.get('BRITIVE_TENANT', ''),
            'description': 'Fraud detection specialist'
        },
        'compliance': {
            'profile': os.environ.get('BRITIVE_PROFILE_COMPLIANCE', ''),
            'tenant': os.environ.get('BRITIVE_TENANT', ''),
            'description': 'Compliance and regulatory checks'
        },
        'risk_analysis': {
            'profile': os.environ.get('BRITIVE_PROFILE_RISK', ''),
            'tenant': os.environ.get('BRITIVE_TENANT', ''),
            'description': 'Risk assessment and analysis'
        }
    }
    
    # Default profile if agent not found in mapping
    BRITIVE_DEFAULT_PROFILE = {
        'profile': BRITIVE_PROFILE,  # Use legacy profile as default
        'tenant': BRITIVE_TENANT,
        'description': 'Default fallback profile'
    }
    
    # AgentCore Agent Configuration
    # These use the Bedrock AgentCore Runtime ARNs - set all values via .env
    AGENTS = {
        "supervisor": {
            "agent_id": os.environ.get("SUPERVISOR_AGENT_ID", ""),
            "agent_arn": os.environ.get("SUPERVISOR_AGENT_ARN", ""),
        },
        "fraud_detection": {
            "agent_id": os.environ.get("FRAUD_AGENT_ID", ""),
            "agent_arn": os.environ.get("FRAUD_AGENT_ARN", ""),
        },
        "compliance": {
            "agent_id": os.environ.get("COMPLIANCE_AGENT_ID", ""),
            "agent_arn": os.environ.get("COMPLIANCE_AGENT_ARN", ""),
        },
        "risk_analysis": {
            "agent_id": os.environ.get("RISK_AGENT_ID", ""),
            "agent_arn": os.environ.get("RISK_AGENT_ARN", ""),
        }
    }

    # Execution Role
    BEDROCK_EXECUTION_ROLE = os.environ.get('BEDROCK_EXECUTION_ROLE', '')
    
    # Data refresh intervals (UNCHANGED)
    DASHBOARD_REFRESH_INTERVAL = 30  # seconds
    
    # Transaction settings (UNCHANGED)
    DEFAULT_TRANSACTION_COUNT = 10
    FRAUD_THRESHOLD = 0.7
    
    # EXISTING METHODS (UNCHANGED - working as-is)
    @classmethod
    def is_agent_configured(cls, agent_type: str) -> bool:
        """Check if an agent is properly configured"""
        agent = cls.AGENTS.get(agent_type, {})
        agent_id = agent.get("agent_id", "")
        return agent_id and not agent_id.startswith("YOUR_")
    
    @classmethod
    def get_all_configured_agents(cls) -> list:
        """Return list of all configured agent names"""
        return [name for name in cls.AGENTS.keys() if cls.is_agent_configured(name)]
    
    # NEW METHODS (added for Britive profile management)
    @classmethod
    def get_britive_profile(cls, agent_name: str) -> dict:
        """
        Get Britive profile configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            dict: Profile configuration with 'profile', 'tenant', and 'description'
        """
        return cls.BRITIVE_PROFILES.get(agent_name, cls.BRITIVE_DEFAULT_PROFILE)
    
    @classmethod
    def get_agent_britive_info(cls) -> dict:
        """
        Get information about Britive profiles for all agents.
        
        Returns:
            dict: Agent names mapped to their profile descriptions
        """
        return {
            name: config['description'] 
            for name, config in cls.BRITIVE_PROFILES.items()
        }