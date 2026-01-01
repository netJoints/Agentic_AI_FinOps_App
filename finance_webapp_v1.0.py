#!/Users/shahzadali/Github/Agentic_AI_FinOps_Bedrock_AgentCore/pyvenv/bin/python
# ============================================
# Enhanced Finance Web App with Real Financial Data APIs
# Single File App
# This is the starting point before making a full stack app
# ============================================
"""
Enhanced web app that uses AgentCore with real financial data from free APIs
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import asyncio
import boto3
from datetime import datetime, timedelta
import subprocess
import json
import requests
from typing import Dict, List

app = Flask(__name__)
CORS(app)

# API Configuration - Add your API keys here (optional - yfinance is free!)
API_KEYS = {
    "finnhub": "demo",  # Optional: Get free key from https://finnhub.io/ (60 calls/min)
    "twelve_data": "demo"  # Optional: Get free key from https://twelvedata.com/ (800 calls/day)
}

# Import yfinance for unlimited free stock data
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance not installed. Run: pip install yfinance")

# AgentCore Agent IDs (update these after deployment)
AGENTS = {
    "supervisor": {
        "agent_id": "YOUR_SUPERVISOR_AGENT_ID",
        "alias_id": "YOUR_SUPERVISOR_ALIAS_ID"
    },
    "fraud_detection": {
        "agent_id": "YOUR_FRAUD_AGENT_ID",
        "alias_id": "YOUR_FRAUD_ALIAS_ID"
    },
    "compliance": {
        "agent_id": "YOUR_COMPLIANCE_AGENT_ID", 
        "alias_id": "YOUR_COMPLIANCE_ALIAS_ID"
    },
    "risk_analysis": {
        "agent_id": "YOUR_RISK_AGENT_ID",
        "alias_id": "YOUR_RISK_ALIAS_ID"
    }
}

class FinancialDataService:
    """Service to fetch real financial data from free APIs"""
    
    @staticmethod
    def get_stock_price(symbol: str = "AAPL") -> Dict:
        """Get real-time stock price using Yahoo Finance (FREE, unlimited)"""
        if not YFINANCE_AVAILABLE:
            return {"symbol": symbol, "price": 0, "error": "yfinance not installed"}
        
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="1d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                open_price = hist['Open'].iloc[-1]
                change = current_price - open_price
                change_percent = (change / open_price) * 100
                
                return {
                    "symbol": symbol,
                    "price": float(current_price),
                    "change": float(change),
                    "change_percent": f"{change_percent:+.2f}%",
                    "volume": int(hist['Volume'].iloc[-1]),
                    "timestamp": str(hist.index[-1]),
                    "market_cap": info.get('marketCap', 0),
                    "pe_ratio": info.get('trailingPE', 0)
                }
        except Exception as e:
            print(f"Error fetching stock price: {e}")
        
        return {"symbol": symbol, "price": 0, "error": "Unable to fetch data"}
    
    @staticmethod
    def get_financial_ratios(symbol: str = "AAPL") -> Dict:
        """Get financial ratios using Yahoo Finance (FREE, unlimited)"""
        if not YFINANCE_AVAILABLE:
            return {"symbol": symbol, "error": "yfinance not installed"}
        
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            
            # Calculate ratios from financial statements
            ratios = {
                "symbol": symbol,
                "current_ratio": info.get('currentRatio', 0),
                "quick_ratio": info.get('quickRatio', 0),
                "debt_to_equity": info.get('debtToEquity', 0),
                "roe": info.get('returnOnEquity', 0),
                "roa": info.get('returnOnAssets', 0),
                "profit_margin": info.get('profitMargins', 0),
                "operating_margin": info.get('operatingMargins', 0),
                "gross_margin": info.get('grossMargins', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "pb_ratio": info.get('priceToBook', 0),
                "beta": info.get('beta', 0),
                "52_week_high": info.get('fiftyTwoWeekHigh', 0),
                "52_week_low": info.get('fiftyTwoWeekLow', 0)
            }
            
            return ratios
            
        except Exception as e:
            print(f"Error fetching ratios: {e}")
        
        return {"symbol": symbol, "error": "Unable to fetch ratios"}
    
    @staticmethod
    def get_multiple_stocks(symbols: List[str] = ["AAPL", "MSFT", "GOOGL", "AMZN"]) -> List[Dict]:
        """Get data for multiple stocks"""
        if not YFINANCE_AVAILABLE:
            return []
        
        stocks_data = []
        for symbol in symbols:
            data = FinancialDataService.get_stock_price(symbol)
            if "error" not in data:
                stocks_data.append(data)
        
        return stocks_data
    
    @staticmethod
    def generate_sample_transactions(count: int = 10) -> List[Dict]:
        """Generate realistic sample transactions for fraud detection"""
        import random
        transactions = []
        base_time = datetime.now()
        
        suspicious_patterns = [
            {"amount": random.uniform(9000, 9999), "risk": 0.85, "reason": "Just below reporting threshold"},
            {"amount": random.uniform(500, 1000), "risk": 0.75, "reason": "Multiple small amounts"},
            {"amount": random.uniform(10000, 50000), "risk": 0.90, "reason": "Unusually large amount"},
        ]
        
        for i in range(count):
            is_suspicious = random.random() < 0.3  # 30% suspicious
            
            if is_suspicious:
                pattern = random.choice(suspicious_patterns)
                transaction = {
                    "transaction_id": f"TXN{1000 + i}",
                    "amount": round(pattern["amount"], 2),
                    "timestamp": (base_time - timedelta(hours=random.randint(0, 48))).isoformat(),
                    "merchant": random.choice(["Online Retailer", "International Wire", "Crypto Exchange", "Unknown Merchant"]),
                    "risk_score": pattern["risk"],
                    "flag": pattern["reason"]
                }
            else:
                transaction = {
                    "transaction_id": f"TXN{1000 + i}",
                    "amount": round(random.uniform(10, 500), 2),
                    "timestamp": (base_time - timedelta(hours=random.randint(0, 48))).isoformat(),
                    "merchant": random.choice(["Grocery Store", "Gas Station", "Restaurant", "Pharmacy"]),
                    "risk_score": round(random.uniform(0.1, 0.4), 2),
                    "flag": "Normal"
                }
            
            transactions.append(transaction)
        
        return sorted(transactions, key=lambda x: x["risk_score"], reverse=True)
    
    @staticmethod
    def get_compliance_data() -> Dict:
        """Generate sample compliance data"""
        return {
            "sox_compliance": {
                "status": "Active",
                "last_audit": (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
                "next_audit": (datetime.now() + timedelta(days=320)).strftime("%Y-%m-%d"),
                "controls_tested": 156,
                "controls_passed": 154,
                "compliance_score": 98.7
            },
            "pci_dss": {
                "status": "Compliant",
                "certification_expiry": (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d"),
                "requirements_met": 12,
                "total_requirements": 12
            },
            "aml_monitoring": {
                "status": "Active",
                "suspicious_activities": 3,
                "reports_filed": 1,
                "review_period": "Last 30 days"
            }
        }

class BritiveAgentCoreClient:
    """Simplified client using Britive credentials with AgentCore built-in memory"""
    
    def __init__(self):
        self.creds = None
        self.client = None
        self.data_service = FinancialDataService()
    
    def checkout_credentials(self):
        """Checkout Britive credentials"""
        try:
            result = subprocess.run(
                ["pybritive", "checkout", "AWS SE Demo/Britive Agentic AI Solution/Admin", "-t", "demo"],
                capture_output=True,
                text=True,
                check=True
            )
            self.creds = json.loads(result.stdout)
            
            # Create boto3 client with Britive credentials
            session = boto3.Session(
                aws_access_key_id=self.creds["AccessKeyId"],
                aws_secret_access_key=self.creds["SecretAccessKey"],
                aws_session_token=self.creds["SessionToken"],
                region_name="us-west-2"
            )
            self.client = session.client('bedrock-agent-runtime')
            print("✅ Britive credentials checked out successfully")
        except Exception as e:
            print(f"❌ Error checking out credentials: {e}")
            raise
    
    def checkin_credentials(self):
        """Checkin Britive credentials"""
        if self.creds:
            try:
                subprocess.run(
                    ["pybritive", "checkin", "AWS SE Demo/Britive Agentic AI Solution/Admin", "-t", "demo"],
                    check=True
                )
                print("✅ Britive credentials checked in successfully")
            except Exception as e:
                print(f"⚠️ Error checking in credentials: {e}")
            finally:
                self.creds = None
    
    def enrich_query_with_data(self, query: str, agent_type: str) -> str:
        """Enrich the query with real financial data based on agent type"""
        enriched_query = query + "\n\n--- Real-Time Financial Data ---\n"
        
        if agent_type == "fraud_detection":
            transactions = self.data_service.generate_sample_transactions(10)
            enriched_query += f"\n📊 Recent Transactions Analysis:\n"
            for txn in transactions[:5]:
                enriched_query += f"• {txn['transaction_id']}: ${txn['amount']:.2f} - Risk: {txn['risk_score']:.2f} - {txn['flag']}\n"
        
        elif agent_type == "compliance":
            compliance = self.data_service.get_compliance_data()
            enriched_query += f"\n✅ Compliance Status:\n"
            enriched_query += f"• SOX Compliance: {compliance['sox_compliance']['compliance_score']}%\n"
            enriched_query += f"• PCI-DSS: {compliance['pci_dss']['status']}\n"
            enriched_query += f"• AML Monitoring: {compliance['aml_monitoring']['status']}\n"
        
        elif agent_type == "risk_analysis":
            stock_data = self.data_service.get_stock_price("AAPL")
            ratios = self.data_service.get_financial_ratios("AAPL")
            portfolio_stocks = self.data_service.get_multiple_stocks(["AAPL", "MSFT", "GOOGL"])
            
            enriched_query += f"\n📈 Market Data:\n"
            for stock in portfolio_stocks[:3]:
                enriched_query += f"• {stock['symbol']}: ${stock.get('price', 0):.2f} ({stock.get('change_percent', 'N/A')})\n"
            
            enriched_query += f"\n📊 AAPL Financial Health:\n"
            enriched_query += f"• P/E Ratio: {ratios.get('pe_ratio', 'N/A')}\n"
            enriched_query += f"• Debt/Equity: {ratios.get('debt_to_equity', 'N/A')}\n"
            enriched_query += f"• Beta (Volatility): {ratios.get('beta', 'N/A')}\n"
            enriched_query += f"• ROE: {ratios.get('roe', 'N/A')}\n"
        
        return enriched_query
    
    async def invoke_agent(self, agent_type: str, query: str, session_id: str) -> dict:
        """
        Invoke AgentCore agent with built-in memory and enriched data
        """
        agent_config = AGENTS[agent_type]
        
        # Check if agents are configured
        if agent_config["agent_id"].startswith("YOUR_"):
            return {
                "success": False,
                "error": f"Agent {agent_type} not configured. Please deploy agents and update AGENTS dictionary.",
                "agent": agent_type
            }
        
        # Enrich query with real data
        enriched_query = self.enrich_query_with_data(query, agent_type)
        
        try:
            response = self.client.invoke_agent(
                agentId=agent_config["agent_id"],
                agentAliasId=agent_config["alias_id"],
                sessionId=session_id,
                inputText=enriched_query,
                enableTrace=True
            )
            
            # Stream and collect response
            full_response = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        full_response += chunk['bytes'].decode('utf-8')
            
            return {
                "success": True,
                "response": full_response,
                "agent": agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": agent_type
            }
    
    async def route_query(self, query: str, session_id: str) -> dict:
        """
        Supervisor logic - route to appropriate agents
        """
        query_lower = query.lower()
        results = {}
        
        # Determine which agents to invoke based on query
        agents_to_call = []
        
        if any(word in query_lower for word in ['fraud', 'transaction', 'suspicious', 'anomaly']):
            agents_to_call.append('fraud_detection')
        
        if any(word in query_lower for word in ['compliance', 'sox', 'pci', 'regulation', 'regulatory']):
            agents_to_call.append('compliance')
        
        if any(word in query_lower for word in ['risk', 'var', 'portfolio', 'stress', 'volatility', 'stock']):
            agents_to_call.append('risk_analysis')
        
        # Default to fraud detection if no specific keywords
        if not agents_to_call:
            agents_to_call = ['fraud_detection']
        
        # Invoke agents sequentially
        for agent_type in agents_to_call:
            result = await self.invoke_agent(agent_type, query, session_id)
            results[agent_type] = result
        
        # Aggregate responses
        successful_responses = []
        errors = []
        
        for agent_type, result in results.items():
            if result["success"]:
                successful_responses.append(f"### {agent_type.replace('_', ' ').title()}\n\n{result['response']}")
            else:
                errors.append(f"❌ {agent_type}: {result['error']}")
        
        combined_response = "\n\n---\n\n".join(successful_responses)
        
        if errors:
            combined_response += f"\n\n**Errors:**\n" + "\n".join(errors)
        
        return {
            "success": len(successful_responses) > 0,
            "response": combined_response,
            "agents_invoked": agents_to_call,
            "session_id": session_id
        }

@app.route('/')
def home():
    """Main page with UI"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint for agent analysis"""
    data = request.json
    query = data.get('query', '')
    session_id = data.get('session_id', f"session-{int(datetime.now().timestamp())}")
    
    if not query:
        return jsonify({"success": False, "error": "Query is required"}), 400
    
    async def process():
        client = BritiveAgentCoreClient()
        try:
            client.checkout_credentials()
            return await client.route_query(query, session_id)
        except Exception as e:
            print(f"ERROR in process(): {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            client.checkin_credentials()
    
    # Run async operation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(process())
    finally:
        loop.close()
    
    return jsonify(result)

@app.route('/api/financial-data', methods=['GET'])
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

# HTML Template with enhanced UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Finance AI Multi-Agent System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .stat-card h3 {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        
        .stat-card .change {
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .change.positive { color: #10b981; }
        .change.negative { color: #ef4444; }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        .input-section {
            margin-bottom: 20px;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            min-height: 120px;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
        }
        
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            flex: 1;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        
        .response-section {
            display: none;
        }
        
        .response-section.visible {
            display: block;
        }
        
        .response-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .response-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #333;
        }
        
        .agents-badge {
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .response-content {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            white-space: pre-wrap;
            line-height: 1.6;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .session-info {
            font-size: 0.9em;
            color: #666;
            margin-top: 10px;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 6px;
        }
        
        .examples {
            margin-top: 15px;
        }
        
        .examples h3 {
            font-size: 0.95em;
            color: #666;
            margin-bottom: 10px;
        }
        
        .example-query {
            display: inline-block;
            background: #f0f0f0;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s;
        }
        
        .example-query:hover {
            background: #667eea;
            color: white;
        }
        
        .refresh-btn {
            cursor: pointer;
            padding: 5px 10px;
            background: #667eea;
            color: white;
            border-radius: 5px;
            font-size: 0.8em;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 Finance AI Multi-Agent System</h1>
            <p>Powered by Amazon Bedrock AgentCore with Real-Time Financial Data</p>
        </div>
        
        <div class="dashboard" id="dashboard">
            <div class="stat-card">
                <h3>📈 Stock Price (AAPL)</h3>
                <div class="value" id="stockPrice">--</div>
                <div class="change" id="stockChange">Loading...</div>
            </div>
            <div class="stat-card">
                <h3>🔍 High-Risk Transactions</h3>
                <div class="value" id="riskCount">--</div>
                <div class="change">Last 24 hours</div>
            </div>
            <div class="stat-card">
                <h3>✅ Compliance Score</h3>
                <div class="value" id="complianceScore">--</div>
                <div class="change positive">SOX Compliant</div>
            </div>
            <div class="stat-card">
                <h3>⚠️ Active Alerts</h3>
                <div class="value" id="alertCount">--</div>
                <div class="change">Requires review</div>
            </div>
        </div>
        
        <div class="card">
            <div class="input-section">
                <textarea id="queryInput" placeholder="Enter your financial analysis query..."></textarea>
                
                <div class="examples">
                    <h3>💡 Example queries:</h3>
                    <span class="example-query" onclick="setQuery('Analyze recent suspicious transactions and identify fraud patterns')">🔍 Analyze suspicious transactions</span>
                    <span class="example-query" onclick="setQuery('Check SOX compliance status and identify any regulatory violations')">✅ Check SOX compliance</span>
                    <span class="example-query" onclick="setQuery('Calculate portfolio risk, VaR, and analyze current stock market volatility')">📊 Calculate portfolio risk</span>
                    <span class="example-query" onclick="setQuery('Review financial ratios and assess fraud risk indicators')">⚠️ Fraud risk assessment</span>
                </div>
                
                <div class="session-info">
                    <strong>Session ID:</strong> <span id="sessionId"></span>
                    <span class="refresh-btn" onclick="loadDashboard()">🔄 Refresh Data</span>
                </div>
            </div>
            
            <div class="button-group">
                <button class="btn-primary" onclick="analyzeQuery()" id="analyzeBtn">
                    🚀 Analyze with AI Agents
                </button>
                <button class="btn-secondary" onclick="clearResults()">
                    🔄 Clear
                </button>
            </div>
        </div>
        
        <div class="card response-section" id="responseSection">
            <div class="response-header">
                <div class="response-title">📊 Analysis Results</div>
                <div class="agents-badge" id="agentsBadge"></div>
            </div>
            <div class="response-content" id="responseContent"></div>
        </div>
        
        <div class="card loading" id="loadingSection" style="display: none;">
            <div class="spinner"></div>
            <p>Analyzing with AI agents and real-time data...</p>
        </div>
    </div>
    
    <script>
        // Generate session ID
        const sessionId = 'session-' + Date.now();
        document.getElementById('sessionId').textContent = sessionId;
        
        // Load dashboard data on page load
        loadDashboard();
        
        function setQuery(query) {
            document.getElementById('queryInput').value = query;
        }
        
        async function loadDashboard() {
            try {
                // Load stock data
                const stockResp = await fetch('/api/financial-data?type=stock&symbol=AAPL');
                const stockData = await stockResp.json();
                document.getElementById('stockPrice').textContent = '$' + (stockData.price || 0).toFixed(2);
                const changeClass = stockData.change >= 0 ? 'positive' : 'negative';
                document.getElementById('stockChange').textContent = stockData.change_percent || 'N/A';
                document.getElementById('stockChange').className = 'change ' + changeClass;
                
                // Load transaction data
                const txnResp = await fetch('/api/financial-data?type=transactions');
                const txnData = await txnResp.json();
                const highRisk = txnData.filter(t => t.risk_score > 0.7).length;
                document.getElementById('riskCount').textContent = highRisk;
                
                // Load compliance data
                const compResp = await fetch('/api/financial-data?type=compliance');
                const compData = await compResp.json();
                document.getElementById('complianceScore').textContent = 
                    (compData.sox_compliance?.compliance_score || 0).toFixed(1) + '%';
                
                // Active alerts (from AML monitoring)
                document.getElementById('alertCount').textContent = 
                    compData.aml_monitoring?.suspicious_activities || 0;
                    
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }
        
        async function analyzeQuery() {
            const query = document.getElementById('queryInput').value.trim();
            
            if (!query) {
                alert('Please enter a query');
                return;
            }
            
            // Show loading
            document.getElementById('loadingSection').style.display = 'block';
            document.getElementById('responseSection').classList.remove('visible');
            document.getElementById('analyzeBtn').disabled = true;
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: query,
                        session_id: sessionId
                    })
                });
                
                const data = await response.json();
                
                // Hide loading
                document.getElementById('loadingSection').style.display = 'none';
                
                if (data.success) {
                    // Show results
                    document.getElementById('responseContent').textContent = data.response;
                    document.getElementById('agentsBadge').textContent = 
                        data.agents_invoked.length + ' agents invoked';
                    document.getElementById('responseSection').classList.add('visible');
                } else {
                    alert('Error: ' + (data.error || 'Unknown error occurred'));
                }
                
            } catch (error) {
                document.getElementById('loadingSection').style.display = 'none';
                alert('Error: ' + error.message);
            } finally {
                document.getElementById('analyzeBtn').disabled = false;
            }
        }
        
        function clearResults() {
            document.getElementById('queryInput').value = '';
            document.getElementById('responseSection').classList.remove('visible');
        }
        
        // Allow Enter to submit (with Shift+Enter for new line)
        document.getElementById('queryInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                analyzeQuery();
            }
        });
        
        // Refresh dashboard every 30 seconds
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("🚀 Starting Finance AI Multi-Agent System with Real-Time Data...")
    print("📝 Make sure to update AGENTS dictionary with your agent IDs!")
    print("\n💰 Using Yahoo Finance (yfinance) - FREE & Unlimited!")
    if not YFINANCE_AVAILABLE:
        print("⚠️  Please install: pip install yfinance")
    print("\n🔑 Optional APIs for more features:")
    print("   - Finnhub (60 calls/min): https://finnhub.io/")
    print("   - Twelve Data (800 calls/day): https://twelvedata.com/")
    print("\n✅ Starting server on http://localhost:5001\n")
    app.run(debug=True, host='0.0.0.0', port=5001)
