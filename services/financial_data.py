# ============================================
# services/financial_data.py
# ============================================
"""
Financial data service - fetches real-time financial data from Yahoo Finance
and generates sample data for testing.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
import logging

logger = logging.getLogger(__name__)

# Try to import yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
    logger.info("✅ yfinance available")
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("⚠️ yfinance not installed. Run: pip install yfinance")


class FinancialDataService:
    """
    Service to fetch real financial data from free APIs (Yahoo Finance)
    and generate sample data for testing.
    """
    
    def __init__(self):
        self.yfinance_available = YFINANCE_AVAILABLE
    
    def get_stock_price(self, symbol: str = "AAPL") -> Dict:
        """
        Get real-time stock price using Yahoo Finance.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with price data or error
        """
        if not self.yfinance_available:
            return {"symbol": symbol, "price": 0, "error": "yfinance not installed"}
        
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="1d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                open_price = hist['Open'].iloc[-1]
                change = current_price - open_price
                change_percent = (change / open_price) * 100 if open_price != 0 else 0
                
                return {
                    "symbol": symbol,
                    "price": float(current_price),
                    "change": float(change),
                    "change_percent": f"{change_percent:+.2f}%",
                    "volume": int(hist['Volume'].iloc[-1]),
                    "timestamp": str(hist.index[-1]),
                    "market_cap": info.get('marketCap', 0),
                    "pe_ratio": info.get('trailingPE', 0)
                }
            
            return {"symbol": symbol, "price": 0, "error": "No data available"}
            
        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
            return {"symbol": symbol, "price": 0, "error": str(e)}
    
    def get_financial_ratios(self, symbol: str = "AAPL") -> Dict:
        """
        Get financial ratios using Yahoo Finance.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with financial ratios or error
        """
        if not self.yfinance_available:
            return {"symbol": symbol, "error": "yfinance not installed"}
        
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                "symbol": symbol,
                "current_ratio": info.get('currentRatio', 0),
                "quick_ratio": info.get('quickRatio', 0),
                "debt_to_equity": info.get('debtToEquity', 0),
                "roe": info.get('returnOnEquity', 0),
                "roa": info.get('returnOnAssets', 0),
                "profit_margin": info.get('profitMargins', 0),
                "operating_margin": info.get('operatingMargins', 0),
                "gross_margin": info.get('grossMargins', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "pb_ratio": info.get('priceToBook', 0),
                "beta": info.get('beta', 0),
                "52_week_high": info.get('fiftyTwoWeekHigh', 0),
                "52_week_low": info.get('fiftyTwoWeekLow', 0)
            }
            
        except Exception as e:
            logger.error(f"Error fetching ratios for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}
    
    def get_multiple_stocks(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """
        Get data for multiple stocks.
        
        Args:
            symbols: List of ticker symbols
            
        Returns:
            List of stock data dicts
        """
        if symbols is None:
            symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
        
        if not self.yfinance_available:
            return []
        
        stocks_data = []
        for symbol in symbols:
            data = self.get_stock_price(symbol)
            if "error" not in data:
                stocks_data.append(data)
        
        return stocks_data
    
    def generate_sample_transactions(self, count: int = 10) -> List[Dict]:
        """
        Generate realistic sample transactions for fraud detection testing.
        
        Args:
            count: Number of transactions to generate
            
        Returns:
            List of transaction dicts sorted by risk score (highest first)
        """
        transactions = []
        base_time = datetime.now()
        
        # Suspicious transaction patterns
        suspicious_patterns = [
            {
                "amount_range": (9000, 9999),
                "risk": 0.85,
                "reason": "Just below reporting threshold",
                "merchants": ["International Wire", "Crypto Exchange", "Unknown Merchant"]
            },
            {
                "amount_range": (500, 1000),
                "risk": 0.75,
                "reason": "Multiple small amounts (potential structuring)",
                "merchants": ["ATM Withdrawal", "Money Order", "Wire Transfer"]
            },
            {
                "amount_range": (10000, 50000),
                "risk": 0.90,
                "reason": "Unusually large amount",
                "merchants": ["International Wire", "Real Estate", "Luxury Goods"]
            },
            {
                "amount_range": (2000, 5000),
                "risk": 0.70,
                "reason": "Unusual merchant category",
                "merchants": ["Gambling Site", "Offshore Account", "Anonymous Payment"]
            },
        ]
        
        # Normal transaction patterns
        normal_merchants = [
            "Grocery Store", "Gas Station", "Restaurant", "Pharmacy",
            "Online Retailer", "Utility Company", "Insurance Premium"
        ]
        
        for i in range(count):
            is_suspicious = random.random() < 0.3  # 30% suspicious rate
            
            if is_suspicious:
                pattern = random.choice(suspicious_patterns)
                amount = random.uniform(*pattern["amount_range"])
                transaction = {
                    "transaction_id": f"TXN{1000 + i:04d}",
                    "amount": round(amount, 2),
                    "timestamp": (base_time - timedelta(hours=random.randint(0, 48))).isoformat(),
                    "merchant": random.choice(pattern["merchants"]),
                    "risk_score": round(pattern["risk"] + random.uniform(-0.05, 0.05), 2),
                    "flag": pattern["reason"],
                    "status": "FLAGGED"
                }
            else:
                transaction = {
                    "transaction_id": f"TXN{1000 + i:04d}",
                    "amount": round(random.uniform(10, 500), 2),
                    "timestamp": (base_time - timedelta(hours=random.randint(0, 48))).isoformat(),
                    "merchant": random.choice(normal_merchants),
                    "risk_score": round(random.uniform(0.1, 0.4), 2),
                    "flag": "Normal",
                    "status": "APPROVED"
                }
            
            transactions.append(transaction)
        
        # Sort by risk score (highest first)
        return sorted(transactions, key=lambda x: x["risk_score"], reverse=True)
    
    def get_compliance_data(self) -> Dict:
        """
        Generate sample compliance data for testing.
        
        Returns:
            Dict with compliance status for SOX, PCI-DSS, and AML
        """
        now = datetime.now()
        
        return {
            "sox_compliance": {
                "status": "Active",
                "last_audit": (now - timedelta(days=45)).strftime("%Y-%m-%d"),
                "next_audit": (now + timedelta(days=320)).strftime("%Y-%m-%d"),
                "controls_tested": 156,
                "controls_passed": 154,
                "controls_failed": 2,
                "compliance_score": 98.7,
                "deficiencies": [
                    {"severity": "LOW", "description": "Password policy not enforced for 3 accounts"},
                    {"severity": "MEDIUM", "description": "Segregation of duties gap in AP process"}
                ]
            },
            "pci_dss": {
                "status": "Compliant",
                "certification_date": (now - timedelta(days=90)).strftime("%Y-%m-%d"),
                "certification_expiry": (now + timedelta(days=180)).strftime("%Y-%m-%d"),
                "requirements_met": 12,
                "total_requirements": 12,
                "last_scan_date": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
                "vulnerabilities_found": 0
            },
            "aml_monitoring": {
                "status": "Active",
                "suspicious_activities": 3,
                "reports_filed": 1,
                "review_period": "Last 30 days",
                "alerts_generated": 47,
                "alerts_cleared": 44,
                "alerts_escalated": 3,
                "training_compliance": 98.5
            },
            "gdpr": {
                "status": "Compliant",
                "data_requests_received": 12,
                "data_requests_completed": 12,
                "average_response_time_days": 5.2,
                "breaches_reported": 0
            }
        }
    
    def get_market_summary(self) -> Dict:
        """
        Get a summary of market conditions.
        
        Returns:
            Dict with market summary data
        """
        indices = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow Jones, NASDAQ
        
        if not self.yfinance_available:
            return {"error": "yfinance not installed"}
        
        summary = {}
        for index in indices:
            try:
                ticker = yf.Ticker(index)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    open_price = hist['Open'].iloc[-1]
                    change_pct = ((current - open_price) / open_price) * 100 if open_price != 0 else 0
                    
                    name_map = {
                        "^GSPC": "S&P 500",
                        "^DJI": "Dow Jones",
                        "^IXIC": "NASDAQ"
                    }
                    
                    summary[name_map.get(index, index)] = {
                        "price": round(current, 2),
                        "change_percent": f"{change_pct:+.2f}%"
                    }
            except Exception as e:
                logger.error(f"Error fetching {index}: {e}")
        
        return summary
