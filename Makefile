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
