import pandas as pd     # pandas is used for building tables, whiles pd is the nickname assigned to it in the project
import numpy as np      # numpy is used for maths, whiles np is the nickname assigned to it in the project

# Imports the 'get_all_energy_data' and 'get_summary' functions from the data_manager.py file inside the data folder
from data.data_manager import get_all_energy_data, get_summary


# Class that analyzes energy output data for Solar, Wind, and Hydro sources. It produces insights that the AI agent uses to make decisions.
class EnergyAnalyzer:

    def __init__(self, days=30, start_date=None):

        # Saves the number of days inside the object 'self' and can be accessed through the variable name 'self.days'
        self.days = days
        # Saves the start date inside the object 'self' and can be accessed through the variable name 'self.start_date'
        self.start_date = start_date
        # Retrieves all energy data for the specified number of days and start date, and saves it inside the object 'self' and can be accessed through the variable name 'self.data'
        self.data = get_all_energy_data(days=days, start_date=start_date)
        # Retrieves a summary of the energy data for the specified number of days and start date, and saves it inside the object 'self' and can be accessed through the variable name 'self.summary'
        self.summary = get_summary(days=days, start_date=start_date)

    # Returns the energy source with the highest total output.
    def get_best_source(self):
        
        best = self.summary["Total mw"].idxmax()
        return best

    # Returns the energy source with the lowest total output.
    def get_worst_source(self):
        
        worst = self.summary["Total mw"].idxmin()
        return worst

    # For spotting peak times, this method returns the average output per hour for each energy source.
    def get_hourly_breakdown(self):

        # Making a copy of the data to avoid modifying the original DataFrame
        df = self.data.copy()

        # Creates a column called 'hour' to receive just the hour number from the timestamp column.
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour

        # Groups the data by hour and source, calculates the mean output for each group, and reshapes the DataFrame so that each source has its own column.
        breakdown = df.groupby(["hour", "source"])["output_mw"].mean().unstack()
        return breakdown

    # Detects periods where the total output from all sources is below a specified threshold, indicating potential energy risk periods.
    def detect_low_output_periods(self, threshold=20):

        # Making a copy of the data to avoid modifying the original DataFrame
        df = self.data.copy()

        # Creates a column called 'hour' to receive just the hour number from the timestamp column.
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour

        # Groups the data by timestamp and sums the output from all sources for each timestamp, then resets the index to make 'timestamp' a column again.
        total_per_hour = df.groupby("timestamp")["output_mw"].sum().reset_index()

        # Filters the DataFrame to find periods where the total output is below the specified threshold.
        low_periods = total_per_hour[total_per_hour["output_mw"] < threshold]
        return low_periods

    # Checks how related the 3 sources are to each other. Low correlation means they complement each other well.
    def get_correlation(self):

        # Creates a pivot table with timestamps as rows, sources as columns, and output values as the data. Then calculates the correlation matrix for the sources and rounds the results to 3 decimal places.
        pivot = self.data.pivot_table(
            index="timestamp", columns="source", values="output_mw"
        )
        return pivot.corr().round(3)


    # Prints a complete analysis report.
    def full_report(self):
        
        print("=" * 50)
        print("       ENERGY SYSTEM ANALYSIS REPORT")
        print("=" * 50)

        print("\n📊 Summary by Source:")
        print(self.summary)

        print(f"\n✅ Best Performing Source: {self.get_best_source()}")
        print(f"⚠️  Weakest Source: {self.get_worst_source()}")

        print("\n🔗 Correlation Between Sources:")
        print(self.get_correlation())
        low = self.detect_low_output_periods()
        
        print(f"\n🚨 Low Output Periods Detected: {len(low)} hours below threshold")
        print("=" * 50)