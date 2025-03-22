import pandas as pd

# Load original CSV
df = pd.read_csv("cities.csv")  # replace with your actual filename

# Keep only the required columns
columns_to_keep = ["name", "state_name", "country_name", "latitude", "longitude"]
df_cleaned = df[columns_to_keep]

# Save to a new CSV
df_cleaned.to_csv("cleaned_locations.csv", index=False)

print("✅ Cleaned CSV saved as 'cleaned_locations.csv'")
