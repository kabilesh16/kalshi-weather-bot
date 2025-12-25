from scipy.stats import norm
import numpy as np
from datetime import datetime, date
import pandas as pd


class NYCTemperatureModel:
    """
    Probabilistic temperature forecasting model for NYC daily high temperatures.
    Uses historical data to estimate mean and variance by day of year.
    """
    
    def __init__(self, mu_by_doy, sigma_by_doy, min_samples=30):
        self.mu_by_doy = mu_by_doy
        self.sigma_by_doy = sigma_by_doy
        self.min_samples = min_samples

    @classmethod
    def train(cls, df, window=7, min_samples=30):
        """
        Train the model on historical temperature data.
        
        Args:
            df: DataFrame with columns 'date' (datetime) and 'high_temp' (float)
            window: Days around each day-of-year to include in statistics
            min_samples: Minimum number of samples required for a day-of-year
            
        Returns:
            Trained NYCTemperatureModel instance
        """
        df = df.copy()
        df["doy"] = df["date"].dt.dayofyear

        mu_by_doy = {}
        sigma_by_doy = {}

        for doy in range(1, 367):
            # Handle year boundaries
            if doy - window < 1:
                mask = (
                    (df["doy"] >= 365 + doy - window) |
                    (df["doy"] <= doy + window)
                )
            elif doy + window > 366:
                mask = (
                    (df["doy"] >= doy - window) |
                    (df["doy"] <= doy + window - 365)
                )
            else:
                mask = (
                    (df["doy"] >= doy - window) &
                    (df["doy"] <= doy + window)
                )

            temps = df.loc[mask, "high_temp"].dropna()

            if len(temps) < min_samples:
                continue

            mu_by_doy[doy] = temps.mean()
            sigma_by_doy[doy] = temps.std(ddof=1)

        return cls(mu_by_doy, sigma_by_doy, min_samples)

    def _params_for_date(self, date_obj):
        """Get mean and standard deviation for a given date."""
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
        elif isinstance(date_obj, datetime):
            date_obj = date_obj.date()
            
        doy = date_obj.timetuple().tm_yday
        
        if doy not in self.mu_by_doy:
            # Find nearest available day
            for offset in range(1, 183):
                for test_doy in [doy - offset, doy + offset]:
                    if test_doy < 1:
                        test_doy += 365
                    elif test_doy > 365:
                        test_doy -= 365
                    if test_doy in self.mu_by_doy:
                        return self.mu_by_doy[test_doy], self.sigma_by_doy[test_doy]
            raise ValueError(f"No data available for date {date_obj}")
        
        return self.mu_by_doy[doy], self.sigma_by_doy[doy]

    def get_forecast(self, date_obj):
        """
        Get forecast parameters (mean, std) for a date.
        
        Returns:
            tuple: (mean, std) in Fahrenheit
        """
        return self._params_for_date(date_obj)

    def get_percentiles(self, date_obj, percentiles=[5, 10, 25, 50, 75, 90, 95]):
        """
        Get temperature percentiles for a date.
        
        Returns:
            dict: Mapping of percentile to temperature value
        """
        mu, sigma = self._params_for_date(date_obj)
        return {p: float(norm.ppf(p / 100, mu, sigma)) for p in percentiles}

    # -------- Probability API --------

    def prob_greater_than(self, x, date_obj):
        """
        Probability that temperature will be greater than x.
        
        Args:
            x: Temperature threshold (Fahrenheit)
            date_obj: Date object, datetime, or string (YYYY-MM-DD)
            
        Returns:
            float: Probability in [0, 1]
        """
        mu, sigma = self._params_for_date(date_obj)
        return float(1 - norm.cdf(x, mu, sigma))

    def prob_less_than(self, x, date_obj):
        """
        Probability that temperature will be less than x.
        
        Args:
            x: Temperature threshold (Fahrenheit)
            date_obj: Date object, datetime, or string (YYYY-MM-DD)
            
        Returns:
            float: Probability in [0, 1]
        """
        mu, sigma = self._params_for_date(date_obj)
        return float(norm.cdf(x, mu, sigma))

    def prob_greater_equal(self, x, date_obj):
        """Probability that temperature will be >= x."""
        return self.prob_greater_than(x - 0.01, date_obj)

    def prob_less_equal(self, x, date_obj):
        """Probability that temperature will be <= x."""
        return self.prob_less_than(x + 0.01, date_obj)

    def prob_range(self, low, high, date_obj, inclusive_low=True, inclusive_high=False):
        """
        Probability that temperature falls within a range.
        
        Args:
            low: Lower bound (Fahrenheit)
            high: Upper bound (Fahrenheit)
            date_obj: Date object, datetime, or string (YYYY-MM-DD)
            inclusive_low: Whether lower bound is inclusive
            inclusive_high: Whether upper bound is inclusive
            
        Returns:
            float: Probability in [0, 1]
        """
        mu, sigma = self._params_for_date(date_obj)
        
        if not inclusive_low:
            low = low + 0.01
        if inclusive_high:
            high = high + 0.01
            
        return float(norm.cdf(high, mu, sigma) - norm.cdf(low, mu, sigma))

    def prob_exactly(self, x, date_obj, tolerance=0.5):
        """
        Probability that temperature falls within tolerance of x.
        Useful for range contracts.
        
        Args:
            x: Target temperature
            date_obj: Date object, datetime, or string (YYYY-MM-DD)
            tolerance: Half-width of the range
            
        Returns:
            float: Probability in [0, 1]
        """
        return self.prob_range(x - tolerance, x + tolerance, date_obj, 
                              inclusive_low=True, inclusive_high=True)
