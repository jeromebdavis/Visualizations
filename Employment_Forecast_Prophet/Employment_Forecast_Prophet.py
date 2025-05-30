import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt 
import os
from datetime import datetime, timedelta

# Change directory
os.chdir('C:/Users/jerom/OneDrive/Courses/LinkedIn/Employment_Forecast_Prophet')

# Load your data
df = pd.read_csv('Employment.csv')

# Preview to check column names
print(df.head())

# Rename columns to match Prophet's expected format
# Prophet expects: 'ds' for date and 'y' for the value being forecasted
df.rename(columns={'date': 'ds', 'PAYEMS': 'y'}, inplace=True)

# Ensure 'ds' column is datetime format
df['ds'] = pd.to_datetime(df['ds'])

# Initialize and fit the Prophet model
model = Prophet()
model.fit(df)

# Create a dataframe for future dates
future = model.make_future_dataframe(periods=12, freq='M')  # forecast 12 months ahead

# Make predictions
forecast = model.predict(future)

# Plot and save the forecast
fig = model.plot(forecast)
plt.title("Employment Forecast")
plt.xlabel("Date")
plt.ylabel("Employment")
plt.grid(True)
fig.savefig(output_path, dpi=300)
plt.show()