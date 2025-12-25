"""
Example usage of the Kalshi Weather Forecasting System

This script demonstrates how to use the system to find mispricing opportunities.
"""
from datetime import date
from forecast_system import ForecastSystem


def main():
    print("Initializing Kalshi Weather Forecasting System...")
    print("=" * 80)
    
    # Initialize the system
    system = ForecastSystem(
        historical_start="1995-01-01",
        historical_end="2024-12-31",
        model_window=7
    )
    
    # Load data and train model
    system.initialize()
    
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Get Forecast for Specific Date")
    print("=" * 80)
    
    # Example: Get forecast for Christmas 2025
    target_date = date(2025, 12, 25)
    forecast = system.get_forecast(target_date)
    
    print(f"\nTemperature Forecast for {target_date}:")
    print(f"  Mean: {forecast['mean']:.1f}°F")
    print(f"  Standard Deviation: {forecast['std']:.1f}°F")
    print(f"  95% Confidence Interval: {forecast['forecast_range_95'][0]:.1f}°F - {forecast['forecast_range_95'][1]:.1f}°F")
    print(f"  80% Confidence Interval: {forecast['forecast_range_80'][0]:.1f}°F - {forecast['forecast_range_80'][1]:.1f}°F")
    
    # Show some probability examples
    print(f"\n  P(T > 50°F): {system.model.prob_greater_than(50, target_date):.1%}")
    print(f"  P(T < 40°F): {system.model.prob_less_than(40, target_date):.1%}")
    print(f"  P(45°F ≤ T < 55°F): {system.model.prob_range(45, 55, target_date):.1%}")
    
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Find Mispricing Opportunities")
    print("=" * 80)
    
    # Find opportunities with at least 3% edge
    print("\nSearching for opportunities with edge >= 3%...")
    opportunities = system.find_opportunities(
        min_edge=0.03,
        min_volume=0,
        max_results=10
    )
    
    if not opportunities.empty:
        print(f"\nFound {len(opportunities)} opportunities:")
        print("\n" + "-" * 80)
        for idx, row in opportunities.iterrows():
            print(f"\n{idx + 1}. {row['ticker']}")
            print(f"   {row['title']}")
            print(f"   Date: {row['date']} | Temp: {row['temperature']}°F")
            print(f"   Model Prob: {row['model_probability']:.1%} | Market Price: {row['market_price']:.1%}")
            print(f"   Edge: {row['edge']:.1%} | EV: {row['expected_value']:.3f}")
            if row['kelly_fraction']:
                print(f"   Kelly Fraction: {row['kelly_fraction']:.1%}")
            print(f"   Volume: {row['volume']}")
    else:
        print("\nNo opportunities found matching criteria.")
        print("This could mean:")
        print("  - No markets are currently open")
        print("  - Markets are efficiently priced")
        print("  - Try lowering min_edge threshold")
    
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Generate Opportunity Report")
    print("=" * 80)
    
    # Generate a formatted report
    report = system.generate_report(
        min_edge=0.02,  # Lower threshold for more results
        min_volume=0,
        max_results=5
    )
    print(report)


if __name__ == "__main__":
    main()

