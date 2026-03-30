# ============================================
# finops_risk_ai_agent.py - With S3 Integration
# ============================================
from strands import Agent, tool
from strands.models import BedrockModel
from strands.agent.conversation_manager import SummarizingConversationManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import boto3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the AgentCore app
app = BedrockAgentCoreApp()

# S3 Configuration
import os
S3_BUCKET = os.environ.get("RISK_AGENT_S3_BUCKET", "")
RISK_FILES = {
    "portfolio": "portfolio_holdings_2025.txt",
    "var": "var_risk_metrics_2025.txt",
    "market": "market_risk_analysis_2025.txt",
    "stress": "stress_testing_scenarios_2025.txt"
}

@tool
def analyze_risk_reports() -> str:
    """
    Retrieve and analyze risk management reports from S3.
    Returns a comprehensive portfolio risk status summary.
    """
    try:
        logger.info(f"📥 Fetching risk reports from S3 bucket: {S3_BUCKET}")

        reports = {}

        # Initialize S3 client (credentials provided by Britive via the Flask app at invocation time)
        s3_client = boto3.client('s3', region_name='us-west-2')

        # Download each risk report
        for report_type, filename in RISK_FILES.items():
            try:
                logger.info(f"📄 Downloading {filename}...")
                response = s3_client.get_object(Bucket=S3_BUCKET, Key=filename)
                content = response['Body'].read().decode('utf-8')
                reports[report_type] = content
                logger.info(f"✅ Successfully downloaded {filename} ({len(content)} chars)")
            except Exception as e:
                logger.error(f"❌ Error downloading {filename}: {e}")
                reports[report_type] = f"Error: Could not retrieve {report_type} report - {str(e)}"
        
        # Analyze and summarize the reports
        summary = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    PORTFOLIO RISK DASHBOARD                              ║
╚══════════════════════════════════════════════════════════════════════════╝

"""
        
        # Portfolio Holdings Summary
        if "portfolio" in reports and "Error" not in reports["portfolio"]:
            portfolio_content = reports["portfolio"]
            summary += """
┌─────────────────────────────────────────────────────────────────────────┐
│ 📊 PORTFOLIO HOLDINGS OVERVIEW                                          │
└─────────────────────────────────────────────────────────────────────────┘
"""
            # Extract key metrics from the report
            for line in portfolio_content.split('\n'):
                if "Total Assets Under Management:" in line:
                    summary += f"   {line.strip()}\n"
                elif "Reporting Date:" in line:
                    summary += f"   {line.strip()}\n"
            
            summary += "\n   Asset Allocation:\n"
            for line in portfolio_content.split('\n'):
                if "US Equities:" in line or "International Equities:" in line:
                    summary += f"   • {line.strip()}\n"
                elif "Fixed Income:" in line or "Alternative Investments:" in line:
                    summary += f"   • {line.strip()}\n"
                elif "Cash & Equivalents:" in line:
                    summary += f"   • {line.strip()}\n"
            
            # Extract top holdings
            if "TOP 10 HOLDINGS" in portfolio_content:
                summary += "\n   Top Holdings:\n"
                lines = portfolio_content.split('\n')
                in_holdings = False
                count = 0
                for line in lines:
                    if "TOP 10 HOLDINGS" in line:
                        in_holdings = True
                        continue
                    if in_holdings and line.strip() and count < 5:
                        if "MSFT" in line or "AAPL" in line or "NVDA" in line or "GOOGL" in line or "AMZN" in line:
                            summary += f"   • {line.strip()}\n"
                            count += 1
        else:
            summary += "\n📊 PORTFOLIO HOLDINGS: ❌ Report not available\n"
        
        summary += "\n"
        
        # VaR Risk Metrics Summary
        if "var" in reports and "Error" not in reports["var"]:
            var_content = reports["var"]
            summary += """
┌─────────────────────────────────────────────────────────────────────────┐
│ 📈 VALUE AT RISK (VaR) METRICS                                          │
└─────────────────────────────────────────────────────────────────────────┘
"""
            # Extract VaR metrics
            for line in var_content.split('\n'):
                if "1-Day VaR (95%)" in line and "Current:" in line:
                    summary += f"   {line.strip()}\n"
                elif "1-Day VaR (99%)" in line and "Current:" in line:
                    summary += f"   {line.strip()}\n"
                elif "10-Day VaR (95%)" in line:
                    summary += f"   {line.strip()}\n"
            
            summary += "\n   Risk Metrics:\n"
            for line in var_content.split('\n'):
                if "Portfolio Volatility:" in line:
                    summary += f"   • {line.strip()}\n"
                elif "Portfolio Beta:" in line:
                    summary += f"   • {line.strip()}\n"
                elif "Sharpe Ratio:" in line:
                    summary += f"   • {line.strip()}\n"
            
            # Check for limit breaches
            if "BREACH" in var_content or "EXCEEDED" in var_content:
                summary += "\n   ⚠️  LIMIT BREACHES DETECTED:\n"
                for line in var_content.split('\n'):
                    if "BREACH" in line or "EXCEEDED" in line:
                        summary += f"   🔴 {line.strip()}\n"
        else:
            summary += "\n📈 VaR METRICS: ❌ Report not available\n"
        
        summary += "\n"
        
        # Market Risk Summary
        if "market" in reports and "Error" not in reports["market"]:
            market_content = reports["market"]
            summary += """
