# Kalshi Weather Bot - Probabilistic Temperature Forecasting System

A probabilistic temperature forecasting system for NYC that estimates the probability of daily high temperatures falling above, below, or within ranges corresponding to Kalshi weather markets. The system is designed to identify mispriced contracts before market uncertainty collapses.

## Features

- **Historical Data Integration**: Loads historical NYC temperature data from Open-Meteo Archive API
- **Probabilistic Forecasting**: Uses statistical models to estimate temperature distributions by day of year
- **Kalshi Market Integration**: Fetches and parses active weather market contracts
- **Mispricing Analysis**: Compares model probabilities with market prices to identify opportunities
- **Expected Value Calculation**: Computes expected value and Kelly criterion for optimal bet sizing

## System Architecture

### Core Components

1. **`data_loader.py`**: Loads historical daily high temperatures for NYC (Central Park)
2. **`nyc_temperature_model.py`**: Probabilistic temperature forecasting model using day-of-year statistics
3. **`kalshi_markets.py`**: Kalshi API integration and contract parsing
4. **`mispricing_analyzer.py`**: Analyzes contracts to identify mispricing opportunities
5. **`forecast_system.py`**: Main orchestration system that ties everything together

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from forecast_system import ForecastSystem

# Initialize the system
system = ForecastSystem()
system.initialize()

# Find mispricing opportunities
opportunities = system.find_opportunities(
    min_edge=0.05,      # Minimum 5% edge
    min_volume=0,       # No minimum volume requirement
    max_results=20      # Top 20 opportunities
)

print(opportunities)
```

### Generate Opportunity Report

```python
# Generate a human-readable report
report = system.generate_report(
    min_edge=0.03,
    min_volume=0,
    max_results=10
)
print(report)
```

### Get Forecast for Specific Date

```python
from datetime import date

# Get temperature forecast
forecast = system.get_forecast(date(2025, 12, 25))
print(f"Mean: {forecast['mean']:.1f}°F")
print(f"95% Range: {forecast['forecast_range_95'][0]:.1f}°F - {forecast['forecast_range_95'][1]:.1f}°F")
```

### Analyze Specific Contract

```python
# Analyze a specific market contract
analysis = system.analyze_specific_contract("KXHIGHNY-2025-12-25-50")
print(f"Model Probability: {analysis['model_probability']:.1%}")
print(f"Market Price: {analysis['market_price']:.1%}")
print(f"Edge: {analysis['edge']:.1%}")
```

### Run the Main Script

```bash
python forecast_system.py
```

## Model Details

The temperature model uses historical data to estimate:
- **Mean temperature** by day of year (using a rolling window)
- **Standard deviation** by day of year
- **Probability distributions** assuming normal distribution

The model calculates probabilities for:
- Temperature greater than a threshold
- Temperature less than a threshold
- Temperature within a range

## Mispricing Analysis

The system identifies opportunities by:
1. Calculating model probability for each contract outcome
2. Comparing with market-implied probability (market price)
3. Computing expected value: `EV = model_prob - market_price`
4. Calculating Kelly fraction for optimal bet sizing

## Example Output

```
================================================================================
KALSHI WEATHER MARKET OPPORTUNITIES
================================================================================

Found 5 opportunities with edge >= 0.05
Minimum volume: 0

--------------------------------------------------------------------------------

1. KXHIGHNY-2025-12-25-50
   Title: Will NYC high temp be >= 50°F on Dec 25?
   Date: 2025-12-25 | Temperature: 50.0°F
   Model Probability: 65.2%
   Market Price: 55.0%
   Edge: 10.2%
   Expected Value: 0.102
   Kelly Fraction: 18.5%
   Volume: 1234
```

## Configuration

You can customize the system by adjusting:

- **Historical data range**: Modify `historical_start` and `historical_end` in `ForecastSystem`
- **Model window**: Adjust `model_window` parameter (default: 7 days)
- **Minimum edge**: Set `min_edge` threshold for opportunities
- **Volume filter**: Set `min_volume` to filter low-liquidity contracts

## Notes

- The system uses the Kalshi public API (no authentication required for market data)
- Market prices are in cents and converted to decimal probabilities
- The model assumes temperature follows a normal distribution (may not hold for extreme events)
- Always verify contract details and market conditions before trading

## License

This project is for educational and research purposes.
