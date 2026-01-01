# ============================================
# finops_fraud_ai_agent.py - Fraud Detection Agent
# ============================================
"""
AgentCore CLI-based deployment for multi-agent finance system
This uses the simplified agentcore CLI workflow instead of manual Docker builds
"""

from strands import Agent, tool
from strands.models import BedrockModel
from strands.agent.conversation_manager import SummarizingConversationManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import boto3
import json
from typing import List

# Initialize the AgentCore app
app = BedrockAgentCoreApp()

@tool
def analyze_transaction_pattern(transactions: List[dict], threshold: float = 0.7) -> str:
    """Analyze transaction patterns for fraud detection"""
    try:
        # Handle empty or invalid input
        if not transactions:
            return "⚠️ No transactions provided for analysis"
        
        high_risk = [t for t in transactions if t.get('risk_score', 0) > threshold]
        result = f"\n🔍 FRAUD DETECTION ANALYSIS\n"
        result += f"Total Transactions: {len(transactions)}\n"
        result += f"High-Risk Transactions: {len(high_risk)}\n"
        result += f"Risk Threshold: {threshold}\n"
        
        if high_risk:
            result += f"\nTop High-Risk Transactions:\n"
            for t in high_risk[:5]:
                result += f"• {t.get('transaction_id', 'N/A')} - ${t.get('amount', 0):,.2f} (Risk: {t.get('risk_score', 0):.2f})\n"
        else:
            result += "\n✅ No high-risk transactions detected\n"
        
        return result
    except Exception as e:
        return f"Error analyzing transactions: {str(e)}"

def create_agent():
    """Create the Fraud Detection Agent"""
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        temperature=0.0,
    )
    
    conversation_manager = SummarizingConversationManager(
        summary_ratio=0.5,
        preserve_recent_messages=5,
    )
    
    agent = Agent(
        model=bedrock_model,
        system_prompt="""You are an enterprise-grade fraud detection AI agent.
Analyze transactions for fraud, calculate risk scores, and provide actionable recommendations.
You can access shared context from other agents via memory to make informed decisions.
When you identify fraud patterns that have compliance implications, note them for other agents.""",
        tools=[analyze_transaction_pattern],
        conversation_manager=conversation_manager,
    )
    
    return agent

# Create the agent instance
agent = create_agent()

# Define the entrypoint for AgentCore
@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "No prompt provided")
    result = agent(user_message)
    return {"result": result.message}

# For local testing
if __name__ == "__main__":
    app.run()