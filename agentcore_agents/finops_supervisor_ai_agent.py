# ============================================
# finops_supervisor_ai_agent.py - Supervisor/Orchestrator Agent
# ============================================
"""
Supervisor Agent for Multi-Agent Finance System
Coordinates task decomposition, routing, and result aggregation
"""

from strands import Agent, tool
from strands.models import BedrockModel
from strands.agent.conversation_manager import SummarizingConversationManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from typing import List, Dict
import json

# Initialize the AgentCore app
app = BedrockAgentCoreApp()

@tool
def decompose_task(query: str) -> str:
    """
    Analyze a financial query and decompose it into subtasks for specialist agents.
    Returns a structured plan with which agents to invoke and in what order.
    """
    # Analyze query for keywords
    query_lower = query.lower()
    
    plan = {
        "original_query": query,
        "subtasks": [],
        "agent_sequence": [],
        "priority": "normal"
    }
    
    # Fraud detection tasks
    if any(word in query_lower for word in ['fraud', 'suspicious', 'anomaly', 'transaction', 'unusual']):
        plan["subtasks"].append({
            "task": "Analyze transactions for fraud patterns and suspicious activities",
            "agent": "fraud_detection",
            "priority": 1
        })
        plan["agent_sequence"].append("fraud_detection")
    
    # Compliance tasks
    if any(word in query_lower for word in ['compliance', 'sox', 'pci', 'regulation', 'audit', 'regulatory', 'aml', 'kyc']):
        plan["subtasks"].append({
            "task": "Check compliance status and regulatory requirements",
            "agent": "compliance",
            "priority": 2
        })
        plan["agent_sequence"].append("compliance")
    
    # Risk analysis tasks
    if any(word in query_lower for word in ['risk', 'var', 'portfolio', 'volatility', 'market', 'exposure', 'hedge']):
        plan["subtasks"].append({
            "task": "Calculate risk metrics and assess portfolio exposure",
            "agent": "risk_analysis",
            "priority": 3
        })
        plan["agent_sequence"].append("risk_analysis")
    
    # If no specific keywords, invoke all agents for comprehensive analysis
    if not plan["agent_sequence"]:
        plan["subtasks"] = [
            {"task": "Comprehensive fraud detection scan", "agent": "fraud_detection", "priority": 1},
            {"task": "Compliance review", "agent": "compliance", "priority": 2},
            {"task": "Risk assessment", "agent": "risk_analysis", "priority": 3}
        ]
        plan["agent_sequence"] = ["fraud_detection", "compliance", "risk_analysis"]
    
    # Set priority based on urgency keywords
    if any(word in query_lower for word in ['urgent', 'immediate', 'critical', 'emergency', 'alert']):
        plan["priority"] = "high"
    
    return json.dumps(plan, indent=2)

@tool
def route_to_agent(agent_name: str, subtask: str) -> str:
    """
    Route a specific subtask to the appropriate specialist agent.
    This is a placeholder that represents the routing decision.
    """
    routing_info = {
        "target_agent": agent_name,
        "subtask": subtask,
        "status": "routed",
        "context_shared": True
    }
    
    return json.dumps(routing_info, indent=2)

@tool
def aggregate_results(results: List[Dict]) -> str:
    """
    Aggregate results from multiple specialist agents into a coherent final report.
    Identifies conflicts, synthesizes insights, and provides actionable recommendations.
    """
    aggregation = {
        "executive_summary": "",
        "key_findings": [],
        "cross_agent_insights": [],
        "conflicts": [],
        "recommendations": [],
        "confidence_score": 0.0
    }
    
    # Analyze results for patterns
    fraud_found = any("high-risk" in str(r).lower() or "fraud" in str(r).lower() for r in results)
    compliance_issues = any("violation" in str(r).lower() or "non-compliant" in str(r).lower() for r in results)
    high_risk = any("high risk" in str(r).lower() or "elevated" in str(r).lower() for r in results)
    
    # Build executive summary
    if fraud_found or compliance_issues or high_risk:
        aggregation["executive_summary"] = "⚠️ Critical issues identified requiring immediate attention."
        aggregation["confidence_score"] = 0.85
    else:
        aggregation["executive_summary"] = "✅ No critical issues detected. Systems operating within normal parameters."
        aggregation["confidence_score"] = 0.92
    
    # Extract key findings
    if fraud_found:
        aggregation["key_findings"].append("Potential fraudulent activities detected")
    if compliance_issues:
        aggregation["key_findings"].append("Compliance violations identified")
    if high_risk:
        aggregation["key_findings"].append("Elevated risk levels observed")
    
    # Cross-agent insights
    if fraud_found and compliance_issues:
        aggregation["cross_agent_insights"].append(
            "Fraud patterns correlate with compliance gaps - suggest integrated remediation"
        )
    
    if fraud_found and high_risk:
        aggregation["cross_agent_insights"].append(
            "Fraudulent activities contributing to increased portfolio risk"
        )
    
    # Recommendations
    if fraud_found:
        aggregation["recommendations"].append("Immediate transaction review and account freeze for high-risk items")
    if compliance_issues:
        aggregation["recommendations"].append("Conduct compliance audit and implement corrective controls")
    if high_risk:
        aggregation["recommendations"].append("Rebalance portfolio and implement risk mitigation strategies")
    
    return json.dumps(aggregation, indent=2)

@tool
def monitor_agent_progress(agent_name: str, status: str) -> str:
    """
    Monitor the progress of specialist agents during task execution.
    Tracks completion status and handles failures.
    """
    monitoring = {
        "agent": agent_name,
        "status": status,
        "timestamp": "current",
        "health": "operational" if status == "completed" else "processing"
    }
    
    return json.dumps(monitoring, indent=2)

def create_agent():
    """Create the Supervisor Agent"""
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
        system_prompt="""You are a Supervisor Agent for a multi-agent financial analysis system.

Your responsibilities:
1. **Task Decomposition**: Break down complex financial queries into specific subtasks for specialist agents
2. **Agent Orchestration**: Determine which specialist agents to invoke (fraud_detection, compliance, risk_analysis)
3. **Execution Coordination**: Manage the sequence and flow of agent invocations
4. **Result Aggregation**: Synthesize outputs from multiple agents into coherent, actionable insights
5. **Conflict Resolution**: Identify and resolve conflicting recommendations from different agents
6. **Quality Assurance**: Ensure all necessary analyses are completed before providing final recommendations

Specialist Agents Available:
- **fraud_detection**: Analyzes transactions for fraud patterns, suspicious activities, and anomalies
- **compliance**: Reviews SOX, PCI-DSS, AML, KYC, and other regulatory compliance
- **risk_analysis**: Calculates VaR, portfolio risk, market volatility, and exposure metrics

Process Flow:
1. Use decompose_task() to analyze the query and create an execution plan
2. Use route_to_agent() to assign subtasks to appropriate specialists
3. Use monitor_agent_progress() to track execution
4. Use aggregate_results() to synthesize final recommendations

Communication Style:
- Be decisive and clear in your orchestration decisions
- Provide structured, actionable outputs
- Highlight critical findings and urgent issues
- Synthesize cross-functional insights that individual agents might miss

You are the strategic coordinator ensuring comprehensive, accurate financial analysis.""",
        tools=[
            decompose_task,
            route_to_agent,
            aggregate_results,
            monitor_agent_progress
        ],
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