# ============================================
# services/britive_helper.py
# ============================================
"""
Helper functions for managing agent-specific Britive credentials.
"""
import logging
from typing import Optional
from services.britive_client import BritiveClient
from config import Config

logger = logging.getLogger(__name__)


def get_britive_client_for_agent(agent_name: str, region: str = None) -> BritiveClient:
    """
    Get a BritiveClient configured for a specific agent.
    
    Args:
        agent_name: Name of the agent (supervisor, fraud_detection, compliance, risk_analysis, fraud_and_risk)
        region: AWS region (uses config default if not provided)
    
    Returns:
        BritiveClient instance configured for the agent
        
    Example:
        client = get_britive_client_for_agent('fraud_detection')
        if client.checkout():
            session = client.get_boto_session()
            # Use session...
            client.checkin()
    """
    if region is None:
        region = Config.BRITIVE_REGION
    
    # Get profile configuration for this agent
    profile_config = Config.get_britive_profile(agent_name)
    
    logger.info(f"🎯 Configuring Britive client for agent: {agent_name}")
    logger.info(f"   Description: {profile_config['description']}")
    
    return BritiveClient(
        profile=profile_config['profile'],
        tenant=profile_config['tenant'],
        region=region
    )


def checkout_credentials_for_agent(agent_name: str, region: str = None) -> Optional[BritiveClient]:
    """
    Checkout Britive credentials for a specific agent.
    Automatically handles the checkout process.
    
    Args:
        agent_name: Name of the agent
        region: AWS region (optional)
    
    Returns:
        BritiveClient with checked out credentials, or None if failed
        
    Example:
        client = checkout_credentials_for_agent('compliance')
        if client:
            try:
                session = client.get_boto_session()
                # Do work with session...
            finally:
                client.checkin()
    """
    client = get_britive_client_for_agent(agent_name, region)
    
    logger.info(f"🔐 Checking out credentials for {agent_name} agent...")
    
    if client.checkout():
        logger.info(f"✅ Successfully checked out credentials for {agent_name}")
        if client.verify_credentials():
            return client
        else:
            logger.error(f"❌ Credential verification failed for {agent_name}")
            client.checkin()
            return None
    else:
        logger.error(f"❌ Failed to checkout credentials for {agent_name}")
        return None


def get_boto_session_for_agent(agent_name: str, region: str = None):
    """
    Context manager for getting a boto3 session with agent-specific credentials.
    Automatically handles checkout and checkin.
    
    Args:
        agent_name: Name of the agent
        region: AWS region (optional)
        
    Yields:
        boto3.Session: Session with agent-specific credentials
        
    Example:
        with get_boto_session_for_agent('fraud_detection') as session:
            bedrock = session.client('bedrock-agent-runtime')
            # Use bedrock client...
    """
    client = checkout_credentials_for_agent(agent_name, region)
    
    if not client:
        raise Exception(f"Failed to checkout credentials for agent: {agent_name}")
    
    try:
        yield client.get_boto_session()
    finally:
        logger.info(f"🔓 Checking in credentials for {agent_name}")
        client.checkin()


def list_configured_agents() -> dict:
    """
    Get information about all configured agents.
    
    Returns:
        dict: Agent names mapped to their descriptions
        
    Example:
        agents = list_configured_agents()
        for name, description in agents.items():
            print(f"{name}: {description}")
    """
    return Config.get_agent_info()


def validate_agent_name(agent_name: str) -> bool:
    """
    Check if an agent name is valid/configured.
    
    Args:
        agent_name: Name to validate
        
    Returns:
        bool: True if agent is configured
    """
    return agent_name in Config.list_available_agents()