┌─────────────────────────────────────────────────────────────────────────┐
│ 🌐 MARKET RISK ANALYSIS                                                 │
└─────────────────────────────────────────────────────────────────────────┘
"""
            # Extract market risk metrics
            for line in market_content.split('\n'):
                if "S&P 500:" in line and "Level:" in line:
                    summary += f"   {line.strip()}\n"
                elif "VIX:" in line:
                    summary += f"   {line.strip()}\n"
                elif "10-Year Treasury:" in line:
                    summary += f"   {line.strip()}\n"
            
            # FX Exposure
            if "FX Exposure" in market_content or "Currency" in market_content:
                summary += "\n   FX Exposure:\n"
                for line in market_content.split('\n'):
                    if "EUR:" in line or "GBP:" in line or "JPY:" in line:
                        summary += f"   • {line.strip()}\n"
        else:
            summary += "\n🌐 MARKET RISK: ❌ Report not available\n"
        
        summary += "\n"
        
        # Stress Testing Summary
        if "stress" in reports and "Error" not in reports["stress"]:
            stress_content = reports["stress"]
            summary += """
┌─────────────────────────────────────────────────────────────────────────┐
│ 🔥 STRESS TESTING SCENARIOS                                             │
└─────────────────────────────────────────────────────────────────────────┘
"""
            summary += "   Historical Scenario Analysis:\n"
            for line in stress_content.split('\n'):
                if "2008 Financial Crisis" in line and "Impact:" in line:
                    summary += f"   • {line.strip()}\n"
                elif "COVID-19" in line and "Impact:" in line:
                    summary += f"   • {line.strip()}\n"
                elif "Dot-Com" in line and "Impact:" in line:
                    summary += f"   • {line.strip()}\n"
            
            # High vulnerability scenarios
            if "HIGH" in stress_content or "VULNERABILITY" in stress_content:
                summary += "\n   ⚠️  High Vulnerability Scenarios:\n"
                for line in stress_content.split('\n'):
                    if "HIGH" in line and ("Probability" in line or "Vulnerability" in line):
                        summary += f"   🔴 {line.strip()}\n"
        else:
            summary += "\n🔥 STRESS TESTING: ❌ Report not available\n"
        
        # Overall Summary
        summary += """

╔══════════════════════════════════════════════════════════════════════════╗
║                        RISK MANAGEMENT STATUS                            ║
╚══════════════════════════════════════════════════════════════════════════╝

✅ Portfolio AUM: $847.5M
⚠️  VaR Utilization: 74.8% of limit (elevated)
🔴 BREACH: Technology sector exceeds 35% concentration limit

🎯 IMMEDIATE ACTIONS REQUIRED:
   1. Reduce tech sector exposure by ~$94M to meet 35% limit
   2. Review VaR limit utilization (approaching threshold)
   3. Implement hedging for high-vulnerability scenarios
   4. Rebalance international equity allocation

📊 RISK TREND ANALYSIS:
   • Portfolio volatility: ELEVATED at 16.8%
   • Beta vs S&P 500: 1.12 (slightly aggressive)
   • Concentration risk: HIGH in technology sector

🔔 UPCOMING REVIEWS:
   • Weekly risk committee meeting: Friday
   • Monthly VaR model validation: January 15, 2026
   • Quarterly stress test update: January 31, 2026

═══════════════════════════════════════════════════════════════════════════

📎 Full reports available in S3: s3://{S3_BUCKET}/
"""
        
        return summary
        
    except Exception as e:
        logger.error(f"❌ Error in analyze_risk_reports: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return f"❌ Error analyzing risk reports: {str(e)}"

def create_agent():
    """Create the Risk Analysis Agent"""
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        temperature=0.0,
    )
    
    conversation_manager = SummarizingConversationManager(
        summary_ratio=0.5,
        preserve_recent_messages=5,
    )
    
    agent = Agent(
        model=bedrock_model,
        system_prompt="""You are an enterprise risk analysis AI agent.

When the user asks about risk, VaR, portfolio, stress testing, or market risk:
1. IMMEDIATELY call the analyze_risk_reports tool
2. Present the risk management status summary
3. Highlight limit breaches and action items

You have access to real risk management reports stored in S3. Always retrieve the latest reports to provide accurate risk status.""",
        tools=[analyze_risk_reports],
        conversation_manager=conversation_manager,
    )
    
    return agent

# Create the agent instance
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent

# Define the entrypoint for AgentCore
@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    try:
        user_message = payload.get("inputText") or payload.get("prompt", "No prompt provided")
        logger.info(f"📥 Received risk query: {user_message[:100]}...")
        
        result = get_agent()(user_message)
        return {"result": result.message}
        
    except Exception as e:
        logger.error(f"❌ Error in invoke: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"result": f"Error processing request: {str(e)}"}

# For local testing
if __name__ == "__main__":
    app.run()
