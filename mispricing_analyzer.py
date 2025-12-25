"""
Mispricing Analysis Module

Compares model probabilities with market prices to identify mispriced contracts.
"""
from typing import List, Dict, Optional
from datetime import date, datetime
import pandas as pd
from nyc_temperature_model import NYCTemperatureModel


class MispricingAnalyzer:
    """
    Analyzes Kalshi contracts to identify mispriced opportunities.
    Compares model probabilities with market-implied probabilities.
    """
    
    def __init__(self, model: NYCTemperatureModel):
        """
        Initialize analyzer with a trained temperature model.
        
        Args:
            model: Trained NYCTemperatureModel instance
        """
        self.model = model
    
    def calculate_model_probability(self, contract: Dict) -> Optional[float]:
        """
        Calculate the model's probability for a contract outcome.
        
        Args:
            contract: Parsed contract dictionary from MarketContractParser
            
        Returns:
            Probability in [0, 1], or None if contract cannot be evaluated
        """
        if contract.get("date") is None:
            return None
        
        contract_type = contract.get("contract_type", "unknown")
        temperature = contract.get("temperature")
        
        if temperature is None:
            return None
        
        contract_date = contract["date"]
        if isinstance(contract_date, str):
            contract_date = datetime.strptime(contract_date, "%Y-%m-%d").date()
        
        try:
            if contract_type == "greater_than":
                # Contract pays if temp >= threshold
                return self.model.prob_greater_equal(temperature, contract_date)
            elif contract_type == "less_than":
                # Contract pays if temp <= threshold
                return self.model.prob_less_equal(temperature, contract_date)
            elif contract_type == "range":
                # For range contracts, would need to parse both bounds
                # For now, treat as single threshold
                return self.model.prob_greater_equal(temperature, contract_date)
            else:
                return None
        except Exception as e:
            print(f"Error calculating probability for {contract.get('ticker')}: {e}")
            return None
    
    def calculate_expected_value(self, contract: Dict, model_prob: float) -> Optional[float]:
        """
        Calculate expected value of a contract.
        
        Args:
            contract: Parsed contract dictionary
            model_prob: Model probability of "Yes" outcome
            market_price: Market price for "Yes" contract
            
        Returns:
            Expected value (positive = good opportunity)
        """
        market_price = contract.get("yes_mid")
        if market_price is None:
            return None
        
        # Expected value = (model_prob * 1.0) - market_price
        # If model says 60% chance but market prices at 50%, EV = 0.6 - 0.5 = 0.1
        return model_prob - market_price
    
    def calculate_kelly_fraction(self, contract: Dict, model_prob: float) -> Optional[float]:
        """
        Calculate Kelly criterion fraction for optimal bet sizing.
        
        Args:
            contract: Parsed contract dictionary
            model_prob: Model probability of "Yes" outcome
            
        Returns:
            Kelly fraction (0 to 1), or None if cannot calculate
        """
        market_price = contract.get("yes_mid")
        if market_price is None or market_price <= 0 or market_price >= 1:
            return None
        
        if model_prob <= 0 or model_prob >= 1:
            return None
        
        # Kelly fraction = (bp - q) / b
        # where b = odds (1/price - 1), p = win prob, q = lose prob
        odds = (1.0 / market_price) - 1.0
        kelly = (odds * model_prob - (1 - model_prob)) / odds
        
        # Only return positive Kelly (favorable bets)
        return max(0.0, kelly) if kelly > 0 else None
    
    def analyze_contract(self, contract: Dict) -> Dict:
        """
        Perform complete analysis on a single contract.
        
        Returns:
            Dictionary with analysis results
        """
        model_prob = self.calculate_model_probability(contract)
        
        if model_prob is None:
            return {
                "contract": contract,
                "model_probability": None,
                "market_price": contract.get("yes_mid"),
                "expected_value": None,
                "kelly_fraction": None,
                "edge": None,
                "analysis_status": "cannot_evaluate"
            }
        
        market_price = contract.get("yes_mid")
        expected_value = self.calculate_expected_value(contract, model_prob) if market_price else None
        kelly_fraction = self.calculate_kelly_fraction(contract, model_prob)
        edge = model_prob - market_price if market_price else None
        
        return {
            "contract": contract,
            "model_probability": model_prob,
            "market_price": market_price,
            "expected_value": expected_value,
            "kelly_fraction": kelly_fraction,
            "edge": edge,
            "analysis_status": "complete"
        }
    
    def analyze_contracts(self, contracts: List[Dict], 
                         min_edge: float = 0.05,
                         min_volume: int = 0) -> pd.DataFrame:
        """
        Analyze multiple contracts and return opportunities.
        
        Args:
            contracts: List of parsed contract dictionaries
            min_edge: Minimum edge (model_prob - market_price) to include
            min_volume: Minimum trading volume to include
            
        Returns:
            DataFrame with analysis results, sorted by expected value
        """
        results = []
        
        for contract in contracts:
            # Filter by volume if specified
            if contract.get("volume", 0) < min_volume:
                continue
            
            analysis = self.analyze_contract(contract)
            
            # Filter by edge if specified
            if analysis["edge"] is not None and analysis["edge"] >= min_edge:
                results.append(analysis)
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # Sort by expected value (descending)
        if "expected_value" in df.columns:
            df = df.sort_values("expected_value", ascending=False, na_last=True)
        
        return df
    
    def get_opportunities(self, contracts: List[Dict],
                         min_edge: float = 0.05,
                         min_volume: int = 0,
                         max_results: int = 20) -> List[Dict]:
        """
        Get top mispricing opportunities.
        
        Args:
            contracts: List of parsed contract dictionaries
            min_edge: Minimum edge required
            min_volume: Minimum volume required
            max_results: Maximum number of results to return
            
        Returns:
            List of opportunity dictionaries
        """
        df = self.analyze_contracts(contracts, min_edge=min_edge, min_volume=min_volume)
        
        if df.empty:
            return []
        
        opportunities = []
        for _, row in df.head(max_results).iterrows():
            opp = {
                "ticker": row["contract"]["ticker"],
                "title": row["contract"]["title"],
                "date": row["contract"]["date"],
                "temperature": row["contract"]["temperature"],
                "model_probability": row["model_probability"],
                "market_price": row["market_price"],
                "edge": row["edge"],
                "expected_value": row["expected_value"],
                "kelly_fraction": row["kelly_fraction"],
                "volume": row["contract"]["volume"],
                "contract_type": row["contract"]["contract_type"],
            }
            opportunities.append(opp)
        
        return opportunities

