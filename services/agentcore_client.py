# ============================================
# services/agentcore_client.py - FIXED VERSION
# ============================================
"""
AgentCore client for invoking agents using Bedrock AgentCore Runtime API.

This version:
- Uses the correct boto3 client ('bedrock-agentcore')
- Properly handles streaming responses
- Maintains session continuity when needed
- Enriches queries with relevant financial data
"""
import uuid
import json
from typing import Dict, List, Optional
import boto3
import logging
from config import Config
from .financial_data import FinancialDataService
from .britive_helper import checkout_credentials_for_agent

logger = logging.getLogger(__name__)


class AgentCoreClient:
    """
    Client for invoking Bedrock AgentCore agents.
    
    This client orchestrates multiple specialist agents (fraud, compliance, risk)
    based on query content and aggregates their responses.
    """
    
    def __init__(self, boto_session: boto3.Session):
        """
        Initialize the AgentCore client.
        
        Args:
            boto_session: Configured boto3 session with AWS credentials
        """
        # Use bedrock-agentcore client with the new public endpoint (migrated from preview)
        # New data plane endpoint: https://docs.aws.amazon.com/general/latest/gr/bedrock_agentcore.html
        self.client = boto_session.client(
            'bedrock-agentcore',
            region_name=Config.AWS_REGION,
            endpoint_url=f'https://bedrock-agentcore.{Config.AWS_REGION}.amazonaws.com'
        )
        self.data_service = FinancialDataService()
        self.config = Config()
        logger.info("🤖 AgentCore Client initialized")
    
    def _enrich_query_with_data(self, query: str, agent_type: str) -> str:
        """
        Enrich query with real-time financial data relevant to the agent type.
        
        Args:
            query: Original user query
            agent_type: Type of agent (fraud_detection, compliance, risk_analysis)
            
        Returns:
            Enriched query string with relevant data
        """
        logger.info(f"📊 Enriching query for agent: {agent_type}")
        
        # For risk analysis: check if query already has portfolio data
        if agent_type == "risk_analysis":
            query_lower = query.lower()
            has_value = any(ind in query_lower for ind in ['$', 'portfolio', 'value', '000', 'k '])
            
            if has_value:
                logger.info("✅ Query already contains portfolio data")
                return query
            
            # Add default portfolio data for vague queries
            portfolio_stocks = self.data_service.get_multiple_stocks(["AAPL", "MSFT", "GOOGL"])
            ratios = self.data_service.get_financial_ratios("AAPL")
            
            enriched = f"{query}\n\n=== PORTFOLIO DATA ===\n"
            enriched += "Portfolio Value: $1,000,000\n\n"
            enriched += "Stock Holdings:\n"
            for stock in portfolio_stocks:
                enriched += f"  - {stock.get('symbol', 'N/A')}: ${stock.get('price', 0):.2f}\n"
            enriched += f"\nPlease calculate VaR and analyze portfolio risk.\n"
            return enriched
        
        # Build enriched query for other agents
        enriched = f"{query}\n\n=== REAL-TIME FINANCIAL DATA ===\n"
        
        if agent_type == "fraud_detection":
            transactions = self.data_service.generate_sample_transactions(10)
            enriched += f"\n📊 TRANSACTION DATA:\n"
            
            for i, txn in enumerate(transactions, 1):
                enriched += f"\nTransaction #{i}:\n"
                enriched += f"  - ID: {txn.get('transaction_id', 'N/A')}\n"
                enriched += f"  - Amount: ${txn.get('amount', 0):.2f}\n"
                enriched += f"  - Merchant: {txn.get('merchant', 'N/A')}\n"
                enriched += f"  - Risk Score: {txn.get('risk_score', 0):.2f}\n"
                enriched += f"  - Status: {txn.get('flag', 'N/A')}\n"
            
            enriched += "\nAnalyze these transactions for fraud patterns and suspicious activity.\n"
            logger.info(f"✅ Added {len(transactions)} transactions to query")
            
        elif agent_type == "compliance":
            compliance = self.data_service.get_compliance_data()
            enriched += f"\n✅ COMPLIANCE STATUS:\n\n"
            
            if 'sox_compliance' in compliance:
                sox = compliance['sox_compliance']
                enriched += f"SOX Compliance:\n"
                enriched += f"  - Score: {sox.get('compliance_score', 'N/A')}%\n"
                enriched += f"  - Status: {sox.get('status', 'N/A')}\n"
                enriched += f"  - Controls Passed: {sox.get('controls_passed', 0)}/{sox.get('controls_tested', 0)}\n\n"
            
            if 'pci_dss' in compliance:
                pci = compliance['pci_dss']
                enriched += f"PCI-DSS:\n"
                enriched += f"  - Status: {pci.get('status', 'N/A')}\n"
                enriched += f"  - Requirements Met: {pci.get('requirements_met', 0)}/{pci.get('total_requirements', 0)}\n\n"
            
            if 'aml_monitoring' in compliance:
                aml = compliance['aml_monitoring']
                enriched += f"AML Monitoring:\n"
                enriched += f"  - Status: {aml.get('status', 'N/A')}\n"
                enriched += f"  - Suspicious Activities: {aml.get('suspicious_activities', 0)}\n"
                enriched += f"  - Reports Filed: {aml.get('reports_filed', 0)}\n\n"
            
            enriched += "Analyze compliance status and provide recommendations.\n"
            logger.info("✅ Added compliance data to query")
        
        return enriched
    
    def _determine_agents(self, query: str) -> List[str]:
        """
        Determine which agents to invoke based on query keywords.
        
        Args:
            query: User query string
            
        Returns:
            List of agent types to invoke
        """
        query_lower = query.lower()
        agents = []
        
        # Fraud detection keywords
        fraud_keywords = ['fraud', 'transaction', 'suspicious', 'anomaly', 'unusual', 'scam']
        if any(word in query_lower for word in fraud_keywords):
            agents.append('fraud_detection')
        
        # Compliance keywords
        compliance_keywords = ['compliance', 'sox', 'pci', 'regulation', 'regulatory', 'audit', 'aml', 'kyc']
        if any(word in query_lower for word in compliance_keywords):
            agents.append('compliance')
        
        # Risk analysis keywords
        risk_keywords = ['risk', 'var', 'portfolio', 'stress', 'volatility', 'stock', 'calculate', 'invested']
        if any(word in query_lower for word in risk_keywords):
            agents.append('risk_analysis')
        
        # Default to fraud detection if no keywords match
        if not agents:
            logger.info("⚠️ No keywords matched - defaulting to fraud_detection")
            agents.append('fraud_detection')
        
        logger.info(f"🎯 Agents to invoke: {', '.join(agents)}")
        return agents
    
    def invoke_agent(self, agent_type: str, query: str, session_id: str) -> Dict:
        """
        Invoke a single AgentCore agent.
        
        Args:
            agent_type: Type of agent to invoke
            query: Query string (will be enriched with data)
            session_id: Session ID for conversation continuity
            
        Returns:
            Dict with success status and response or error
        """
        logger.info(f"🚀 Invoking {agent_type} agent...")
        
        # Get agent configuration
        agent_config = self.config.AGENTS.get(agent_type)
        if not agent_config:
            return {
                "success": False,
                "error": f"Unknown agent type: {agent_type}",
                "agent": agent_type
            }
        
        # Check if agent is configured
        if not self.config.is_agent_configured(agent_type):
            logger.error(f"❌ Agent {agent_type} not configured")
            return {
                "success": False,
                "error": f"Agent {agent_type} not configured. Update config.py with agent IDs.",
                "agent": agent_type
            }
        
        agent_arn = agent_config["agent_arn"]
        logger.info(f"📍 Agent ARN: {agent_arn}")
        logger.info(f"📍 Session ID: {session_id}")

        # Enrich query with relevant data
        enriched_query = self._enrich_query_with_data(query, agent_type)
        logger.info(f"📤 Query length: {len(enriched_query)} chars")

        # Checkout this agent's specific Britive profile (runs locally, browser auth if needed)
        britive_client = checkout_credentials_for_agent(agent_type)
        if britive_client:
            logger.info(f"✅ Using {agent_type}-specific Britive credentials")
            invoke_client = britive_client.get_boto_session().client(
                'bedrock-agentcore',
                region_name=Config.AWS_REGION,
                endpoint_url=f'https://bedrock-agentcore.{Config.AWS_REGION}.amazonaws.com'
            )
        else:
            logger.warning(f"⚠️ Could not checkout {agent_type} profile, falling back to supervisor credentials")
            invoke_client = self.client

        try:
            # Prepare payload
            payload_data = {"inputText": enriched_query}

            # Invoke the agent using AgentCore Runtime API
            response = invoke_client.invoke_agent_runtime(
                agentRuntimeArn=agent_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(payload_data).encode('utf-8'),
                contentType='application/json',
                accept='application/json'
            )
            
            logger.info(f"📥 Response received from AgentCore")
            
            # Parse the response
            full_response = self._parse_response(response)
            
            if not full_response.strip():
                full_response = f"Agent {agent_type} completed but returned empty response."
            
            logger.info(f"✅ {agent_type} responded ({len(full_response)} chars)")
            return {
                "success": True,
                "response": full_response,
                "agent": agent_type
            }
            
        except self.client.exceptions.ResourceNotFoundException as e:
            logger.error(f"❌ Agent not found: {e}")
            return {
                "success": False,
                "error": f"Agent {agent_type} not found. Verify the ARN is correct.",
                "agent": agent_type
            }
        except self.client.exceptions.AccessDeniedException as e:
            logger.error(f"❌ Access denied: {e}")
            return {
                "success": False,
                "error": f"Access denied to {agent_type}. Check IAM permissions.",
                "agent": agent_type
            }
        except Exception as e:
            logger.error(f"❌ Error invoking {agent_type}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "agent": agent_type
            }
        finally:
            if britive_client:
                logger.info(f"🔓 Checking in {agent_type} Britive credentials")
                britive_client.checkin()

    def _parse_response(self, response: Dict) -> str:
        """
        Parse the AgentCore response and extract the text content.
        
        Args:
            response: Raw response from AgentCore API
            
        Returns:
            Extracted text response
        """
        full_response = ""
        
        # Handle StreamingBody response
        if 'response' in response:
            try:
                streaming_body = response['response']
                response_bytes = streaming_body.read()
                response_text = response_bytes.decode('utf-8')
                
                try:
                    response_json = json.loads(response_text)
                    full_response = self._extract_text_from_json(response_json)
                except json.JSONDecodeError:
                    full_response = response_text
                    
            except Exception as e:
                logger.error(f"Error reading streaming body: {e}")
                full_response = f"Error reading response: {e}"
        
        # Handle payload response
        elif 'payload' in response:
            payload = response['payload']
            if isinstance(payload, bytes):
                payload_str = payload.decode('utf-8')
            else:
                payload_str = str(payload)
            
            try:
                payload_json = json.loads(payload_str)
                full_response = self._extract_text_from_json(payload_json)
            except json.JSONDecodeError:
                full_response = payload_str
        
        # Handle streaming completion
        elif 'completion' in response:
            for chunk in response['completion']:
                if 'text' in chunk:
                    full_response += chunk['text']
                elif 'content' in chunk:
                    full_response += chunk['content']
                elif 'chunk' in chunk and 'bytes' in chunk['chunk']:
                    full_response += chunk['chunk']['bytes'].decode('utf-8')
        
        else:
            logger.warning(f"⚠️ Unexpected response structure: {list(response.keys())}")
            full_response = json.dumps(response, indent=2, default=str)
        
        return full_response
    
    def _extract_text_from_json(self, data: Dict) -> str:
        """
        Extract text content from various JSON response formats.
        
        Args:
            data: Parsed JSON response
            
        Returns:
            Extracted text
        """
        # Try various known response formats
        if 'result' in data:
            result = data['result']
            if isinstance(result, str):
                return result
            if isinstance(result, dict):
                if 'content' in result and isinstance(result['content'], list):
                    return '\n'.join(item.get('text', '') for item in result['content'] if 'text' in item)
                if 'text' in result:
                    return result['text']
                if 'message' in result:
                    return result['message']
        
        if 'content' in data and isinstance(data['content'], list):
            return '\n'.join(item.get('text', '') for item in data['content'] if 'text' in item)
        
        if 'output' in data:
            return data['output']
        
        if 'text' in data:
            return data['text']
        
        if 'message' in data:
            return data['message']
        
        # Fallback: return formatted JSON
        return json.dumps(data, indent=2)
    
    def orchestrate(self, query: str, session_id: Optional[str] = None) -> Dict:
        """
        Orchestrate multiple agents based on the query content.
        
        Args:
            query: User query
            session_id: Optional session ID (generated if not provided)
            
        Returns:
            Dict with aggregated results from all invoked agents
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        logger.info(f"🎭 Starting orchestration")
        logger.info(f"📝 Query: {query[:100]}...")
        logger.info(f"🔑 Session: {session_id}")
        
        # Determine which agents to call
        agents_to_call = self._determine_agents(query)
        results = {}
        
        # Invoke each agent
        for agent_type in agents_to_call:
            logger.info(f"⏳ Processing: {agent_type}")
            
            # Generate unique session for each agent to avoid context pollution
            agent_session = f"{session_id}-{agent_type}-{uuid.uuid4().hex[:8]}"
            
            result = self.invoke_agent(agent_type, query, agent_session)
            results[agent_type] = result
        
        # Aggregate responses
        successful_responses = []
        errors = []
        
        for agent_type, result in results.items():
            if result["success"]:
                header = agent_type.replace('_', ' ').title()
                successful_responses.append(f"### {header}\n\n{result['response']}")
                logger.info(f"✅ {agent_type}: Success")
            else:
                errors.append(f"❌ {agent_type}: {result['error']}")
                logger.error(f"❌ {agent_type}: {result['error']}")
        
        # Combine responses
        combined_response = "\n\n---\n\n".join(successful_responses)
        
        if errors:
            combined_response += f"\n\n**Errors:**\n" + "\n".join(errors)
        
        logger.info(f"🏁 Orchestration complete: {len(successful_responses)} success, {len(errors)} errors")
        
        return {
            "success": len(successful_responses) > 0,
            "response": combined_response,
            "agents_invoked": agents_to_call,
            "session_id": session_id,
            "results": {k: {"success": v["success"]} for k, v in results.items()}
        }
