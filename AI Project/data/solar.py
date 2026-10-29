import numpy as np          # numpy is used for maths, whiles np is the nickname assigned to it in the project
import pandas as pd         # pandas is used for building tables, whiles pd is the nickname assigned to it in the project


# Function to generate solar energy data for benchmarking purposes
def generate_solar_data(days=30, start_date=None):

    # Total number of hours in the specified or selected number of days
    hours = days * 24

    # Use selected start date or default to 2026-01-01 and store in a variable called 'start'
    if start_date:
        start = pd.Timestamp(start_date)
    else:
        start = pd.Timestamp("2026-01-01")

    # Store the data from the start date with the number of hours in a variable called 'time_index'
    time_index = pd.date_range(start=start, periods=hours, freq="h")

    # Solar only generates during daylight hours (6am to 6pm)
    # 'hour_of_day' is a variable that stores the hour of the day for each timestamp in time_index
    hour_of_day = time_index.hour
    daylight = ((hour_of_day >= 6) & (hour_of_day <= 18)).astype(float)

    # 'solar_curve' is a variable that stores the solar output curve based on the hour of the day using the sine function. The output is scaled to a maximum of 1, and negative values are set to 0.
    solar_curve = np.maximum(0, np.sin((hour_of_day - 6) * np.pi / 12))

    # Add randomness to simulate cloud cover using 0.5 as heavy cloud and 1.0 as clear sky. The output is stored in a variable called 'weather_factor'
    weather_factor = np.random.uniform(0.5, 1.0, size=hours)

    # Ghana's maximum solar capacity is 186 MW
    # Multiply the solar curve(sun intensity), weather factor relating to cloud cover, and daylight to get the final output in Megawatts (mw) and store it in a variable called 'output_mw'
    output_mw = solar_curve * weather_factor * daylight * 186

    # Build a table with the timestamp, source, and output in Megawatts (mw) and store it in a variable called 'df'
    df = pd.DataFrame({
        "timestamp": time_index,
        "source": "Solar",
        "output_mw": output_mw
    })
    return df