# ============================================
# routes/api.py - Enhanced with Agent-Specific Profiles
# ============================================
"""
API routes for the FinOps AI Multi-Agent System.
Now supports agent-specific Britive profiles.
"""
from datetime import datetime
from flask import request, jsonify
import logging

from . import api_bp
from services import FinancialDataService, BritiveClient, AgentCoreClient
from services.britive_helper import checkout_credentials_for_agent, get_britive_client_for_agent
from config import Config

logger = logging.getLogger(__name__)

# Initialize services at module level (reused across requests)
config = Config()
financial_service = FinancialDataService()


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "agents_configured": config.get_all_configured_agents(),
        "britive_profiles_configured": list(config.BRITIVE_PROFILES.keys())
    })


@api_bp.route('/agents', methods=['GET'])
def list_agents():
    """List available agents and their configuration status."""
    agents_info = {}
    for name, agent_config in config.AGENTS.items():
        # Get Britive profile info for this agent
        britive_profile = config.get_britive_profile(name)
        
        agents_info[name] = {
            "configured": config.is_agent_configured(name),
            "agent_id": agent_config.get("agent_id", "NOT SET"),
            "britive_profile": britive_profile['description']
        }
    
    return jsonify({
        "agents": agents_info,
        "total": len(config.AGENTS),
        "configured": len(config.get_all_configured_agents())
    })


