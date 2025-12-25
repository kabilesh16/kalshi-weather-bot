"""
Quick validation script to check if the system is ready to run.
"""
import sys

def check_imports():
    """Check if all required modules can be imported."""
    print("Checking imports...")
    try:
        import requests
        print("✓ requests")
    except ImportError as e:
        print(f"✗ requests: {e}")
        return False
    
    try:
        import pandas
        print("✓ pandas")
    except ImportError as e:
        print(f"✗ pandas: {e}")
        return False
    
    try:
        import numpy
        print("✓ numpy")
    except ImportError as e:
        print(f"✗ numpy: {e}")
        return False
    
    try:
        import scipy
        print("✓ scipy")
    except ImportError as e:
        print(f"✗ scipy: {e}")
        return False
    
    print("\nChecking project modules...")
    try:
        from data_loader import load_nyc_daily_highs
        print("✓ data_loader")
    except ImportError as e:
        print(f"✗ data_loader: {e}")
        return False
    
    try:
        from nyc_temperature_model import NYCTemperatureModel
        print("✓ nyc_temperature_model")
    except ImportError as e:
        print(f"✗ nyc_temperature_model: {e}")
        return False
    
    try:
        from kalshi_markets import KalshiMarketClient, MarketContractParser
        print("✓ kalshi_markets")
    except ImportError as e:
        print(f"✗ kalshi_markets: {e}")
        return False
    
    try:
        from mispricing_analyzer import MispricingAnalyzer
        print("✓ mispricing_analyzer")
    except ImportError as e:
        print(f"✗ mispricing_analyzer: {e}")
        return False
    
    try:
        from forecast_system import ForecastSystem
        print("✓ forecast_system")
    except ImportError as e:
        print(f"✗ forecast_system: {e}")
        return False
    
    return True

def check_syntax():
    """Check if Python files have valid syntax."""
    print("\nChecking syntax...")
    import py_compile
    import os
    
    files = [
        "data_loader.py",
        "nyc_temperature_model.py",
        "kalshi_markets.py",
        "mispricing_analyzer.py",
        "forecast_system.py",
    ]
    
    for file in files:
        try:
            py_compile.compile(file, doraise=True)
            print(f"✓ {file}")
        except py_compile.PyCompileError as e:
            print(f"✗ {file}: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("KALSHI WEATHER BOT - SETUP VALIDATION")
    print("=" * 60)
    print()
    
    syntax_ok = check_syntax()
    imports_ok = check_imports()
    
    print()
    print("=" * 60)
    if syntax_ok and imports_ok:
        print("✓ All checks passed! System is ready to run.")
        print("\nNext steps:")
        print("  1. Run: python example_usage.py")
        print("  2. Or: python forecast_system.py")
        sys.exit(0)
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        if not imports_ok:
            print("\nTo install dependencies, run:")
            print("  pip install -r requirements.txt")
        sys.exit(1)

