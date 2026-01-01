# ============================================
# services/agentcore_client.py (FIXED WITH FRESH SESSIONS)
# ============================================
"""
AgentCore client for invoking agents using Bedrock AgentCore API
"""
import uuid
import json
from typing import Dict, List
import boto3
import logging
from config import Config
from .financial_data import FinancialDataService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentCoreClient:
    """Client for invoking AgentCore agents"""
    
    def __init__(self, boto_session: boto3.Session):
        self.client = boto_session.client('bedrock-agentcore')
        self.data_service = FinancialDataService()
        self.config = Config()
        logger.info("🤖 AgentCore Client initialized")
    
    def _enrich_query_with_data(self, query: str, agent_type: str) -> str:
        """Enrich query with real-time financial data"""
        logger.info(f"📊 Enriching query for agent type: {agent_type}")
        
        # FOR RISK ANALYSIS: Don't add extra data if query already has specifics
        if agent_type == "risk_analysis":
            # Check if query already contains portfolio value
            query_lower = query.lower()
            has_value = any(indicator in query_lower for indicator in ['$', 'portfolio', 'value', 'k', '000'])
            
            if has_value:
                # Query already has data - don't add more, just pass it through
                logger.info("✅ Query already contains portfolio data - passing through directly")
                return query
            else:
                # Only add data if query is vague
                portfolio_stocks = self.data_service.get_multiple_stocks(["AAPL", "MSFT", "GOOGL"])
                ratios = self.data_service.get_financial_ratios("AAPL")
                
                enriched_query = f"{query}\n\n=== PORTFOLIO DATA ===\n"
                enriched_query += f"Portfolio Value: $1,000,000\n\n"
                
                enriched_query += "Stock Holdings:\n"
                for stock in portfolio_stocks:
                    enriched_query += f"  - {stock.get('symbol', 'N/A')}: ${stock.get('price', 0):.2f}\n"
                
                enriched_query += f"\nPlease calculate VaR and analyze portfolio risk.\n"
                logger.info("✅ Added portfolio data for vague query")
                return enriched_query
        
        # For other agents, use original enrichment logic
        enriched_query = f"{query}\n\n=== REAL-TIME FINANCIAL DATA ===\n"
        
        if agent_type == "fraud_detection":
            transactions = self.data_service.generate_sample_transactions(10)
            enriched_query += f"\n📊 TRANSACTION DATA:\n"
            
            for i, txn in enumerate(transactions, 1):
                enriched_query += f"\nTransaction #{i}:\n"
                enriched_query += f"  - Amount: ${txn.get('amount', 0):.2f}\n"
                enriched_query += f"  - Risk Score: {txn.get('risk_score', 0):.2f}\n"
                enriched_query += f"  - Status: {txn.get('flag', 'N/A')}\n"
            
            enriched_query += "\nAnalyze these transactions for fraud.\n"
            logger.info(f"✅ Added {len(transactions)} transactions")
        
        elif agent_type == "compliance":
            compliance = self.data_service.get_compliance_data()
            enriched_query += f"\n✅ COMPLIANCE STATUS:\n\n"
            
            if 'sox_compliance' in compliance:
                sox = compliance['sox_compliance']
                enriched_query += f"SOX: {sox.get('compliance_score', 'N/A')}% - {sox.get('status', 'N/A')}\n"
            
            if 'pci_dss' in compliance:
                pci = compliance['pci_dss']
                enriched_query += f"PCI-DSS: {pci.get('status', 'N/A')}\n"
            
            if 'aml_monitoring' in compliance:
                aml = compliance['aml_monitoring']
                enriched_query += f"AML: {aml.get('status', 'N/A')} ({aml.get('suspicious_activities', 0)} suspicious)\n"
            
            enriched_query += "\nAnalyze compliance and provide recommendations.\n"
            logger.info("✅ Added compliance data")
        
        return enriched_query
    
    def _determine_agents(self, query: str) -> List[str]:
        """Determine which agents to invoke based on query"""
        query_lower = query.lower()
        agents = []
        
        if any(word in query_lower for word in ['fraud', 'transaction', 'suspicious', 'anomaly']):
            agents.append('fraud_detection')
        
        if any(word in query_lower for word in ['compliance', 'sox', 'pci', 'regulation', 'regulatory']):
            agents.append('compliance')
        
        if any(word in query_lower for word in ['risk', 'var', 'portfolio', 'stress', 'volatility', 'stock', 'calculate']):
            agents.append('risk_analysis')
        
        # Default to fraud detection if no keywords match
        if not agents:
            agents.append('fraud_detection')
        
        logger.info(f"🎯 Determined agents to invoke: {', '.join(agents)}")
        return agents

    async def invoke_agent(self, agent_type: str, query: str, session_id: str) -> Dict:
        """Invoke a single AgentCore agent"""
        logger.info(f"🚀 Invoking {agent_type} agent...")
        agent_config = self.config.AGENTS[agent_type]

        # Check if agent is configured
        if agent_config["agent_id"].startswith("YOUR_"):
            logger.error(f"❌ Agent {agent_type} not configured")
            return {
                "success": False,
                "error": f"Agent {agent_type} not configured. Please deploy and update config.",
                "agent": agent_type
            }

        # CRITICAL FIX: Always generate a NEW session ID for each request
        # This prevents the agent from using cached/old conversation context
        session_id = str(uuid.uuid4())
        logger.info(f"🔑 Generated FRESH session ID: {session_id}")

        agent_arn = agent_config["agent_arn"]
        logger.info(f"📝 Agent ARN: {agent_arn}")
        logger.info(f"📝 Using session ID: {session_id}")

        # Enrich query with real-time data
        enriched_query = self._enrich_query_with_data(query, agent_type)
        
        # Log what we're actually sending
        logger.info(f"📤 Sending query to agent: {enriched_query[:200]}...")

        try:
            logger.info(f"📤 Sending request to Bedrock AgentCore...")
            
            # Prepare payload - use only inputText, no sessionId in payload
            payload_data = {
                "inputText": enriched_query
            }
            
            logger.info(f"📋 Payload keys: {list(payload_data.keys())}")
            
            # Use invoke_agent_runtime with correct parameters
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=agent_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(payload_data).encode('utf-8'),
                contentType='application/json',
                accept='application/json'
            )

            logger.info(f"📥 Response received from AgentCore")
            logger.info(f"📋 Response keys: {list(response.keys())}")

            # Parse response
            full_response = ""
            
            if 'response' in response:
                streaming_body = response['response']
                logger.info(f"📡 Reading StreamingBody response...")
                
                try:
                    response_bytes = streaming_body.read()
                    response_text = response_bytes.decode('utf-8')
                    logger.info(f"📦 Raw response: {response_text[:500]}...")
                    
                    try:
                        response_json = json.loads(response_text)
                        
                        if 'result' in response_json:
                            result = response_json['result']
                            if 'content' in result and isinstance(result['content'], list):
                                for item in result['content']:
                                    if 'text' in item:
                                        full_response += item['text'] + "\n"
                            elif 'text' in result:
                                full_response = result['text']
                            else:
                                full_response = json.dumps(result, indent=2)
                        elif 'content' in response_json and isinstance(response_json['content'], list):
                            for item in response_json['content']:
                                if 'text' in item:
                                    full_response += item['text'] + "\n"
                        elif 'output' in response_json:
                            full_response = response_json['output']
                        elif 'text' in response_json:
                            full_response = response_json['text']
                        elif 'message' in response_json:
                            full_response = response_json['message']
                        else:
                            full_response = json.dumps(response_json, indent=2)
                            
                    except json.JSONDecodeError:
                        full_response = response_text
                        
                except Exception as e:
                    logger.error(f"❌ Error reading streaming body: {e}")
                    full_response = f"Error reading response: {e}"
            
            elif 'payload' in response:
                payload_response = response['payload']
                if isinstance(payload_response, bytes):
                    payload_str = payload_response.decode('utf-8')
                else:
                    payload_str = str(payload_response)
                
                try:
                    payload_json = json.loads(payload_str)
                    if 'output' in payload_json:
                        full_response = payload_json['output']
                    elif 'text' in payload_json:
                        full_response = payload_json['text']
                    else:
                        full_response = json.dumps(payload_json, indent=2)
                except json.JSONDecodeError:
                    full_response = payload_str
            
            elif 'completion' in response:
                logger.info("📡 Processing streaming completion...")
                for chunk in response['completion']:
                    if 'text' in chunk:
                        full_response += chunk['text']
                    elif 'content' in chunk:
                        full_response += chunk['content']
                    elif 'chunk' in chunk:
                        inner_chunk = chunk['chunk']
                        if 'bytes' in inner_chunk:
                            full_response += inner_chunk['bytes'].decode('utf-8')
            else:
                logger.warning(f"⚠️ Unexpected response structure: {list(response.keys())}")
                full_response = json.dumps(response, indent=2, default=str)

            if not full_response.strip():
                full_response = f"Agent {agent_type} completed but returned empty response."

            logger.info(f"✅ Agent {agent_type} responded successfully ({len(full_response)} chars)")
            return {
                "success": True,
                "response": full_response,
                "agent": agent_type
            }

        except Exception as e:
            logger.error(f"❌ Error invoking {agent_type}: {str(e)}")
            logger.error(f"📋 Error type: {type(e).__name__}")
            import traceback
            logger.error(f"📋 Traceback:\n{traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "agent": agent_type
            }

    async def orchestrate(self, query: str, session_id: str = None) -> Dict:
        """Orchestrate multiple agents"""
        # Note: We generate a session_id here but each agent will generate its own fresh one
        if not session_id or len(session_id) < 33:
            session_id = str(uuid.uuid4())
            logger.info(f"🔑 Generated new session ID for orchestration: {session_id}")

        logger.info(f"🎭 Starting orchestration for query: '{query[:50]}...'")
        logger.info(f"🔑 Session ID: {session_id}")

        agents_to_call = self._determine_agents(query)
        results = {}

        for agent_type in agents_to_call:
            logger.info(f"⏳ Processing agent: {agent_type}")
            # Pass session_id but invoke_agent will generate a fresh one anyway
            result = await self.invoke_agent(agent_type, query, session_id)
            results[agent_type] = result

        # Aggregate responses
        successful_responses = []
        errors = []
        for agent_type, result in results.items():
            if result["success"]:
                successful_responses.append(
                    f"### {agent_type.replace('_', ' ').title()}\n\n{result['response']}"
                )
                logger.info(f"✅ {agent_type} completed successfully")
            else:
                errors.append(f"❌ {agent_type}: {result['error']}")
                logger.error(f"❌ {agent_type} failed: {result['error']}")

        combined_response = "\n\n---\n\n".join(successful_responses)
        if errors:
            combined_response += f"\n\n**Errors:**\n" + "\n".join(errors)

        logger.info(f"🏁 Orchestration complete: {len(successful_responses)} successful, {len(errors)} errors")
        return {
            "success": len(successful_responses) > 0,
            "response": combined_response,
            "agents_invoked": agents_to_call,
            "session_id": session_id
        }