# ============================================
# services/britive_client.py - Enhanced Version
# ============================================
"""
Britive client for managing AWS credentials.
Now supports agent-specific profiles.
"""
import subprocess
import json
import os
import boto3
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class BritiveClient:
    """
    Manages Britive credential checkout and checkin.
    Now supports multiple agent-specific profiles.
    
    Usage:
        # Direct usage
        client = BritiveClient(profile="...", tenant="...")
        if client.checkout():
            session = client.get_boto_session()
            # Use session for AWS operations
        client.checkin()
        
        # Or use as context manager
        with BritiveClient(profile="...", tenant="...") as client:
            session = client.get_boto_session()
            # Use session...
    """
    
    def __init__(self, profile: str, tenant: str, region: str = 'us-west-2'):
        """
        Initialize Britive client.
        
        Args:
            profile: Britive profile path
            tenant: Britive tenant
            region: AWS region
        """
        self.profile = profile
        self.tenant = tenant
        self.region = region
        self.credentials: Optional[Dict] = None
        self._boto_session: Optional[boto3.Session] = None
        
        # Log which profile is being used
        logger.info(f"📋 Initialized BritiveClient")
        logger.info(f"   Profile: {self._mask_profile(profile)}")
        logger.info(f"   Tenant: {tenant}")
        logger.info(f"   Region: {region}")
    
    def _mask_profile(self, profile: str) -> str:
        """Mask sensitive parts of profile name for logging."""
        parts = profile.split('/')
        if len(parts) > 2:
            return f"{parts[0]}/***/{parts[-1]}"
        return profile
    
    def checkout(self) -> bool:
        """
        Checkout Britive credentials and store them.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("🔑 Checking out Britive credentials...")
        logger.info(f"   Profile: {self.profile}")
        logger.info(f"   Tenant: {self.tenant}")
        
        try:
            result = subprocess.run(
                ["pybritive", "checkout", self.profile, "-t", self.tenant],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Britive checkout failed (exit code {result.returncode})")
                logger.error(f"   stderr: {result.stderr}")
                return False
            
            # Parse credentials from stdout
            output = result.stdout.strip()
            
            # Find the JSON part (starts with '{')
            json_start = output.find('{')
            if json_start == -1:
                logger.error(f"❌ No JSON found in pybritive output")
                logger.error(f"   Output: {output[:200]}...")
                return False
            
            json_str = output[json_start:]
            
            try:
                self.credentials = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse credentials JSON: {e}")
                logger.error(f"   JSON string: {json_str[:200]}...")
                return False
            
            # Validate required keys
            required_keys = ['AccessKeyId', 'SecretAccessKey', 'SessionToken']
            missing_keys = [k for k in required_keys if k not in self.credentials]
            if missing_keys:
                logger.error(f"❌ Missing required credential keys: {missing_keys}")
                return False
            
            # Set environment variables for AWS CLI/SDK compatibility
            os.environ['AWS_ACCESS_KEY_ID'] = self.credentials['AccessKeyId']
            os.environ['AWS_SECRET_ACCESS_KEY'] = self.credentials['SecretAccessKey']
            os.environ['AWS_SESSION_TOKEN'] = self.credentials['SessionToken']
            os.environ['AWS_DEFAULT_REGION'] = self.region
            
            # Create boto3 session with explicit credentials
            self._boto_session = boto3.Session(
                aws_access_key_id=self.credentials['AccessKeyId'],
                aws_secret_access_key=self.credentials['SecretAccessKey'],
                aws_session_token=self.credentials['SessionToken'],
                region_name=self.region
            )
            
            logger.info("✅ Britive credentials checked out successfully")
            logger.info(f"   Access Key: {self.credentials['AccessKeyId'][:10]}...")
            if 'Expiration' in self.credentials:
                logger.info(f"   Expiration: {self.credentials['Expiration']}")
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Britive checkout timed out")
            return False
        except FileNotFoundError:
            logger.error("❌ pybritive command not found. Install with: pip install pybritive")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during checkout: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def checkin(self) -> bool:
        """
        Checkin Britive credentials.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("🔓 Checking in Britive credentials...")
        
        try:
            result = subprocess.run(
                ["pybritive", "checkin", self.profile, "-t", self.tenant],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("✅ Britive credentials checked in successfully")
            else:
                logger.warning(f"⚠️ Britive checkin returned code {result.returncode}")
                logger.warning(f"   stderr: {result.stderr}")
            
            return result.returncode == 0
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking in credentials: {e}")
            return False
        finally:
            # Clear stored credentials regardless of checkin success
            self.credentials = None
            self._boto_session = None
            
            # Clear environment variables
            for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']:
                os.environ.pop(key, None)
    
    def get_boto_session(self) -> boto3.Session:
        """
        Get boto3 session with Britive credentials.
        
        Returns:
            boto3.Session: Session configured with Britive credentials,
                          or default session if no credentials available
        """
        if self._boto_session is not None:
            return self._boto_session
        
        if self.credentials:
            # Create session from stored credentials
            self._boto_session = boto3.Session(
                aws_access_key_id=self.credentials['AccessKeyId'],
                aws_secret_access_key=self.credentials['SecretAccessKey'],
                aws_session_token=self.credentials['SessionToken'],
                region_name=self.region
            )
            return self._boto_session
        
        # Fallback to default session (uses env vars or ~/.aws/credentials)
        logger.warning("⚠️ No Britive credentials - using default boto3 session")
        return boto3.Session(region_name=self.region)
    
    def verify_credentials(self) -> bool:
        """
        Verify that AWS credentials are working.
        
        Returns:
            bool: True if credentials are valid
        """
        try:
            session = self.get_boto_session()
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            
            logger.info("✅ AWS credentials verified")
            logger.info(f"   Account: {identity.get('Account')}")
            logger.info(f"   ARN: {identity.get('Arn')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to verify AWS credentials: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry - checkout credentials"""
        if not self.checkout():
            raise Exception(f"Failed to checkout Britive credentials for profile: {self.profile}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - checkin credentials"""
        self.checkin()
        return False  # Don't suppress exceptions