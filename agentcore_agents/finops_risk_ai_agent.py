# ============================================
# finops_risk_ai_agent.py - FINAL NUCLEAR FIX
# ============================================
from strands import Agent, tool
from strands.models import BedrockModel
from strands.agent.conversation_manager import SummarizingConversationManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the AgentCore app
app = BedrockAgentCoreApp()

@tool
def calculate_value_at_risk(portfolio_value: float, volatility: float = 0.15) -> str:
    """Calculate Value at Risk for portfolio"""
    try:
        if portfolio_value <= 0:
            return "⚠️ Portfolio value must be greater than zero"
        
        if volatility < 0 or volatility > 1:
            return "⚠️ Volatility must be between 0 and 1"
        
        var = portfolio_value * volatility * 1.645
        
        result = f"\n📊 VALUE AT RISK ANALYSIS\n"
        result += f"Portfolio Value: ${portfolio_value:,.2f}\n"
        result += f"Volatility: {volatility * 100:.2f}%\n"
        result += f"Confidence Level: 95%\n"
        result += f"Daily VaR (95%): ${var:,.2f}\n"
        result += f"\n💡 This means there is a 5% chance of losing more than ${var:,.2f} in a single day.\n"
        
        return result
    except Exception as e:
        return f"Error calculating Value at Risk: {str(e)}"

def extract_portfolio_value(text):
    """Extract portfolio value from text - handles $100k, $100,000, etc."""
    logger.info(f"Attempting to extract portfolio value from: {text[:100]}...")
    
    # Pattern 1: $100k or 100k format
    match = re.search(r'\$?(\d+)k\b', text, re.IGNORECASE)
    if match:
        value = float(match.group(1)) * 1000
        logger.info(f"✅ Extracted {value} from 'k' pattern")
        return value
    
    # Pattern 2: $100,000 or 100000 format
    match = re.search(r'\$?([\d,]+)', text)
    if match:
        value_str = match.group(1).replace(',', '')
        if len(value_str) >= 5:  # Only substantial amounts
            value = float(value_str)
            logger.info(f"✅ Extracted {value} from number pattern")
            return value
    
    logger.info("❌ No portfolio value found")
    return None

def create_agent():
    """Create the Risk Analysis Agent"""
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
        system_prompt="""You are a VaR calculator. When you see portfolio information, extract it and calculate immediately.""",
        tools=[calculate_value_at_risk],
        conversation_manager=conversation_manager,
    )
    
    return agent

# Create the agent instance
agent = create_agent()

# Define the entrypoint for AgentCore
@app.entrypoint
def invoke(payload):
    """Process user input with PREPROCESSING to extract portfolio value"""
    try:
        user_message = payload.get("inputText") or payload.get("prompt", "No prompt provided")
        logger.info(f"📥 Received message: {user_message[:100]}...")
        
        # CRITICAL: Extract portfolio value BEFORE sending to agent
        portfolio_value = extract_portfolio_value(user_message)
        
        if portfolio_value:
            # We found a value - calculate directly, bypass agent
            logger.info(f"💰 Portfolio value found: ${portfolio_value:,.0f} - calculating directly")
            result = calculate_value_at_risk(portfolio_value)
            return {"result": result}
        else:
            # No value found - let agent handle it
            logger.info("🤖 No portfolio value found - passing to agent")
            result = agent(user_message)
            return {"result": result.message}
            
    except Exception as e:
        logger.error(f"❌ Error in invoke: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"result": f"Error processing request: {str(e)}"}

# For local testing
if __name__ == "__main__":
    test_queries = [
        "Calculate: VaR 95%, $100k, 60% SPY + 30% AGG + 10% GLD, 1 month",
        "VaR for $50,000 portfolio",
        "What's my risk?"
    ]
    
    print("🧪 Testing extraction locally:\n")
    for query in test_queries:
        print(f"Query: {query}")
        value = extract_portfolio_value(query)
        if value:
            print(f"✅ Extracted: ${value:,.0f}")
            print(calculate_value_at_risk(value))
        else:
            print("❌ No value found - would ask agent")
        print("-" * 60)
    
    app.run()