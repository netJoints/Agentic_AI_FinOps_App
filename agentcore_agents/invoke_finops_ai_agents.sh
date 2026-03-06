#!/bin/bash

# Load .env from project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
if [ -f "$ENV_FILE" ]; then
  set -a && source "$ENV_FILE" && set +a
  echo "✅ Loaded .env"
else
  echo "⚠️  No .env file found at $ENV_FILE — using existing environment variables"
fi

# Step 1: Checkout AWS profile (writes to ~/.aws/credentials under [agentic-ai])
pybritive checkout "${BRITIVE_CHECKOUT_PROFILE}" -t "${BRITIVE_TENANT}"

# Step 2: Also extract and export credentials as environment variables
CREDS_JSON=$(pybritive checkout "${BRITIVE_CHECKOUT_PROFILE}" -t "${BRITIVE_TENANT}")
AWS_ACCESS_KEY_ID=$(echo "$CREDS_JSON" | jq -r '.AccessKeyId')
AWS_SECRET_ACCESS_KEY=$(echo "$CREDS_JSON" | jq -r '.SecretAccessKey')
AWS_SESSION_TOKEN=$(echo "$CREDS_JSON" | jq -r '.SessionToken')

export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_SESSION_TOKEN
export AWS_PROFILE=agentic-ai
export AWS_DEFAULT_REGION=us-west-2



# Verify AWS credentials are working
echo "=== Verifying AWS Access ==="
aws sts get-caller-identity --profile agentic-ai

agentcore configure list

echo ""
echo "=== Invoking Supervisor Agent ==="
# agentcore invoke --agent finops_supervisor_ai_agent '{"prompt": "hello supervisor agent"}'
agentcore invoke --agent finops_risk_ai_agent '{"prompt": "Calculate: VaR 95%, $100k, 60% SPY + 30% AGG + 10% GLD, 1 month"}'
# agentcore invoke --agent finops_compliance_ai_agent '{"prompt": "hello compliance agent"}'
# agentcore invoke --agent finops_fraud_ai_agent '{"prompt": "hello fraud agent"}'
