#!/bin/bash
# You need to run this script only one time
# Once AgentCore Agents are deployed, you get the ID and that is what you use in your code

# Step 1: Checkout AWS profile using pybritive
CREDS_JSON=$(pybritive checkout "aws_standalone_app_513826297540/513826297540 (aws_standalone_app_513826297540_environment)/AWS Admin Full Access" -t agentic-ai)

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
EXECUTION_ROLE="arn:aws:iam::513826297540:role/service-role/AmazonBedrockAgentCoreRuntimeServiceRole-shahzad"
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
agentcore launch \
  --agent "$RISK_AGENT_NAME" \
  --auto-update-on-conflict \
  --env STAGE=prod \
  --env LOG_LEVEL=debug

# After the agents are "launched" the next step is to use the agentcore invoke command to "invoke" agentic AI agents
