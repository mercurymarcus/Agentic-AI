# Imports the EnergyAnalyzer class from the analyzer.py file inside the agent folder
from agent.analyzer import EnergyAnalyzer

# Imports the DecisionEngine class from the decision_engine.py file inside the agent folder
from agent.decision_engine import DecisionEngine

# Imports the CostEngine class from the cost_engine.py file inside the agent folder
from agent.cost_engine import CostEngine


# Class that represents the main AI Agent for Energy System Modelling. 
class EnergyAgent:
    

    def __init__(self, days=30, start_date=None):
        self.days = days
        self.start_date = start_date
        self.analyzer = EnergyAnalyzer(days=days, start_date=start_date)
        self.engine = DecisionEngine(days=days, start_date=start_date)
        self.cost_engine = CostEngine(self.engine.data)
        self.name = "Agentic AI"

    # Runs and prints the full energy analysis report.
    def run_analysis(self):
        
        self.analyzer.full_report()

    # Makes a real-time decision on the best energy source and prints recommendation and energy mix.
    def make_decision(self, timestamp=None):
        
        print("\n🤖 AGENT DECISION")
        print("-" * 40)
        decision = self.engine.get_current_best(timestamp)
        mix = self.engine.recommend_mix(timestamp)

        print(f"⚡ Recommended Source : {decision['recommended_source']}")
        print(f"📦 Output at this time: {decision['output_mw']} mw")

        print(f"\n🔀 Suggested Energy Mix:")
        for source, percent in mix.items():
            bar = "█" * int(percent / 5)
            print(f"   {source:<8}: {bar} {percent}%")

    
    # Runs and prints the full cost analysis report.
    def run_cost_analysis(self):
        
        self.cost_engine.full_cost_report()

    # Prints the optimised hourly schedule for the day, showing which source the agent recommends each hour.
    def daily_schedule(self):
        
        print("\n📅 DAILY OPTIMIZATION SCHEDULE")
        print("-" * 40)
        schedule = self.engine.optimise_daily()
        for time, source in schedule.items():
            print(f"  {time}  →  {source}")

    # Checks and reports any energy risk periods.
    def check_risks(self):
        
        print("\n⚠️  RISK ASSESSMENT")
        print("-" * 40)
        result = self.engine.flag_risk()
        print(result)

    # Runs the full agentic pipeline: analysis, cost, decision, schedule, and risk check.
    def full_run(self):
        
        print(f"\n{'='*50}")
        print(f"  {self.name} — FULL SYSTEM RUN")
        print(f"{'='*50}")

        self.run_analysis()
        self.run_cost_analysis()
        self.make_decision()
        self.daily_schedule()
        self.check_risks()
        
        print(f"\n{'='*50}")
        print("  AGENT RUN COMPLETE")
        print(f"{'='*50}")