import sys
import os

# Path fix MUST come before any local imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data.data_manager import get_all_energy_data, get_summary
from data.real_data import get_real_energy_data, get_real_summary
from data.cost_data import COST_DATA
from agent.energy_agent import EnergyAgent
from benchmark.benchmark_runner import BenchmarkRunner

# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Energy System Dashboard",
    page_icon="⚡",
    layout="wide"
)

# ─────────────────────────────────────────────
# CUSTOM STYLING
# ─────────────────────────────────────────────
st.markdown("""
    <style>
        .main { background-color: #0e1117; }
        .block-container { padding-top: 1.5rem; }
        h1 { color: #00d4ff; font-size: 2rem; }
        h2 { color: #ffffff; }
        h3 { color: #aaaaaa; }
        .metric-box {
            background-color: #1e2130;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            margin: 5px;
        }
        .alert-box {
            background-color: #3d1a1a;
            border-left: 5px solid #ff4444;
            padding: 10px 15px;
            border-radius: 5px;
            color: #ff9999;
        }
        .success-box {
            background-color: #1a3d1a;
            border-left: 5px solid #44ff44;
            padding: 10px 15px;
            border-radius: 5px;
            color: #99ff99;
        }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("⚡ Agentic AI — Energy System Dashboard")
st.markdown("**Sources: Solar | Wind | Hydro** — Powered by Agentic AI")
st.divider()

# ─────────────────────────────────────────────
# SIDEBAR — CONTROLS
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/lightning-bolt.png", width=60)
    st.title("⚙️ Controls")
    st.markdown("---")

    st.markdown("### 📅 Select Date Range")

    # Default start and end dates
    default_start = pd.Timestamp.now().normalize() - pd.Timedelta(days=29)
    default_end = pd.Timestamp.now().normalize()

    start_date = st.date_input(
        "Start Date",
        value=default_start.date(),
        min_value=pd.Timestamp("2026-01-01").date(),
        max_value=default_end.date()
    )

    end_date = st.date_input(
        "End Date",
        value=default_end.date(),
        min_value=pd.Timestamp("2026-01-01").date(),
        max_value=(pd.Timestamp.now() + pd.Timedelta(days=16)).date()
    )

    # Validate date range
    if start_date >= end_date:
        st.error("⚠️ End date must be after start date.")
        end_date = default_end.date()

    # Calculate number of days from selected range
    days = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1

    st.caption(f"📊 Selected period: **{days} days**")

    selected_sources = st.multiselect(
        "🔍 Filter Energy Sources",
        options=["Solar", "Wind", "Hydro"],
        default=["Solar", "Wind", "Hydro"]
    )

    run_agent = st.button("🤖 Run AI Agent", use_container_width=True)

    st.markdown("---")
    st.markdown("### 🌍 Data Mode")
    data_mode = st.radio(
        "Select data source:",
        options=["🔬 Simulated Data", "🌐 Real Data (Ghana)"],
        index=0
    )
    use_real_data = data_mode == "🌐 Real Data (Ghana)"

    st.markdown("---")
    st.markdown("### 📘 About")
    st.markdown(
        "This dashboard models Solar, Wind, and Hydro energy systems "
        "using an Agentic AI that analyses data and makes decisions."
    )

# ─────────────────────────────────────────────
# LOAD DATA AND AGENT
# ─────────────────────────────────────────────
with st.spinner("Loading energy data..."):
    if use_real_data:
        if days > 16:
            st.warning(
                f"⚠️ Real Data mode is limited to 16 days by the API. "
                f"Showing data from {start_date} for 16 days. "
                f"Switch to Simulated mode for longer periods."
            )

        df, location_name = get_real_energy_data(
            start_date=start_date,
            end_date=end_date,
            days=days
        )
        summary, _ = get_real_summary(
            start_date=start_date,
            end_date=end_date,
            days=days
        )

        if df is None:
            st.warning("⚠️ Could not fetch real data. Switching to simulated data.")
            df = get_all_energy_data(days=days, start_date=start_date)
            summary = get_summary(days=days, start_date=start_date)
            location_name = "Simulated"
            use_real_data = False
        else:
            st.success(
                f"✅ Real data loaded for {location_name} "
                f"({start_date} to {end_date})"
            )
    else:
        df = get_all_energy_data(days=days, start_date=start_date)
        summary = get_summary(days=days, start_date=start_date)
        location_name = "Simulated"
        st.info(
            f"🔬 Simulated data loaded from "
            f"{start_date} to {end_date} ({days} days)"
        )

    agent = EnergyAgent(days=days, start_date=start_date)

# Filter by selected sources
df_filtered = df[df["source"].isin(selected_sources)]

# ─────────────────────────────────────────────
# SECTION 1 — SUMMARY METRICS
# ─────────────────────────────────────────────
st.subheader("📊 Summary Metrics")

col1, col2, col3 = st.columns(3)

source_colors = {"Solar": "🌞", "Wind": "💨", "Hydro": "💧"}

for col, source in zip([col1, col2, col3], ["Solar", "Wind", "Hydro"]):
    if source in summary.index:
        with col:
            icon = source_colors[source]
            total = summary.loc[source, "Total mw"]
            avg = summary.loc[source, "Avg mw/hr"]
            peak = summary.loc[source, "Peak mw"]
            st.metric(
                label=f"{icon} {source}",
                value=f"{total:,.0f} mw total",
                delta=f"Avg: {avg} mw/hr | Peak: {peak} mw"
            )

st.divider()

# ─────────────────────────────────────────────
# SECTION 2 — ENERGY OUTPUT CHART
# ─────────────────────────────────────────────
st.subheader("📈 Energy Output Over Time")

tab1, tab2, tab3 = st.tabs(["Line Chart", "Area Chart", "Bar Comparison"])

with tab1:
    fig_line = px.line(
        df_filtered,
        x="timestamp",
        y="output_mw",
        color="source",
        title="Hourly Energy Output — Solar, Wind, Hydro",
        labels={"output_mw": "Output (mw)", "timestamp": "Time"},
        color_discrete_map={
            "Solar": "#FFD700",
            "Wind": "#00BFFF",
            "Hydro": "#32CD32"
        }
    )
    fig_line.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="white",
        legend_title="Energy Source"
    )
    st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    fig_area = px.area(
        df_filtered,
        x="timestamp",
        y="output_mw",
        color="source",
        title="Cumulative Energy Output",
        labels={"output_mw": "Output (MW)", "timestamp": "Time"},
        color_discrete_map={
            "Solar": "#FFD700",
            "Wind": "#00BFFF",
            "Hydro": "#32CD32"
        }
    )
    fig_area.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="white"
    )
    st.plotly_chart(fig_area, use_container_width=True)

with tab3:
    fig_bar = px.bar(
        summary.reset_index(),
        x="source",
        y="Total mw",
        color="source",
        title="Total Output Comparison by Source",
        color_discrete_map={
            "Solar": "#FFD700",
            "Wind": "#00BFFF",
            "Hydro": "#32CD32"
        }
    )
    fig_bar.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# SECTION 3 — AI AGENT DECISION PANEL
# ─────────────────────────────────────────────
st.subheader("🤖 AI Agent Decision Panel")

if run_agent:
    with st.spinner("Agent is thinking..."):
        decision = agent.engine.get_current_best()
        mix = agent.engine.recommend_mix()
        risk = agent.engine.flag_risk()
        schedule = agent.engine.optimise_daily()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### ⚡ Current Recommendation")
        source = decision["recommended_source"]
        output = decision["output_mw"]
        icon = source_colors.get(source, "🔋")

        st.markdown(f"""
        <div class='metric-box'>
            <h2>{icon} {source}</h2>
            <p style='color:#aaa;'>Recommended Energy Source</p>
            <h3 style='color:#00d4ff;'>{output} mw</h3>
            <p style='color:#aaa;'>Current Output</p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("### 🔀 Suggested Energy Mix")
        for src, pct in mix.items():
            st.markdown(f"**{source_colors.get(src,'')} {src}**")
            st.progress(int(pct) / 100, text=f"{pct}%")

    st.divider()

    # ── Risk Assessment ──
    st.markdown("### ⚠️ Risk Assessment")
    if "No critical" in risk:
        st.markdown(
            f"<div class='success-box'>✅ {risk}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='alert-box'>🚨 {risk}</div>",
            unsafe_allow_html=True
        )

    st.divider()

    # ── Daily Schedule ──
    st.markdown("### 📅 Daily Optimisation Schedule")
    schedule_df = pd.DataFrame(
        list(schedule.items()),
        columns=["Hour", "Recommended Source"]
    )

    def color_source(val):
        colors = {"Solar": "#3d3500", "Wind": "#003040", "Hydro": "#003d00"}
        return f"background-color: {colors.get(val, '#1e2130')}; color: white;"

    styled = schedule_df.style.map(color_source, subset=["Recommended Source"])
    st.dataframe(styled, use_container_width=True, height=400)

else:
    st.info(
        "👈 Click **Run AI Agent** in the sidebar to see decisions, "
        "energy mix, risk alerts and daily schedule."
    )

st.divider()

# ─────────────────────────────────────────────
# SECTION 3B — COST ANALYSIS PANEL
# ─────────────────────────────────────────────
st.subheader("💰 Cost Analysis & Optimisation")

run_cost = st.button("💰 Run Cost Analysis", use_container_width=True)

if run_cost:
    with st.spinner("Analysing energy costs..."):
        cost_engine = agent.cost_engine
        cost_summary = cost_engine.get_cost_summary()
        cheapest, cheapest_cost = cost_engine.get_cheapest_source()
        efficient, efficiency = cost_engine.get_most_efficient_source()
        avg_cost, savings, grid_cost = cost_engine.get_savings_vs_grid()
        recommendations = cost_engine.get_cost_saving_recommendations()
        optimal_mix = cost_engine.get_optimal_cost_mix()

    # ── Cost Metric Cards ──
    st.markdown("### 💵 Cost Overview")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class='metric-box'>
            <h3>✅ Cheapest Source</h3>
            <h2 style='color:#00d4ff;'>{cheapest}</h2>
            <p style='color:#aaa;'>${cheapest_cost}/mwh</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class='metric-box'>
            <h3>⚡ Most Efficient</h3>
            <h2 style='color:#00d4ff;'>{efficient}</h2>
            <p style='color:#aaa;'>{efficiency} mw per $</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class='metric-box'>
            <h3>💵 Avg Renewable Cost</h3>
            <h2 style='color:#00d4ff;'>${avg_cost}/mwh</h2>
            <p style='color:#aaa;'>vs Ghana Grid $85/mwh</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Savings vs Grid ──
    st.markdown("### 💰 Savings vs Ghana Grid Price")
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        savings_color = "green" if savings > 0 else "red"
        savings_label = "saved" if savings > 0 else "more expensive"
        st.markdown(f"""
        <div class='metric-box'>
            <h3>Total Savings</h3>
            <h2 style='color:{savings_color};'>
                ${abs(savings):,.2f}
            </h2>
            <p style='color:#aaa;'>
                {savings_label} vs Ghana grid price
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_s2:
        st.markdown(f"""
        <div class='metric-box'>
            <h3>Grid Cost Would Be</h3>
            <h2 style='color:#ff9900;'>${grid_cost:,.2f}</h2>
            <p style='color:#aaa;'>
                At Ghana grid rate of $85/mwh
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Cost Summary Table ──
    st.markdown("### 📊 Cost Breakdown by Source")
    cost_display = cost_summary.copy()
    cost_display.columns = [
        "Total Output (mw)",
        "Total Cost ($)",
        "Avg Cost ($/mwh)",
        "Carbon (kg)",
        "mw per $"
    ]
    st.dataframe(cost_display, use_container_width=True)

    st.divider()

    # ── Cost per MWh Bar Chart ──
    st.markdown("### 📈 Cost per mwh by Source")
    cost_chart_data = {
        "Source": list(COST_DATA.keys()),
        "LCOE ($/mwh)": [v["lcoe"] for v in COST_DATA.values()],
        "O&M ($/mwh)": [v["om"] for v in COST_DATA.values()],
        "Carbon Cost ($/mwh)": [v["carbon_price"] for v in COST_DATA.values()]
    }
    cost_df = pd.DataFrame(cost_chart_data)

    fig_cost = px.bar(
        cost_df,
        x="Source",
        y=["LCOE ($/mwh)", "O&M ($/mwh)", "Carbon Cost ($/mwh)"],
        title="Cost Breakdown per mwh by Energy Source",
        barmode="stack",
        color_discrete_map={
            "LCOE ($/mwh)": "#00BFFF",
            "O&M ($/mwh)": "#FFD700",
            "Carbon Cost ($/mwh)": "#FF6B6B"
        }
    )
    fig_cost.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="white",
        legend_title="Cost Component"
    )
    st.plotly_chart(fig_cost, use_container_width=True)

    st.divider()

    # ── Optimal Cost Mix ──
    st.markdown("### 🔀 Cost-Optimised Energy Mix")
    st.caption(
        "This mix weights each source by output efficiency "
        "and cost — cheaper high-output sources get higher share."
    )
    for src, pct in optimal_mix.items():
        icon = {"Solar": "🌞", "Wind": "💨", "Hydro": "💧"}.get(src, "🔋")
        cost = COST_DATA[src]["total_cost"]
        st.markdown(f"**{icon} {src}** — ${cost}/MWh")
        st.progress(int(pct) / 100, text=f"{pct}%")

    st.divider()

    # ── Recommendations ──
    st.markdown("### 📋 Cost Saving Recommendations")
    for rec in recommendations:
        if "⚠️" in rec:
            st.markdown(
                f"<div class='alert-box'>{rec}</div>",
                unsafe_allow_html=True
            )
        elif "✅" in rec:
            st.markdown(
                f"<div class='success-box'>{rec}</div>",
                unsafe_allow_html=True
            )
        else:
            st.info(rec)

else:
    st.info(
        "👆 Click **Run Cost Analysis** to see cost breakdown, "
        "savings and optimisation recommendations."
    )

st.divider()

# ─────────────────────────────────────────────
# SECTION 4 — HOURLY HEATMAP
# ─────────────────────────────────────────────
st.subheader("🌡️ Hourly Output Heatmap")

df_heat = df_filtered.copy()
df_heat["hour"] = pd.to_datetime(df_heat["timestamp"]).dt.hour
df_heat["day"] = pd.to_datetime(df_heat["timestamp"]).dt.date

pivot = df_heat.groupby(["day", "hour"])["output_mw"].sum().reset_index()
pivot_table = pivot.pivot(index="day", columns="hour", values="output_mw")

fig_heat = go.Figure(data=go.Heatmap(
    z=pivot_table.values,
    x=[f"{h:02d}:00" for h in range(24)],
    y=[str(d) for d in pivot_table.index],
    colorscale="Viridis",
    colorbar=dict(title="MW")
))
fig_heat.update_layout(
    title="Total Energy Output by Hour and Day",
    xaxis_title="Hour of Day",
    yaxis_title="Date",
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font_color="white",
    height=500
)
st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# SECTION 5 — BENCHMARK EVALUATION
# ─────────────────────────────────────────────
st.subheader("🏆 Benchmark Evaluation")

run_benchmark = st.button("▶️ Run Full Benchmark", use_container_width=True)

if run_benchmark:
    with st.spinner("Running benchmark evaluation..."):
        runner = BenchmarkRunner(days=days, start_date=start_date)
        results = runner.run_all()

    # ── Score Cards ──
    st.markdown("### 📋 Benchmark Results")
    b1, b2, b3, b4 = st.columns(4)

    metric_list = [
        (b1, "🎯 Prediction Accuracy", "Prediction Accuracy"),
        (b2, "⚡ Decision Quality",    "Decision Quality"),
        (b3, "⚠️ Risk Detection",      "Risk Detection"),
        (b4, "📅 Optimisation",        "Optimisation Score"),
    ]

    for col, label, key in metric_list:
        with col:
            score = results.get(key, 0)
            color = "green" if score >= 75 else "orange" if score >= 50 else "red"
            st.markdown(f"""
            <div class='metric-box'>
                <h3>{label}</h3>
                <h2 style='color:{color};'>{score}%</h2>
            </div>
            """, unsafe_allow_html=True)

    # ── Overall Score ──
    overall = results.get("Overall Score", 0)
    grade = runner.scorer.get_grade(overall)
    color = "green" if overall >= 75 else "orange" if overall >= 50 else "red"

    st.markdown(f"""
    <div style='text-align:center; padding:20px; background:#1e2130;
                border-radius:10px; margin-top:15px;'>
        <h2>🏆 Overall Score:
            <span style='color:{color};'>{overall} / 100</span>
        </h2>
        <h3 style='color:#aaa;'>Grade: {grade}</h3>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Multi-Scenario Chart ──
    st.markdown("### 📈 Performance Across Different Time Periods")
    with st.spinner("Running multi-scenario analysis..."):
        multi_df = runner.run_multi_scenario(scenarios=[7, 14, 30, 60])

    fig_bench = px.line(
        multi_df.reset_index(),
        x="Days",
        y=["Prediction Accuracy", "Decision Quality",
           "Risk Detection", "Optimisation Score", "Overall Score"],
        title="Agent Performance vs Amount of Data Modelled",
        labels={"value": "Score (%)", "Days": "Days of Data"},
        markers=True
    )
    fig_bench.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="white",
        legend_title="Metric"
    )
    st.plotly_chart(fig_bench, use_container_width=True)

else:
    st.info(
        "👆 Click **Run Full Benchmark** to evaluate "
        "your AI agent's performance."
    )

st.divider()

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; color:#555; padding:20px;'>
    Agentic AI — Research Masters Project | Solar · Wind · Hydro
</div>
""", unsafe_allow_html=True)