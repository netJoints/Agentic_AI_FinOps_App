# ============================================
# routes/api.py  
# ============================================
"""
API routes for the application
"""
import asyncio
from datetime import datetime
from flask import request, jsonify
from . import api_bp
from services import FinancialDataService, BritiveClient, AgentCoreClient
from config import Config

@api_bp.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint - orchestrates agents"""
    data = request.json
    query = data.get('query', '')
    session_id = data.get('session_id', f"session-{int(datetime.now().timestamp())}")
    
    if not query:
        return jsonify({"success": False, "error": "Query is required"}), 400
    
    config = Config()
    
    async def process():
        # Initialize Britive client
        britive_client = BritiveClient(
            profile=config.BRITIVE_PROFILE,
            tenant=config.BRITIVE_TENANT
        )
        
        try:
            # Checkout credentials
            britive_client.checkout()
            boto_session = britive_client.get_boto_session()
            
            # Initialize AgentCore client
            agentcore_client = AgentCoreClient(boto_session)
            
            # Orchestrate agents
            return await agentcore_client.orchestrate(query, session_id)
            
        except Exception as e:
            print(f"ERROR in process(): {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            britive_client.checkin()
    
    # Run async operation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(process())
    finally:
        loop.close()
    
    return jsonify(result)

@api_bp.route('/financial-data', methods=['GET'])
def get_financial_data():
    """Get real-time financial data without invoking agents"""
    data_type = request.args.get('type', 'stock')
    symbol = request.args.get('symbol', 'AAPL')
    
    service = FinancialDataService()
    
    if data_type == 'stock':
        return jsonify(service.get_stock_price(symbol))
    elif data_type == 'ratios':
        return jsonify(service.get_financial_ratios(symbol))
    elif data_type == 'multiple':
        symbols = request.args.get('symbols', 'AAPL,MSFT,GOOGL,AMZN').split(',')
        return jsonify(service.get_multiple_stocks(symbols))
    elif data_type == 'transactions':
        return jsonify(service.generate_sample_transactions(20))
    elif data_type == 'compliance':
        return jsonify(service.get_compliance_data())
    
    return jsonify({"error": "Invalid data type"}), 400