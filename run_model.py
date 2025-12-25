from datetime import date
from data_loader import load_nyc_daily_highs
from nyc_temperature_model import NYCTemperatureModel

# Load historical NYC temperature data via API
df = load_nyc_daily_highs(
    start_date="1995-01-01",
    end_date="2024-12-31"
)

# Train the model
model = NYCTemperatureModel.train(df, window=7)

# Example queries
query_date = date(2025, 12, 25)

print("P(T > 47):", round(model.prob_greater_than(47, query_date), 3))
print("P(T < 41):", round(model.prob_less_than(41, query_date), 3))
print("P(45 ≤ T < 46):", round(model.prob_range(45, 46, query_date), 3))
