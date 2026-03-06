#!/bin/bash
# You need to run this script only one time
# Once AgentCore Agents are deployed, you get the ID and that is what you use in your code

# Load .env from project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
if [ -f "$ENV_FILE" ]; then
  set -a && source "$ENV_FILE" && set +a
  echo "✅ Loaded .env"
else
  echo "⚠️  No .env file found at $ENV_FILE — using existing environment variables"
fi

# Step 1: Checkout AWS profile using pybritive
CREDS_JSON=$(pybritive checkout "${BRITIVE_CHECKOUT_PROFILE}" -t "${BRITIVE_TENANT}")

# Step 2: Extract credentials into shell variables
export AWS_ACCESS_KEY_ID=$(echo "$CREDS_JSON" | jq -r '.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS_JSON" | jq -r '.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo "$CREDS_JSON" | jq -r '.SessionToken')

# Step 3: Confirm credentials are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$AWS_SESSION_TOKEN" ]; then
  echo "❌ Failed to retrieve AWS credentials. Aborting deployment."
  exit 1
fi

# Step 4: Define variables for supervisor agent
RISK_AGENT_NAME="finops_risk_ai_agent"
RISK_AGENT_ENTRYPOINT="finops_risk_ai_agent.py"
# Set BEDROCK_EXECUTION_ROLE env var before running this script
# e.g. export BEDROCK_EXECUTION_ROLE="arn:aws:iam::123456789012:role/service-role/AmazonBedrockAgentCoreRuntimeServiceRole-yourname"
EXECUTION_ROLE="${BEDROCK_EXECUTION_ROLE}"
REQUIREMENTS_FILE="requirements.txt"

# Step 5: Run agentcore configure
echo "🚀 Running agentcore configure..."
agentcore configure \
  --name "$RISK_AGENT_NAME" \
  --entrypoint "$RISK_AGENT_ENTRYPOINT" \
  --execution-role "$EXECUTION_ROLE" \
  --requirements-file "$REQUIREMENTS_FILE" \
  --verbose

# Step 6: Launch the agent with environment variables and auto-update
echo "🚀 Launching agentcore..."
agentcore deploy \
  --agent "$RISK_AGENT_NAME" \
  --env STAGE=prod \
  --env LOG_LEVEL=debug

# After the agents are "launched" the next step is to use the agentcore invoke command to "invoke" agentic AI agents
