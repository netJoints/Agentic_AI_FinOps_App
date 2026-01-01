# ============================================
# services/britive_client.py
# ============================================
"""
Britive client for managing AWS credentials
"""
import subprocess
import boto3


class BritiveClient:
    """Manages Britive credential checkout and checkin"""
    
    def __init__(self, profile: str, tenant: str):
        self.profile = profile
        self.tenant = tenant
    
    def checkout(self):
        """Checkout Britive credentials"""
        print("🔑 Checking out Britive credentials...")
        try:
            result = subprocess.run(
                ["pybritive", "checkout", self.profile, "-t", self.tenant],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            print("✅ Britive credentials checked out successfully")
            return True
        except Exception as e:
            print(f"❌ Error checking out credentials: {e}")
            return False
    
    def checkin(self):
        """Checkin Britive credentials"""
        print("🔓 Checking in Britive credentials...")
        try:
            subprocess.run(
                ["pybritive", "checkin", self.profile, "-t", self.tenant],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            print("✅ Britive credentials checked in successfully")
        except Exception as e:
            print(f"⚠️ Error checking in credentials: {e}")
    
    def get_boto_session(self):
        """Get boto3 session with Britive credentials"""
        return boto3.Session()