@api_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint - orchestrates AI agents based on query content.
    Now uses agent-specific Britive profiles.
    
    Request body:
        {
            "query": "Your analysis query",
            "session_id": "optional-session-id",
            "agent": "optional-specific-agent-name"  # NEW: Can specify which agent to use
        }
    
    Returns:
        {
            "success": true/false,
            "response": "Combined agent responses",
            "agents_invoked": ["agent1", "agent2"],
            "session_id": "session-id"
        }
    """
    # Parse request
    data = request.get_json(silent=True) or {}
    query = data.get('query', '').strip()
    session_id = data.get('session_id') or f"session-{int(datetime.now().timestamp() * 1000)}-{hash(query) % 10000}"
    requested_agent = data.get('agent')  # Optional: specific agent to use
    
    # Validate input
    if not query:
        return jsonify({"success": False, "error": "Query is required"}), 400
    
    if len(query) > 10000:
        return jsonify({"success": False, "error": "Query too long (max 10000 chars)"}), 400
    
    logger.info(f"📝 Analyze request: {query[:100]}...")
    logger.info(f"🔑 Session: {session_id}")
    
    # Determine which agent to use (default: supervisor)
    agent_name = requested_agent if requested_agent else 'supervisor'
    
    if agent_name not in config.AGENTS:
        return jsonify({
            "success": False,
            "error": f"Unknown agent: {agent_name}",
            "available_agents": list(config.AGENTS.keys())
        }), 400
    
    logger.info(f"🤖 Using agent: {agent_name}")
    
    # Checkout credentials for the specific agent
    britive_client = checkout_credentials_for_agent(agent_name)
    
    if not britive_client:
        return jsonify({
            "success": False,
            "error": f"Failed to checkout credentials for {agent_name} agent. Check Britive configuration."
        }), 500
    
    try:
        # Get boto session and create AgentCore client
        boto_session = britive_client.get_boto_session()
        agentcore_client = AgentCoreClient(boto_session)
        
        # Orchestrate agents (synchronous)
        # The AgentCoreClient will coordinate with other agents as needed
        result = agentcore_client.orchestrate(query, session_id)
        
        logger.info(f"✅ Analysis complete: {len(result.get('agents_invoked', []))} agents")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }), 500
        
    finally:
        # Always checkin credentials
        logger.info(f"🔓 Checking in credentials for {agent_name}")
        britive_client.checkin()


@api_bp.route('/analyze-multi', methods=['POST'])
def analyze_multi():
    """
    NEW ENDPOINT: Invoke multiple specific agents with their own profiles.
    
    Request body:
        {
            "query": "Your analysis query",
            "agents": ["fraud_detection", "compliance"],  # List of agents to invoke
            "session_id": "optional-session-id"
        }
    """
    data = request.get_json(silent=True) or {}
    query = data.get('query', '').strip()
    agent_names = data.get('agents', [])
    session_id = data.get('session_id') or f"session-{int(datetime.now().timestamp() * 1000)}"
    
    if not query:
        return jsonify({"success": False, "error": "Query is required"}), 400
    
    if not agent_names:
        return jsonify({"success": False, "error": "At least one agent must be specified"}), 400
    
    # Validate all requested agents
    invalid_agents = [a for a in agent_names if a not in config.AGENTS]
    if invalid_agents:
        return jsonify({
            "success": False,
            "error": f"Unknown agents: {invalid_agents}",
            "available_agents": list(config.AGENTS.keys())
        }), 400
    
    logger.info(f"📝 Multi-agent analyze: {query[:100]}...")
    logger.info(f"🤖 Invoking agents: {agent_names}")
    
    results = {}
    agents_invoked = []
    
    # Invoke each agent with its specific profile
    for agent_name in agent_names:
        logger.info(f"🎯 Invoking {agent_name}...")
        
        # Checkout credentials for this specific agent
        britive_client = checkout_credentials_for_agent(agent_name)
        
        if not britive_client:
            results[agent_name] = {
                "success": False,
                "error": f"Failed to checkout credentials for {agent_name}"
            }
            continue
        
        try:
            # Get boto session and create AgentCore client
            boto_session = britive_client.get_boto_session()
            agentcore_client = AgentCoreClient(boto_session)
            
            # Invoke this specific agent
            agent_result = agentcore_client.invoke_single_agent(
                agent_name=agent_name,
                query=query,
                session_id=f"{session_id}-{agent_name}"
            )
            
            results[agent_name] = agent_result
            agents_invoked.append(agent_name)
            logger.info(f"✅ {agent_name} complete")
            
        except Exception as e:
            logger.error(f"❌ {agent_name} failed: {e}")
            results[agent_name] = {
                "success": False,
                "error": str(e)
            }
        
        finally:
            # Always checkin credentials
            britive_client.checkin()
    
    return jsonify({
        "success": len(agents_invoked) > 0,
        "session_id": session_id,
        "agents_invoked": agents_invoked,
        "results": results
    })


@api_bp.route('/financial-data', methods=['GET'])
def get_financial_data():
    """
    Get real-time financial data without invoking AI agents.
    
    Query parameters:
        type: stock, ratios, multiple, transactions, compliance, market
        symbol: Stock symbol (default: AAPL)
        symbols: Comma-separated symbols for 'multiple' type
    """
    data_type = request.args.get('type', 'stock')
    symbol = request.args.get('symbol', 'AAPL').upper()
    
    # Basic symbol validation
    if data_type in ['stock', 'ratios'] and (not symbol.isalpha() or len(symbol) > 5):
        return jsonify({"error": f"Invalid stock symbol: {symbol}"}), 400
    
    try:
        if data_type == 'stock':
            return jsonify(financial_service.get_stock_price(symbol))
        
        elif data_type == 'ratios':
            return jsonify(financial_service.get_financial_ratios(symbol))
        
        elif data_type == 'multiple':
            symbols_str = request.args.get('symbols', 'AAPL,MSFT,GOOGL,AMZN')
            symbols = [s.strip().upper() for s in symbols_str.split(',')]
            return jsonify(financial_service.get_multiple_stocks(symbols))
        
        elif data_type == 'transactions':
            count = min(int(request.args.get('count', 20)), 100)  # Max 100
            return jsonify(financial_service.generate_sample_transactions(count))
        
        elif data_type == 'compliance':
            return jsonify(financial_service.get_compliance_data())
        
        elif data_type == 'market':
            return jsonify(financial_service.get_market_summary())
        
        else:
            return jsonify({
                "error": f"Invalid data type: {data_type}",
                "valid_types": ["stock", "ratios", "multiple", "transactions", "compliance", "market"]
            }), 400
            
    except Exception as e:
        logger.error(f"Error fetching financial data: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/test-credentials', methods=['GET'])
def test_credentials():
    """
    Test endpoint to verify Britive credentials are working.
    Now tests agent-specific profiles.
    
    Query parameters:
        agent: Optional agent name to test (default: supervisor)
    """
    agent_name = request.args.get('agent', 'supervisor')
    
    if agent_name not in config.AGENTS:
        return jsonify({
            "success": False,
            "error": f"Unknown agent: {agent_name}",
            "available_agents": list(config.AGENTS.keys())
        }), 400
    
    logger.info(f"🧪 Testing credentials for agent: {agent_name}")
    
    # Get profile info
    profile_config = config.get_britive_profile(agent_name)
    
    try:
        # Use the helper to checkout credentials for this agent
        britive_client = checkout_credentials_for_agent(agent_name)
        
        if not britive_client:
            return jsonify({
                "success": False,
                "agent": agent_name,
                "step": "checkout",
                "error": "Failed to checkout Britive credentials",
                "profile": profile_config['profile'],
                "tenant": profile_config['tenant']
            }), 500
        
        # Credentials already verified by checkout_credentials_for_agent
        return jsonify({
            "success": True,
            "agent": agent_name,
            "checkout": True,
            "verify": True,
            "profile": profile_config['profile'],
            "tenant": profile_config['tenant'],
            "description": profile_config['description']
        })
        
    except Exception as e:
        logger.error(f"❌ Credential test failed: {e}")
        return jsonify({
            "success": False,
            "agent": agent_name,
            "error": str(e)
        }), 500
        
    finally:
        if britive_client:
            britive_client.checkin()


@api_bp.route('/britive-profiles', methods=['GET'])
def list_britive_profiles():
    """
    NEW ENDPOINT: List all configured Britive profiles.
    """
    profiles_info = {}
    
    for agent_name, profile_config in config.BRITIVE_PROFILES.items():
        profiles_info[agent_name] = {
            "profile": profile_config['profile'],
            "tenant": profile_config['tenant'],
            "description": profile_config['description'],
            "agent_configured": config.is_agent_configured(agent_name)
        }
    
    return jsonify({
        "profiles": profiles_info,
        "total": len(config.BRITIVE_PROFILES),
        "default_profile": config.BRITIVE_DEFAULT_PROFILE
    })