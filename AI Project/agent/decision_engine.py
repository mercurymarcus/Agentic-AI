import pandas as pd     # pandas is used for building tables, whiles pd is the nickname assigned to it in the project

# Imports the 'get_all_energy_data' function from the data_manager.py file inside the data folder
from data.data_manager import get_all_energy_data

# Class that makes decisions about which energy source to prioritise. It acts as the reasoning core of the AI agent.
class DecisionEngine:

    # Initializes the DecisionEngine with a specified number of days and an optional start date. It retrieves energy data for analysis.
    def __init__(self, days=30, start_date=None):
        self.start_date = start_date
        self.data = get_all_energy_data(days=days, start_date=start_date)

    # Returns the energy source with the highest total output over the specified period
    def get_current_best(self, timestamp=None):
        
        df = self.data.copy()

        if timestamp:
            df = df[df["timestamp"] == timestamp]
        else:
            latest_time = df["timestamp"].max()
            df = df[df["timestamp"] == latest_time]

        if df.empty:
            return "No data available for that time."

        # Finds the row with the maximum output and returns the timestamp, recommended source, and output in megawatts
        best_row = df.loc[df["output_mw"].idxmax()]
        return {
            "timestamp": best_row["timestamp"],
            "recommended_source": best_row["source"],
            "output_mw": round(best_row["output_mw"], 2)
        }

    # Recommends a weighted energy mix based on current output levels. Returns percentage contribution from each source.
    def recommend_mix(self, timestamp=None):
        
        df = self.data.copy()

        if timestamp:
            df = df[df["timestamp"] == timestamp]
        else:
            latest_time = df["timestamp"].max()
            df = df[df["timestamp"] == latest_time]

        if df.empty:
            return "No data available."

        # Calculates the total output
        total = df["output_mw"].sum()
        if total == 0:
            return {"Solar": 0, "Wind": 0, "Hydro": 0}

        # Calculates the percentage contribution of each source to the total output and rounds it to 1 decimal place
        mix = {}
        for _, row in df.iterrows():
            mix[row["source"]] = round((row["output_mw"] / total) * 100, 1)

        return mix

    # Flags periods where total output falls below a specified threshold, indicating potential energy risk periods.
    def flag_risk(self, threshold=15):
        
        total_per_time = self.data.groupby("timestamp")["output_mw"].sum().reset_index()
        risks = total_per_time[total_per_time["output_mw"] < threshold]

        if risks.empty:
            return "✅ No critical risk periods detected."
        else:
            return f"🚨 {len(risks)} risk periods found where total output is < {threshold} mw"

    
    # Optimizes energy source showing which source is best to use at each hour of the day
    def optimise_daily(self):
        
        df = self.data.copy()
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour

        schedule = {}
        for hour in range(24):
            hour_data = df[df["hour"] == hour]
            best_source = hour_data.groupby("source")["output_mw"].mean().idxmax()
            schedule[f"{hour:02d}:00"] = best_source

        return schedule