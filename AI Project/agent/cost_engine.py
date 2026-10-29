import pandas as pd
import numpy as np
from data.cost_data import COST_DATA, GHANA_GRID_PRICE_MWH, get_all_costs


class CostEngine:
    """
    Analyses and optimises energy costs across Solar, Wind and Hydro.
    Uses IRENA 2024 and Ghana Energy Commission cost figures.
    Provides cost-aware decision making for the EnergyAgent.
    """

    def __init__(self, data):
        self.data = data
        self.costs = get_all_costs()

    # ─────────────────────────────────────────
    # COST CALCULATION
    # ─────────────────────────────────────────
    def calculate_hourly_costs(self):
        """
        Calculates the cost of energy produced each hour
        for each source based on actual output and cost per MWh.
        Returns DataFrame with cost columns added.
        """
        df = self.data.copy()

        # Add cost per MWh for each source
        df["cost_per_mwh"] = df["source"].map({
            source: data["total_cost"]
            for source, data in self.costs.items()
        })

        # Add carbon emissions per hour
        df["carbon_kg"] = df["source"].map({
            source: data["carbon_kg_mwh"]
            for source, data in self.costs.items()
        }) * df["output_mw"]

        # Total cost for this hour = output * cost per MWh
        df["total_cost_usd"] = df["output_mw"] * df["cost_per_mwh"]

        return df

    # ─────────────────────────────────────────
    # COST SUMMARY
    # ─────────────────────────────────────────
    def get_cost_summary(self):
        """
        Returns total cost, average cost per MWh and
        total carbon emissions for each source.
        """
        df = self.calculate_hourly_costs()

        summary = df.groupby("source").agg(
            total_output_mw=("output_mw", "sum"),
            total_cost_usd=("total_cost_usd", "sum"),
            avg_cost_per_mwh=("cost_per_mwh", "mean"),
            total_carbon_kg=("carbon_kg", "sum")
        ).round(2)

        # Cost efficiency — output per dollar spent
        summary["mw_per_dollar"] = (
            summary["total_output_mw"] /
            summary["total_cost_usd"]
        ).round(4)

        return summary

    # ─────────────────────────────────────────
    # CHEAPEST SOURCE
    # ─────────────────────────────────────────
    def get_cheapest_source(self):
        """
        Returns the source with the lowest cost per MWh.
        This is the most economically efficient source.
        """
        cheapest = min(
            self.costs.items(),
            key=lambda x: x[1]["total_cost"]
        )
        return cheapest[0], cheapest[1]["total_cost"]

    # ─────────────────────────────────────────
    # MOST EFFICIENT SOURCE
    # ─────────────────────────────────────────
    def get_most_efficient_source(self):
        """
        Returns the source with the best output per dollar.
        Balances actual MW output against cost.
        """
        summary = self.get_cost_summary()
        if summary.empty:
            return "Unknown", 0
        best = summary["mw_per_dollar"].idxmax()
        efficiency = summary.loc[best, "mw_per_dollar"]
        return best, round(efficiency, 4)

    # ─────────────────────────────────────────
    # OPTIMAL COST MIX
    # ─────────────────────────────────────────
    def get_optimal_cost_mix(self, timestamp=None):
        """
        Recommends an energy mix that balances output
        and cost efficiency at a given timestamp.
        Cheaper sources get higher weighting.
        """
        df = self.data.copy()

        if timestamp:
            df = df[df["timestamp"] == timestamp]
        else:
            latest = df["timestamp"].max()
            df = df[df["timestamp"] == latest]

        if df.empty:
            return {}

        # Weight each source by output divided by cost
        weights = {}
        for _, row in df.iterrows():
            source = row["source"]
            output = row["output_mw"]
            cost = self.costs[source]["total_cost"]
            # Higher output and lower cost = higher weight
            weights[source] = output / cost if cost > 0 else 0

        total_weight = sum(weights.values())
        if total_weight == 0:
            return {s: 0 for s in weights}

        mix = {
            source: round((w / total_weight) * 100, 1)
            for source, w in weights.items()
        }
        return mix

    # ─────────────────────────────────────────
    # COST SAVING RECOMMENDATIONS
    # ─────────────────────────────────────────
    def get_cost_saving_recommendations(self):
        """
        Analyses the current energy mix and recommends
        specific actions to reduce cost.
        Returns a list of recommendations.
        """
        summary = self.get_cost_summary()
        recommendations = []

        # Check if expensive sources are being over-used
        for source, data in self.costs.items():
            if source not in summary.index:
                continue

            cost = data["total_cost"]
            output = summary.loc[source, "total_output_mw"]
            total_output = summary["total_output_mw"].sum()
            share = (output / total_output * 100) if total_output > 0 else 0

            if cost > 60 and share > 30:
                recommendations.append(
                    f"⚠️ {source} has a high cost of ${cost}/mwh "
                    f"but contributes {share:.1f}% of output. "
                    f"Consider reducing reliance on {source}."
                )
            elif cost < 40 and share < 20:
                recommendations.append(
                    f"✅ {source} is cost-efficient at ${cost}/mwh "
                    f"but only contributes {share:.1f}% of output. "
                    f"Consider increasing {source} utilisation."
                )

        # Carbon recommendation
        total_carbon = summary["total_carbon_kg"].sum()
        if total_carbon > 1000:
            recommendations.append(
                f"🌱 Total carbon emissions are {total_carbon:,.0f} kg. "
                f"Shifting more load to Solar or Wind would reduce this to zero."
            )

        if not recommendations:
            recommendations.append(
                "✅ Current energy mix is already cost-optimised "
                "for the selected period."
            )

        return recommendations

    # ─────────────────────────────────────────
    # SAVINGS VS GRID
    # ─────────────────────────────────────────
    def get_savings_vs_grid(self):
        """
        Compares your renewable energy cost against
        Ghana's average grid electricity price.
        Shows how much money renewables are saving.
        """
        summary = self.get_cost_summary()
        total_output = summary["total_output_mw"].sum()
        total_cost = summary["total_cost_usd"].sum()

        if total_output == 0:
            return 0, 0, 0

        avg_renewable_cost = total_cost / total_output
        grid_cost = total_output * GHANA_GRID_PRICE_MWH
        renewable_cost = total_cost
        savings = grid_cost - renewable_cost

        return round(avg_renewable_cost, 2), round(savings, 2), round(grid_cost, 2)

    # ─────────────────────────────────────────
    # FULL COST REPORT
    # ─────────────────────────────────────────
    def full_cost_report(self):
        """
        Prints a complete cost analysis report.
        """
        print("=" * 55)
        print("        ENERGY COST ANALYSIS REPORT")
        print("=" * 55)

        summary = self.get_cost_summary()
        print("\n💰 Cost Summary by Source:")
        print(summary.to_string())

        cheapest, cheapest_cost = self.get_cheapest_source()
        efficient, efficiency = self.get_most_efficient_source()

        print(f"\n✅ Cheapest Source     : {cheapest} (${cheapest_cost}/mwh)")
        print(f"⚡ Most Efficient Source: {efficient} ({efficiency} mw/$)")

        avg_cost, savings, grid_cost = self.get_savings_vs_grid()
        print(f"\n📊 Average Renewable Cost : ${avg_cost}/mwh)")