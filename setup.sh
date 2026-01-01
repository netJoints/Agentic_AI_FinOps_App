#!/bin/bash
# ============================================
# setup.sh - Automated setup script
# ============================================

echo "🚀 Setting up FinOps AI Multi-Agent Application..."

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p finops_app/{services,routes,templates,static/{css,js}}

# Create __init__.py files
echo "📝 Creating __init__.py files..."
touch finops_app/__init__.py
touch finops_app/services/__init__.py
touch finops_app/routes/__init__.py

# Create placeholder files
echo "📄 Creating application files..."
touch finops_app/app.py
touch finops_app/config.py
touch finops_app/services/financial_data.py
touch finops_app/services/britive_client.py
touch finops_app/services/agentcore_client.py
touch finops_app/routes/api.py
touch finops_app/routes/views.py
touch finops_app/templates/index.html
touch finops_app/static/css/styles.css
touch finops_app/static/js/main.js
touch finops_app/requirements.txt
touch finops_app/.env.example
touch finops_app/README.md

echo "✅ Directory structure created!"

# Display tree structure
echo ""
echo "📂 Project structure:"
echo "finops_app/"
echo "├── app.py                      # Main Flask application"
echo "├── config.py                   # Configuration"
echo "├── requirements.txt            # Dependencies"
echo "├── .env.example                # Environment variables template"
echo "├── README.md                   # Documentation"
echo "├── services/"
echo "│   ├── __init__.py"
echo "│   ├── financial_data.py       # Financial data service"
echo "│   ├── britive_client.py       # Britive credential manager"
echo "│   └── agentcore_client.py     # AgentCore client"
echo "├── routes/"
echo "│   ├── __init__.py"
echo "│   ├── api.py                  # API endpoints"
echo "│   └── views.py                # Web views"
echo "├── templates/"
echo "│   └── index.html              # Main HTML template"
echo "└── static/"
echo "    ├── css/"
echo "    │   └── styles.css          # Styles"
echo "    └── js/"
echo "        └── main.js             # Frontend JavaScript"

echo ""
echo "📋 Next steps:"
echo "1. Copy the code from the artifacts into the respective files"
echo "2. Install dependencies: pip install -r requirements.txt"
echo "3. Configure your agents in config.py"
echo "4. Set up environment variables in .env"
echo "5. Run: python app.py"


# ============================================
# requirements.txt
# ============================================
cat > finops_app/requirements.txt << 'EOF'
flask>=2.3.0
flask-cors>=4.0.0
boto3>=1.28.0
yfinance>=0.2.28
requests>=2.31.0
bedrock-agentcore>=0.1.0
strands-agents>=0.1.0
python-dotenv>=1.0.0
EOF


# ============================================
# .env.example
# ============================================
cat > finops_app/.env.example << 'EOF'
# AWS Configuration
AWS_REGION=us-west-2

# Britive Configuration
BRITIVE_PROFILE=AWS SE Demo/Britive Agentic AI Solution/Admin
BRITIVE_TENANT=demo

# AgentCore Agent IDs (update after deployment)
SUPERVISOR_AGENT_ID=YOUR_SUPERVISOR_AGENT_ID
SUPERVISOR_ALIAS_ID=YOUR_SUPERVISOR_ALIAS_ID

FRAUD_AGENT_ID=YOUR_FRAUD_AGENT_ID
FRAUD_ALIAS_ID=YOUR_FRAUD_ALIAS_ID

COMPLIANCE_AGENT_ID=YOUR_COMPLIANCE_AGENT_ID
COMPLIANCE_ALIAS_ID=YOUR_COMPLIANCE_ALIAS_ID

RISK_AGENT_ID=YOUR_RISK_AGENT_ID
RISK_ALIAS_ID=YOUR_RISK_ALIAS_ID

# Optional API Keys
FINNHUB_API_KEY=demo
TWELVE_DATA_API_KEY=demo

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
EOF


# ============================================
# README.md
# ============================================
cat > finops_app/README.md << 'EOF'
# FinOps AI Multi-Agent System

Enterprise-grade financial analysis platform using AWS Bedrock AgentCore with real-time data.

## Features

- **Multi-Agent Architecture**: Fraud Detection, Compliance, Risk Analysis
- **Real-Time Data**: Yahoo Finance integration (free, unlimited)
- **Britive Security**: Dynamic credential management
- **AgentCore Runtime**: Serverless agent deployment

## Quick Start

### 1. Setup

