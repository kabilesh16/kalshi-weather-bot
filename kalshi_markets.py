"""
Kalshi Market Integration Module

Fetches and parses Kalshi weather market contracts for NYC temperature markets.
"""
import requests
from datetime import datetime, date
import re
from typing import List, Dict, Optional, Tuple


class KalshiMarketClient:
    """Client for interacting with Kalshi API to fetch weather market data."""
    
    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_markets(self, series_ticker: str = "KXHIGHNY", status: str = "open") -> List[Dict]:
        """
        Fetch markets for a given series.
        
        Args:
            series_ticker: Series identifier (e.g., "KXHIGHNY" for NYC high temp)
            status: Market status filter ("open", "closed", "all")
            
        Returns:
            List of market dictionaries
        """
        url = f"{self.BASE_URL}/markets"
        params = {
            "series_ticker": series_ticker,
            "status": status
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("markets", [])
        except requests.RequestException as e:
            print(f"Error fetching markets: {e}")
            return []
    
    def get_market_details(self, market_ticker: str) -> Optional[Dict]:
        """Get detailed information for a specific market."""
        url = f"{self.BASE_URL}/markets/{market_ticker}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("market")
        except requests.RequestException as e:
            print(f"Error fetching market {market_ticker}: {e}")
            return None
    
    def get_event_details(self, event_ticker: str) -> Optional[Dict]:
        """Get event details for a given event ticker."""
        url = f"{self.BASE_URL}/events/{event_ticker}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("event")
        except requests.RequestException as e:
            print(f"Error fetching event {event_ticker}: {e}")
            return None


class MarketContractParser:
    """Parses Kalshi market contracts to extract temperature thresholds and dates."""
    
    @staticmethod
    def parse_temperature_threshold(title: str) -> Optional[float]:
        """
        Extract temperature threshold from market title.
        Handles patterns like "Will NYC high temp be >= 50°F on Dec 25?"
        
        Returns:
            Temperature in Fahrenheit, or None if not found
        """
        # Look for temperature patterns: "50°F", "50 F", ">= 50", etc.
        patterns = [
            r'([\d.]+)\s*°?\s*F',  # "50°F" or "50 F"
            r'[><=]+\s*([\d.]+)',  # ">= 50" or "< 50"
            r'([\d.]+)\s*degrees',  # "50 degrees"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def parse_date_from_title(title: str) -> Optional[date]:
        """
        Extract date from market title.
        Handles patterns like "Dec 25", "December 25, 2025", etc.
        
        Returns:
            date object or None
        """
        # Common date patterns
        patterns = [
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})(?:,\s*(\d{4}))?',
            r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?',
        ]
        
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                try:
                    if '/' in match.group(0):
                        # MM/DD/YYYY format
                        parts = match.group(0).split('/')
                        month = int(parts[0])
                        day = int(parts[1])
                        year = int(parts[2]) if len(parts) > 2 and parts[2] else datetime.now().year
                        if year < 100:
                            year += 2000
                        return date(year, month, day)
                    else:
                        # Month name format
                        month_name = match.group(1).lower()[:3]
                        month = month_map.get(month_name)
                        day = int(match.group(2))
                        year = int(match.group(3)) if match.group(3) else datetime.now().year
                        return date(year, month, day)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    @staticmethod
    def parse_contract_type(title: str) -> str:
        """
        Determine contract type from title.
        
        Returns:
            "greater_than", "less_than", "range", or "unknown"
        """
        title_lower = title.lower()
        
        if any(op in title_lower for op in ['>=', 'greater', 'above', 'over', 'exceed']):
            return "greater_than"
        elif any(op in title_lower for op in ['<=', 'less', 'below', 'under']):
            return "less_than"
        elif any(word in title_lower for word in ['between', 'range', 'within']):
            return "range"
        else:
            return "unknown"
    
    @staticmethod
    def parse_contract(market: Dict) -> Dict:
        """
        Parse a market contract to extract structured information.
        
        Returns:
            Dictionary with parsed contract details
        """
        title = market.get("title", "")
        ticker = market.get("ticker", "")
        
        contract = {
            "ticker": ticker,
            "title": title,
            "event_ticker": market.get("event_ticker", ""),
            "yes_bid": market.get("yes_bid", 0) / 100.0 if market.get("yes_bid") else None,  # Convert cents to decimal
            "yes_ask": market.get("yes_ask", 0) / 100.0 if market.get("yes_ask") else None,
            "no_bid": market.get("no_bid", 0) / 100.0 if market.get("no_bid") else None,
            "no_ask": market.get("no_ask", 0) / 100.0 if market.get("no_ask") else None,
            "volume": market.get("volume", 0),
            "open_time": market.get("open_time"),
            "close_time": market.get("close_time"),
            "status": market.get("status", "unknown"),
            "temperature": MarketContractParser.parse_temperature_threshold(title),
            "date": MarketContractParser.parse_date_from_title(title),
            "contract_type": MarketContractParser.parse_contract_type(title),
        }
        
        # Calculate mid price (average of bid and ask)
        if contract["yes_bid"] is not None and contract["yes_ask"] is not None:
            contract["yes_mid"] = (contract["yes_bid"] + contract["yes_ask"]) / 2.0
        elif contract["yes_bid"] is not None:
            contract["yes_mid"] = contract["yes_bid"]
        elif contract["yes_ask"] is not None:
            contract["yes_mid"] = contract["yes_ask"]
        else:
            contract["yes_mid"] = None
        
        return contract


def fetch_nyc_markets(status: str = "open") -> List[Dict]:
    """
    Convenience function to fetch and parse NYC temperature markets.
    
    Args:
        status: Market status filter
        
    Returns:
        List of parsed contract dictionaries
    """
    client = KalshiMarketClient()
    markets = client.get_markets(series_ticker="KXHIGHNY", status=status)
    
    parser = MarketContractParser()
    contracts = [parser.parse_contract(m) for m in markets]
    
    return contracts

