# ============================================
# services/financial_data.py
# ============================================
"""
Financial data service - fetches real-time financial data
"""
from datetime import datetime, timedelta
from typing import Dict, List
import random

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance not installed. Run: pip install yfinance")


class FinancialDataService:
    """Service to fetch real financial data from free APIs"""
    
    def __init__(self):
        self.yfinance_available = YFINANCE_AVAILABLE
    
    def get_stock_price(self, symbol: str = "AAPL") -> Dict:
        """Get real-time stock price using Yahoo Finance"""
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
                change_percent = (change / open_price) * 100
                
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
        except Exception as e:
            print(f"Error fetching stock price: {e}")
        
        return {"symbol": symbol, "price": 0, "error": "Unable to fetch data"}
    
    def get_financial_ratios(self, symbol: str = "AAPL") -> Dict:
        """Get financial ratios using Yahoo Finance"""
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
            print(f"Error fetching ratios: {e}")
        
        return {"symbol": symbol, "error": "Unable to fetch ratios"}
    
    def get_multiple_stocks(self, symbols: List[str] = None) -> List[Dict]:
        """Get data for multiple stocks"""
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
        """Generate realistic sample transactions for fraud detection"""
        transactions = []
        base_time = datetime.now()
        
        suspicious_patterns = [
            {"amount": random.uniform(9000, 9999), "risk": 0.85, "reason": "Just below reporting threshold"},
            {"amount": random.uniform(500, 1000), "risk": 0.75, "reason": "Multiple small amounts"},
            {"amount": random.uniform(10000, 50000), "risk": 0.90, "reason": "Unusually large amount"},
        ]
        
        for i in range(count):
            is_suspicious = random.random() < 0.3
            
            if is_suspicious:
                pattern = random.choice(suspicious_patterns)
                transaction = {
                    "transaction_id": f"TXN{1000 + i}",
                    "amount": round(pattern["amount"], 2),
                    "timestamp": (base_time - timedelta(hours=random.randint(0, 48))).isoformat(),
                    "merchant": random.choice(["Online Retailer", "International Wire", "Crypto Exchange", "Unknown Merchant"]),
                    "risk_score": pattern["risk"],
                    "flag": pattern["reason"]
                }
            else:
                transaction = {
                    "transaction_id": f"TXN{1000 + i}",
                    "amount": round(random.uniform(10, 500), 2),
                    "timestamp": (base_time - timedelta(hours=random.randint(0, 48))).isoformat(),
                    "merchant": random.choice(["Grocery Store", "Gas Station", "Restaurant", "Pharmacy"]),
                    "risk_score": round(random.uniform(0.1, 0.4), 2),
                    "flag": "Normal"
                }
            
            transactions.append(transaction)
        
        return sorted(transactions, key=lambda x: x["risk_score"], reverse=True)
    
    def get_compliance_data(self) -> Dict:
        """Generate sample compliance data"""
        return {
            "sox_compliance": {
                "status": "Active",
                "last_audit": (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
                "next_audit": (datetime.now() + timedelta(days=320)).strftime("%Y-%m-%d"),
                "controls_tested": 156,
                "controls_passed": 154,
                "compliance_score": 98.7
            },
            "pci_dss": {
                "status": "Compliant",
                "certification_expiry": (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d"),
                "requirements_met": 12,
                "total_requirements": 12
            },
            "aml_monitoring": {
                "status": "Active",
                "suspicious_activities": 3,
                "reports_filed": 1,
                "review_period": "Last 30 days"
            }
        }

