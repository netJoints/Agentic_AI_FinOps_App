# FinOps AI Multi-Agent System

Enterprise-grade financial analysis platform powered by Amazon Bedrock AgentCore with real-time data.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (Flask + HTML/CSS/JS)                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Flask API                               │
│                     /api/analyze                                │
└─────────────────────────────┬───────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Britive Client │  │  AgentCore      │  │  Financial Data │
│  (AWS Creds)    │  │  Client         │  │  Service        │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────────────────────────┐
│  AWS STS        │  │        Bedrock AgentCore            │
│  (JIT Creds)    │  │  ┌──────────┬──────────┬──────────┐ │
└─────────────────┘  │  │  Fraud   │Compliance│   Risk   │ │
                     │  │  Agent   │  Agent   │  Agent   │ │
                     │  └──────────┴──────────┴──────────┘ │
                     └─────────────────────────────────────┘
```

## 📁 Project Structure

```
finops_fixed/
├── app.py                      # Main Flask application
├── config.py                   # Configuration (agents, AWS, etc.)
├── requirements.txt            # Python dependencies
├── services/
│   ├── __init__.py
│   ├── agentcore_client.py     # AgentCore API client
│   ├── britive_client.py       # Britive credential manager
│   └── financial_data.py       # Yahoo Finance + sample data
├── routes/
│   ├── __init__.py
│   ├── api.py                  # REST API endpoints
│   └── views.py                # Web page routes
├── templates/
│   └── index.html              # Main dashboard UI
└── static/
    ├── css/
    │   └── styles.css          # Dashboard styles
    └── js/
        └── main.js             # Frontend JavaScript
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd finops_fixed
pip install -r requirements.txt
```

### 2. Configure Agents

Update `config.py` with your deployed agent ARNs:

```python
AGENTS = {
    "fraud_detection": {
        "agent_id": "your-fraud-agent-id",
        "agent_arn": "arn:aws:bedrock-agentcore:us-west-2:YOUR_ACCOUNT:runtime/your-fraud-agent-id"
    },
    # ... other agents
}
```

### 3. Configure Britive

Update the Britive profile in `config.py`:

```python
BRITIVE_PROFILE = "your-britive-profile"
BRITIVE_TENANT = "your-tenant"
```

### 4. Run the Application

```bash
python app.py
```

Visit: **http://localhost:5011**

## 🔧 API Endpoints

### `POST /api/analyze`

Submit a query for AI agent analysis.

**Request:**
```json
{
    "query": "Analyze recent transactions for fraud patterns",
    "session_id": "optional-session-id"
}
```

**Response:**
```json
{
    "success": true,
    "response": "Combined agent responses...",
    "agents_invoked": ["fraud_detection", "compliance"],
    "session_id": "session-123"
}
```

### `GET /api/financial-data`

Get real-time financial data.

**Parameters:**
- `type`: `stock`, `ratios`, `multiple`, `transactions`, `compliance`, `market`
- `symbol`: Stock ticker (default: AAPL)

**Example:**
```bash
curl "http://localhost:5011/api/financial-data?type=stock&symbol=MSFT"
```

### `GET /api/health`

Health check endpoint.

### `GET /api/agents`

List configured agents and their status.

### `GET /api/test-credentials`

Test Britive credential checkout (for debugging).

## 🤖 Agent Types

| Agent | Keywords | Purpose |
|-------|----------|---------|
| **fraud_detection** | fraud, transaction, suspicious, anomaly | Analyze transactions for fraud |
| **compliance** | compliance, sox, pci, regulation, audit | Check regulatory compliance |
| **risk_analysis** | risk, var, portfolio, volatility | Calculate portfolio risk |

## 🔑 Authentication Flow

1. User submits query via UI
2. Flask API calls Britive to checkout AWS credentials
3. Britive returns temporary STS credentials
4. AgentCore client uses credentials to invoke agents
5. Credentials are checked back in after request

## ⚙️ Configuration Options

### Environment Variables

```bash
# AWS
AWS_REGION=us-west-2
AWS_ACCOUNT_ID=your-account-id

# Britive
BRITIVE_PROFILE=your-profile
BRITIVE_TENANT=your-tenant

# Agents (override config.py)
SUPERVISOR_AGENT_ID=your-supervisor-id
FRAUD_AGENT_ID=your-fraud-id
COMPLIANCE_AGENT_ID=your-compliance-id
RISK_AGENT_ID=your-risk-id

# Flask
PORT=5011
FLASK_DEBUG=true
```

## 🧪 Testing

### Test Financial Data Service

```bash
curl http://localhost:5011/api/financial-data?type=stock&symbol=AAPL
curl http://localhost:5011/api/financial-data?type=transactions
curl http://localhost:5011/api/financial-data?type=compliance
```

### Test Credentials

```bash
curl http://localhost:5011/api/test-credentials
```

### Test Analysis

```bash
curl -X POST http://localhost:5011/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Check SOX compliance status"}'
```

## 🐛 Troubleshooting

### "pybritive not found"

Install pybritive:
```bash
pip install pybritive
```

### "Failed to checkout AWS credentials"

1. Verify Britive profile name in config
2. Ensure pybritive is logged in: `pybritive login`
3. Check profile permissions

### "Agent not found"

1. Verify agent ARNs in config.py
2. Ensure agents are deployed and running
3. Check IAM permissions for invoking agents

### "yfinance not installed"

```bash
pip install yfinance
```

## 📝 Changelog

### v2.0.0 (Fixed)
- Fixed Britive client to properly parse and use credentials
- Fixed AgentCore client to use correct boto3 client
- Added credential verification
- Added comprehensive error handling
- Added health check and test endpoints
- Improved logging throughout

### v1.0.0 (Original)
- Initial implementation

## 📄 License

MIT License
