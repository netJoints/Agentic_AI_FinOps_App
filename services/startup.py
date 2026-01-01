# ============================================
# services/startup.py - FIXED for dot output
# ============================================
"""
Startup initialization for FinOps application
"""
import subprocess
import json
import logging
import os

logger = logging.getLogger(__name__)


class StartupManager:
    """Handles application startup tasks"""
    
    def __init__(self, britive_profile: str, britive_tenant: str):
        self.britive_profile = britive_profile
        self.britive_tenant = britive_tenant
    
    def checkout_britive_credentials(self) -> bool:
        """Checkout Britive credentials and set environment variables"""
        try:
            logger.info("🔐 Checking out Britive credentials...")
            
            # Checkout credentials
            cmd = [
                "pybritive", "checkout",
                self.britive_profile,
                "-t", self.britive_tenant
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Britive checkout failed: {result.stderr}")
                return False
            
            # Parse credentials from stdout
            # pybritive outputs a dot (.) followed by JSON
            output = result.stdout.strip()
            
            # Find the JSON part (starts with '{')
            json_start = output.find('{')
            if json_start == -1:
                logger.error(f"❌ No JSON found in output: {output}")
                return False
            
            json_str = output[json_start:]
            
            try:
                creds = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Could not parse credentials: {e}")
                logger.error(f"Output: {output}")
                return False
            
            # Validate required keys
            required_keys = ['AccessKeyId', 'SecretAccessKey', 'SessionToken']
            if not all(key in creds for key in required_keys):
                logger.error(f"❌ Missing required credentials keys")
                return False
            
            # Set environment variables
            os.environ['AWS_ACCESS_KEY_ID'] = creds['AccessKeyId']
            os.environ['AWS_SECRET_ACCESS_KEY'] = creds['SecretAccessKey']
            os.environ['AWS_SESSION_TOKEN'] = creds['SessionToken']
            os.environ['AWS_PROFILE'] = self.britive_tenant
            os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
            
            logger.info("✅ Britive credentials checked out successfully")
            logger.info(f"   Access Key: {creds['AccessKeyId'][:10]}...")
            logger.info(f"   Expiration: {creds.get('Expiration', 'N/A')}")
            
            # Verify AWS access
            self._verify_aws_access()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking out Britive credentials: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _verify_aws_access(self):
        """Verify AWS credentials are working"""
        try:
            result = subprocess.run(
                ["aws", "sts", "get-caller-identity"],
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )
            
            if result.returncode == 0:
                identity = json.loads(result.stdout)
                logger.info(f"✅ AWS Identity verified: {identity.get('Arn', 'Unknown')}")
                logger.info(f"   Account: {identity.get('Account', 'Unknown')}")
                logger.info(f"   User ID: {identity.get('UserId', 'Unknown')}")
            else:
                logger.warning(f"⚠️ Could not verify AWS identity: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not verify AWS identity: {e}")
    
    def initialize_agent_sessions(self) -> dict:
        """Initialize agent sessions using agentcore CLI (optional)"""
        sessions = {}
        agents = [
            'finops_supervisor_ai_agent',
            'finops_risk_ai_agent',
            'finops_compliance_ai_agent',
            'finops_fraud_ai_agent'
        ]
        
        logger.info("🤖 Initializing agent sessions...")
        
        for agent in agents:
            try:
                # Invoke agent with a simple hello to initialize session
                cmd = [
                    "agentcore", "invoke",
                    "--agent", agent,
                    '{"prompt": "Initialize session"}'
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    env=os.environ.copy()
                )
                
                if result.returncode == 0:
                    # Extract session ID from output
                    for line in result.stdout.split('\n'):
                        if 'Session ID:' in line:
                            session_id = line.split('Session ID:')[1].strip()
                            sessions[agent] = session_id
                            logger.info(f"✅ {agent}: {session_id}")
                            break
                else:
                    logger.warning(f"⚠️ Could not initialize {agent}: {result.stderr}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error initializing {agent}: {e}")
        
        return sessions
    
    def run_startup_tasks(self) -> bool:
        """Run all startup tasks"""
        logger.info("🚀 Running startup tasks...")
        
        # 1. Checkout Britive credentials
        if not self.checkout_britive_credentials():
            return False
        
        # 2. Initialize agent sessions (optional - uncomment if needed)
        # sessions = self.initialize_agent_sessions()
        
        logger.info("✅ Startup tasks completed successfully")
        return True