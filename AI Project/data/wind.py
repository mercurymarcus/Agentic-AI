import numpy as np      # numpy is used for maths, whiles np is the nickname assigned to it in the project
import pandas as pd     # pandas is used for building tables, whiles pd is the nickname assigned to it in the project

# Function to generate wind energy data for benchmarking purposes
def generate_wind_data(days=30, start_date=None):

    # Total number of hours in the specified or selected number of days
    hours = days * 24

    # Use selected start date or default to 2026-01-01 and store in a variable called 'start'
    if start_date:
        start = pd.Timestamp(start_date)
    else:
        start = pd.Timestamp("2026-01-01")

    # Store the data from the start date with the number of hours in a variable called 'time_index'
    time_index = pd.date_range(start=start, periods=hours, freq="h")

    # Wind speed varies between 0 and 15 m/s
    # The Weibull distribution is commonly used to model wind speeds. Data is stored in a variable called 'wind_speed'
    # The shape parameter of 2 is typical for wind speed distributions, and the scale parameter of 8 gives a reasonable average wind speed in Ghana.
    wind_speed = np.random.weibull(2, size=hours) * 8

    # Power output proportional to cube of wind speed (standard wind formula)
    # Wind energy capacity at 100 MW which is projected for Ghana. The output is stored in a variable called 'output_mw'
    output_mw = np.minimum(wind_speed ** 3 * 0.5, 100)

    # Build a table with the timestamp, source, and output in Megawatts (mw) and store it in a variable called 'df'
    df = pd.DataFrame({
        "timestamp": time_index,
        "source": "Wind",
        "output_mw": output_mw
    })
    return df