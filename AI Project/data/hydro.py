import numpy as np      # numpy is used for maths, whiles np is the nickname assigned to it in the project
import pandas as pd     # pandas is used for building tables, whiles pd is the nickname assigned to it in the project

# Function to generate hydro energy data for benchmarking purposes
def generate_hydro_data(days=30, start_date=None):
    
    # Total number of hours in the specified or selected number of days
    hours = days * 24

    # Use selected start date or default to 2026-01-01 and store in a variable called 'start'
    if start_date:
        start = pd.Timestamp(start_date)
    else:
        start = pd.Timestamp("2026-01-01")

    # Store the data from the start date with the number of hours in a variable called 'time_index'
    time_index = pd.date_range(start=start, periods=hours, freq="h")

    # Creates an array of integers just to track the number of hours for the seasonal calculation
    day_index = np.arange(hours)

    # seasonal swing of the total hydro output we used was 25% so therefore 1580 MW * 0.25 = 395 MW
    seasonal = np.sin(day_index * 2 * np.pi / (365 * 24)) * 395

    # Total output of 1580 MW added to seasonal variation that was calculated earlier and stored in a variable called 'seasonal' to get the final output in Megawatts (mw) and store it in a variable called 'base_output'
    base_output = 1580 + seasonal

    # small random noise because realistically the output will not be exactly the same every hour, so we add some random noise to simulate that. The noise is normally distributed with a mean of 0 and a standard deviation of 50 MW. The output is stored in a variable called 'noise'
    noise = np.random.normal(0, 50, size=hours)

    # Final output is the base output plus the noise, but we also make sure that the output is not negative by using np.maximum to set a lower limit of 0 MW. The final output is stored in a variable called 'output_mw'
    output_mw = np.maximum(0, base_output + noise)

    # Build a table with the timestamp, source, and output in Megawatts (mw) and store it in a variable called 'df'
    df = pd.DataFrame({
        "timestamp": time_index,
        "source": "Hydro",
        "output_mw": output_mw
    })
    return df