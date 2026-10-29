# Imports the 'generate_solar_data' function from the solar.py file inside the data folder
from data.solar import generate_solar_data

# Imports the 'generate_wind_data' function from the wind.py file inside the data folder
from data.wind import generate_wind_data

# Imports the 'generate_hydro_data' function from the hydro.py file inside the data folder
from data.hydro import generate_hydro_data

import pandas as pd     # pandas is used for building tables, whiles pd is the nickname assigned to it in the project


# Function to combine all energy data into a single DataFrame
def get_all_energy_data(days=30, start_date=None):

    # Calling the generate_solar_data from solar.py and storing the output in a variable called 'solar'
    solar = generate_solar_data(days=days, start_date=start_date)

    # Calling the generate_wind_data from wind.py and storing the output in a variable called 'wind'
    wind = generate_wind_data(days=days, start_date=start_date)

    # Calling the generate_hydro_data from hydro.py and storing the output in a variable called 'hydro'
    hydro = generate_hydro_data(days=days, start_date=start_date)

    # Combining the solar, wind, and hydro DataFrames into a single DataFrame called 'combined'
    combined = pd.concat([solar, wind, hydro], ignore_index=True)

    # Sorting the combined DataFrame by timestamp and resetting the index to ensure a clean DataFrame
    combined = combined.sort_values("timestamp").reset_index(drop=True)

    return combined


# Function to get a summary of total output per energy source
def get_summary(days=30, start_date=None):

    # Calling the get_all_energy_data function to retrieve the combined energy data and storing it in a variable called 'df'
    df = get_all_energy_data(days=days, start_date=start_date)

    # Summary grouping and calculation of the total, mean, and maximum output
    summary = df.groupby("source")["output_mw"].agg(
        ["sum", "mean", "max"]
    ).round(2)  # Rounding the results to 2 decimal places

    # Renaming the columns of the summary DataFrame for better readability
    summary.columns = ["Total mw", "Avg mw/hr", "Peak mw"]
    return summary