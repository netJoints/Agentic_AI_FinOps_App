# ============================================
# britive_checkout.py - Britive JIT credential helper for AgentCore agents
# ============================================
"""
Provides a context manager for per-agent Britive profile checkout.

Each specialist agent calls britive_session() before accessing AWS resources,
ensuring it uses its own scoped credentials rather than inheriting shared ones.

Authentication: fetches the Britive API token from AWS Secrets Manager at runtime
using the container's IAM execution role. No tokens stored in .env or source code.

Secret name in Secrets Manager: britive/api-token
"""
import subprocess
import json
import os
import logging
import boto3
from contextlib import contextmanager

logger = logging.getLogger(__name__)

BRITIVE_TENANT = os.environ.get("BRITIVE_TENANT", "agentic-ai")
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
SECRETS_MANAGER_SECRET_NAME = "britive/api-token"

_cached_api_token = None


def _get_britive_api_token() -> str:
    """
    Retrieve the Britive API token.

    Order of precedence:
    1. BRITIVE_API_TOKEN env var (useful for local dev/testing only)
    2. AWS Secrets Manager — fetched using the container's IAM execution role.
       Secret name: britive/api-token
    """
    global _cached_api_token

    # 1. Env var override (local dev only — never set this in production .env)
    token = os.environ.get("BRITIVE_API_TOKEN", "")
    if token:
        return token

    # 2. Return cached value to avoid repeated Secrets Manager calls
    if _cached_api_token:
        return _cached_api_token

    # 3. Fetch from AWS Secrets Manager using the execution role
    logger.info(f"🔐 Fetching Britive API token from Secrets Manager ({SECRETS_MANAGER_SECRET_NAME})")
    try:
        sm = boto3.client("secretsmanager", region_name=AWS_REGION)
        response = sm.get_secret_value(SecretId=SECRETS_MANAGER_SECRET_NAME)
        secret = response.get("SecretString", "")
        # Support both plain string and JSON {"token": "..."} formats
        try:
            secret = json.loads(secret).get("token", secret)
        except (json.JSONDecodeError, AttributeError):
            pass
        if not secret:
            raise ValueError("Secret value is empty")
        _cached_api_token = secret
        logger.info("✅ Britive API token retrieved from Secrets Manager")
        return _cached_api_token
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve Britive API token from Secrets Manager: {e}")


def _checkout(profile: str) -> dict:
    """
    Call pybritive checkout for the given profile and return AWS credentials dict.
    Raises on failure.
    """
    api_token = _get_britive_api_token()

    env = os.environ.copy()
    env["BRITIVE_API_TOKEN"] = api_token

    logger.info(f"🔑 Britive checkout: profile='{profile}' tenant='{BRITIVE_TENANT}'")

    result = subprocess.run(
        ["pybritive", "checkout", profile, "-t", BRITIVE_TENANT, "--mode", "json"],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Britive checkout failed (exit {result.returncode}): {result.stderr.strip()}"
        )

    # Output may have informational lines before the JSON blob
    output = result.stdout.strip()
    json_start = output.find("{")
    if json_start == -1:
        raise RuntimeError(f"No JSON credentials in pybritive output: {output[:300]}")

    credentials = json.loads(output[json_start:])

    required = {"AccessKeyId", "SecretAccessKey", "SessionToken"}
    missing = required - credentials.keys()
    if missing:
        raise RuntimeError(f"Credential response missing keys: {missing}")

    logger.info(f"✅ Checked out credentials (key={credentials['AccessKeyId'][:10]}...)")
    return credentials


def _checkin(profile: str) -> None:
    """Call pybritive checkin for the given profile. Logs but does not raise on error."""
    api_token = os.environ.get("BRITIVE_API_TOKEN", "")
    env = os.environ.copy()
    if api_token:
        env["BRITIVE_API_TOKEN"] = api_token

    logger.info(f"🔓 Britive checkin: profile='{profile}'")
    try:
        result = subprocess.run(
            ["pybritive", "checkin", profile, "-t", BRITIVE_TENANT],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        if result.returncode != 0:
            logger.warning(f"⚠️ Checkin returned code {result.returncode}: {result.stderr.strip()}")
        else:
            logger.info("✅ Britive credentials checked in")
    except Exception as e:
        logger.warning(f"⚠️ Checkin error (credentials may auto-expire): {e}")


@contextmanager
def britive_session(profile: str, region: str = None):
    """
    Context manager: checkout Britive credentials for `profile`, yield a
    boto3.Session scoped to those credentials, then checkin on exit.

    Usage:
        with britive_session(BRITIVE_PROFILE) as session:
            s3 = session.client('s3')
            s3.get_object(...)
    """
    region = region or AWS_REGION
    credentials = _checkout(profile)

    session = boto3.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name=region,
    )

    try:
        yield session
    finally:
        _checkin(profile)
