"""
Main Forecasting System

Orchestrates the complete probabilistic temperature forecasting system for Kalshi markets.
"""
from datetime import date, datetime
from typing import Dict
import pandas as pd
from data_loader import load_nyc_daily_highs
from nyc_temperature_model import NYCTemperatureModel
from kalshi_markets import fetch_nyc_markets, KalshiMarketClient, MarketContractParser
from mispricing_analyzer import MispricingAnalyzer


class ForecastSystem:
    """
    Complete probabilistic temperature forecasting system for NYC Kalshi markets.
    """
    
    def __init__(self, 
                 historical_start: str = "1995-01-01",
                 historical_end: str = "2024-12-31",
                 model_window: int = 7):
        """
        Initialize the forecasting system.
        
        Args:
            historical_start: Start date for historical data
            historical_end: End date for historical data
            model_window: Window size for day-of-year statistics
        """
        self.historical_start = historical_start
        self.historical_end = historical_end
        self.model_window = model_window
        self.model = None
        self.analyzer = None
        self._initialized = False
    
    def initialize(self, force_reload: bool = False):
        """
        Load data, train model, and initialize analyzer.
        
        Args:
            force_reload: If True, reload data even if model already exists
        """
        if self._initialized and not force_reload:
            return
        
        print("Loading historical temperature data...")
        df = load_nyc_daily_highs(
            start_date=self.historical_start,
            end_date=self.historical_end
        )
        print(f"Loaded {len(df)} days of historical data")
        
        print("Training temperature model...")
        self.model = NYCTemperatureModel.train(df, window=self.model_window)
        print("Model trained successfully")
        
        self.analyzer = MispricingAnalyzer(self.model)
        self._initialized = True
    
    def get_forecast(self, target_date):
        """
        Get temperature forecast for a specific date.
        
        Args:
            target_date: date object, datetime, or string (YYYY-MM-DD)
            
        Returns:
            Dictionary with forecast details
        """
        if not self._initialized:
            self.initialize()
        
        mu, sigma = self.model.get_forecast(target_date)
        percentiles = self.model.get_percentiles(target_date)
        
        return {
            "date": target_date,
            "mean": mu,
            "std": sigma,
            "percentiles": percentiles,
            "forecast_range_95": (percentiles[5], percentiles[95]),
            "forecast_range_80": (percentiles[10], percentiles[90]),
        }
    
    def find_opportunities(self,
                          min_edge: float = 0.05,
                          min_volume: int = 0,
                          max_results: int = 20,
                          market_status: str = "open") -> pd.DataFrame:
        """
        Find mispriced contract opportunities.
        
        Args:
            min_edge: Minimum edge (model_prob - market_price) required
            min_volume: Minimum trading volume required
            max_results: Maximum number of opportunities to return
            market_status: Market status filter ("open", "closed", "all")
            
        Returns:
            DataFrame with opportunities sorted by expected value
        """
        if not self._initialized:
            self.initialize()
        
        print(f"Fetching {market_status} Kalshi markets...")
        contracts = fetch_nyc_markets(status=market_status)
        print(f"Found {len(contracts)} contracts")
        
        if not contracts:
            print("No contracts found")
            return pd.DataFrame()
        
        print("Analyzing contracts for mispricing opportunities...")
        opportunities = self.analyzer.get_opportunities(
            contracts,
            min_edge=min_edge,
            min_volume=min_volume,
            max_results=max_results
        )
        
        if not opportunities:
            print("No opportunities found matching criteria")
            return pd.DataFrame()
        
        df = pd.DataFrame(opportunities)
        return df
    
    def analyze_specific_contract(self, market_ticker: str) -> Dict:
        """
        Analyze a specific contract by ticker.
        
        Args:
            market_ticker: Kalshi market ticker (e.g., "KXHIGHNY-2025-12-25-50")
            
        Returns:
            Dictionary with detailed analysis
        """
        if not self._initialized:
            self.initialize()
        
        client = KalshiMarketClient()
        market = client.get_market_details(market_ticker)
        
        if not market:
            return {"error": f"Market {market_ticker} not found"}
        
        parser = MarketContractParser()
        contract = parser.parse_contract(market)
        
        analysis = self.analyzer.analyze_contract(contract)
        
        # Add forecast details
        if contract.get("date"):
            forecast = self.get_forecast(contract["date"])
            analysis["forecast"] = forecast
        
        return analysis
    
    def generate_report(self,
                       min_edge: float = 0.05,
                       min_volume: int = 0,
                       max_results: int = 20) -> str:
        """
        Generate a human-readable report of opportunities.
        
        Returns:
            String report
        """
        df = self.find_opportunities(
            min_edge=min_edge,
            min_volume=min_volume,
            max_results=max_results
        )
        
        if df.empty:
            return "No opportunities found matching criteria."
        
        report_lines = [
            "=" * 80,
            "KALSHI WEATHER MARKET OPPORTUNITIES",
            "=" * 80,
            f"\nFound {len(df)} opportunities with edge >= {min_edge}",
            f"Minimum volume: {min_volume}\n",
            "-" * 80,
        ]
        
        for idx, row in df.iterrows():
            report_lines.extend([
                f"\n{idx + 1}. {row['ticker']}",
                f"   Title: {row['title']}",
                f"   Date: {row['date']} | Temperature: {row['temperature']}°F",
                f"   Model Probability: {row['model_probability']:.1%}",
                f"   Market Price: {row['market_price']:.1%}",
                f"   Edge: {row['edge']:.1%}",
                f"   Expected Value: {row['expected_value']:.3f}",
                f"   Kelly Fraction: {row['kelly_fraction']:.1%}" if row['kelly_fraction'] else "   Kelly Fraction: N/A",
                f"   Volume: {row['volume']}",
            ])
        
        report_lines.append("\n" + "=" * 80)
        
        return "\n".join(report_lines)


def main():
    """Example usage of the forecasting system."""
    system = ForecastSystem()
    system.initialize()
    
    # Generate opportunity report
    print("\n" + system.generate_report(min_edge=0.03, min_volume=0, max_results=10))
    
    # Example: Get forecast for a specific date
    print("\n" + "=" * 80)
    print("FORECAST EXAMPLE")
    print("=" * 80)
    forecast = system.get_forecast(date(2025, 12, 25))
    print(f"\nDate: {forecast['date']}")
    print(f"Mean: {forecast['mean']:.1f}°F")
    print(f"Std: {forecast['std']:.1f}°F")
    print(f"95% Range: {forecast['forecast_range_95'][0]:.1f}°F - {forecast['forecast_range_95'][1]:.1f}°F")
    print(f"80% Range: {forecast['forecast_range_80'][0]:.1f}°F - {forecast['forecast_range_80'][1]:.1f}°F")


if __name__ == "__main__":
    main()