```bash
# Run setup script
chmod +x setup.sh
./setup.sh

# Install dependencies
cd finops_app
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Deploy Agents

```bash
# Deploy each agent
cd agent_deployments/fraud_detection
agentcore configure -e fraud_agent.py --region us-west-2
agentcore launch

# Repeat for compliance and risk agents
```

### 3. Configure

Update `config.py` or `.env` with your agent IDs:
- FRAUD_AGENT_ID
- COMPLIANCE_AGENT_ID
- RISK_AGENT_ID

### 4. Run

```bash
python app.py
```

Visit: http://localhost:5001

## Architecture

```
User Query
    ↓
Flask API (/api/analyze)
    ↓
Britive Client (checkout credentials)
    ↓
AgentCore Client (orchestrate agents)
    ↓
├── Fraud Detection Agent
├── Compliance Agent
└── Risk Analysis Agent
    ↓
Aggregate Results → User
```

## Project Structure

- **app.py**: Main Flask application
- **config.py**: Configuration management
- **services/**: Business logic
  - `financial_data.py`: Real-time financial data
  - `britive_client.py`: Credential management
  - `agentcore_client.py`: Agent orchestration
- **routes/**: API and view routes
- **templates/**: HTML templates
- **static/**: CSS and JavaScript

## API Endpoints

### POST /api/analyze
Analyze query with AI agents
```json
{
  "query": "Analyze fraud risk",
  "session_id": "session-123"
}
```

### GET /api/financial-data
Get real-time financial data
```
?type=stock&symbol=AAPL
?type=transactions
?type=compliance
```

## Environment Variables

See `.env.example` for all configuration options.

## Debugging

Each module is separate for easy debugging:

1. **Financial Data Issues**: Check `services/financial_data.py`
2. **Britive Issues**: Check `services/britive_client.py`
3. **Agent Issues**: Check `services/agentcore_client.py`
4. **API Issues**: Check `routes/api.py`
5. **Frontend Issues**: Check `static/js/main.js`

## Common Issues

### Agents not configured
- Update agent IDs in `config.py`
- Ensure agents are deployed: `agentcore launch`

### Britive checkout fails
- Check profile name in config
- Verify pybritive is installed: `pip install pybritive`

### No financial data
- Install yfinance: `pip install yfinance`
- Check internet connection

## License

MIT
EOF


# ============================================
# Makefile for common tasks
# ============================================
cat > finops_app/Makefile << 'EOF'
.PHONY: help setup install run test clean

help:
	@echo "FinOps AI Multi-Agent System"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup      - Create directory structure"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run the application"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean cache files"

setup:
	@echo "📁 Creating directory structure..."
	@mkdir -p services routes templates static/css static/js
	@touch services/__init__.py routes/__init__.py

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

run:
	@echo "🚀 Starting application..."
	python app.py

test:
	@echo "🧪 Running tests..."
	python -m pytest tests/

clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
EOF


# ============================================
# File placement guide
# ============================================
cat > FILE_MAPPING.md << 'EOF'
# File Mapping Guide

Copy code from artifacts to these files:

## From "Modular FinOps App Structure" artifact:

### config.py
```python
# Copy the "config.py - Configuration" section
```

### services/__init__.py
```python
# Copy the "services/__init__.py" section
```

### services/financial_data.py
```python
# Copy the "services/financial_data.py" section
```

### services/britive_client.py
```python
# Copy the "services/britive_client.py" section
```

### services/agentcore_client.py
```python
# Copy the "services/agentcore_client.py" section
```

### routes/__init__.py
```python
# Copy the "routes/__init__.py" section
```

### routes/api.py
```python
# Copy the "routes/api.py" section
```

### routes/views.py
```python
# Copy the "routes/views.py" section
```

### app.py
```python
# Copy the "app.py - Main application" section
```

## From "Frontend Files" artifact:

### templates/index.html
```html
<!-- Copy the HTML section -->
```

### static/css/styles.css
```css
/* Copy the CSS section */
```

### static/js/main.js
```javascript
// Copy the JavaScript section
```

## Quick Copy Commands

```bash
# After creating files with setup.sh, use your editor to copy each section
# Or use this approach:

# 1. Copy each code block from the artifacts
# 2. Paste into the corresponding file
# 3. Save all files

# Verify structure
tree finops_app/

# Install and run
cd finops_app
pip install -r requirements.txt
python app.py
```
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Read FILE_MAPPING.md for instructions on copying code from artifacts"