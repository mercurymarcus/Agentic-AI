import pandas as pd
from data.data_manager import get_all_energy_data
from agent.energy_agent import EnergyAgent
from benchmark.scoring import BenchmarkScorer


# Class that runs the full benchmark evaluation on the EnergyAgent.
class BenchmarkRunner:
    
    def __init__(self, days=30, start_date=None):
        self.days = days
        self.start_date = start_date
        self.data = get_all_energy_data(days=days, start_date=start_date)
        self.agent = EnergyAgent(days=days, start_date=start_date)
        self.scorer = BenchmarkScorer(self.data, self.agent)
        self.results = {}

    def run_all(self):
        
        print("\n" + "=" * 55)
        print("     BENCHMARK EVALUATION — AGENTIC AI")
        print("=" * 55)
        print(f"  Sources : Solar | Wind | Hydro")
        print(f"  Period  : {self.days} days of modelled data")
        if self.start_date:
            print(f"  From    : {self.start_date}")
        print("=" * 55)

        print("\n⏳ Running benchmarks...\n")

        acc   = self.scorer.score_prediction_accuracy()
        qual  = self.scorer.score_decision_quality()
        risk  = self.scorer.score_risk_detection()
        optim = self.scorer.score_optimisation()
        total = self.scorer.overall_score()

        self.results = {
            "Prediction Accuracy": acc,
            "Decision Quality":    qual,
            "Risk Detection":      risk,
            "Optimisation Score":  optim,
            "Overall Score":       total
        }

        return self.results

    def print_report(self):
        """
        Prints a formatted benchmark report to the terminal.
        """
        if not self.results:
            self.run_all()

        print("\n📋 BENCHMARK RESULTS")
        print("-" * 55)

        metrics = [
            ("Prediction Accuracy", "🎯", 0.30),
            ("Decision Quality",    "⚡", 0.30),
            ("Risk Detection",      "⚠️ ", 0.20),
            ("Optimisation Score",  "📅", 0.20),
        ]

        for name, icon, weight in metrics:
            score = self.results.get(name, 0)
            bar_len = int(score / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(
                f"  {icon} {name:<22} [{bar}] "
                f"{score:>6.1f}%  (weight: {int(weight*100)}%)"
            )

        print("-" * 55)
        overall = self.results.get("Overall Score", 0)
        grade = self.scorer.get_grade(overall)
        print(f"\n  🏆 OVERALL SCORE : {overall:.1f} / 100")
        print(f"  📝 GRADE         : {grade}")
        print("\n" + "=" * 55)

    def run_multi_scenario(self, scenarios=[7, 30, 60, 90]):
        
        print("\n🔄 Running Multi-Scenario Benchmark...")
        print(f"   Testing over: {scenarios} days\n")

        records = []
        for days in scenarios:
            runner = BenchmarkRunner(
                days=days,
                start_date=self.start_date
            )
            results = runner.run_all()
            results["Days"] = days
            records.append(results)
            print(f"   ✅ {days}-day scenario complete")

        df = pd.DataFrame(records).set_index("Days")
        print("\n📊 MULTI-SCENARIO RESULTS")
        print("-" * 55)
        print(df.to_string())
        print("-" * 55)
        return df