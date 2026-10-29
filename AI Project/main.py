import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agent.energy_agent import EnergyAgent
from benchmark.benchmark_runner import BenchmarkRunner

print("=" * 55)
print("   AGENTIC AI — ENERGY SYSTEM MODELLING")
print("   Sources: Solar | Wind | Hydro")
print("=" * 55)

# ── STEP 1: Run the AI Agent ──
print("\n🤖 STARTING ENERGY AGENT...\n")
agent = EnergyAgent(days=30)
agent.full_run()

# ── STEP 2: Run the Benchmark ──
print("\n📊 STARTING BENCHMARK EVALUATION...\n")
runner = BenchmarkRunner(days=30)
runner.run_all()
runner.print_report()

# ── STEP 3: Multi-Scenario Benchmark ──
print("\n🔄 RUNNING MULTI-SCENARIO BENCHMARK...\n")
runner.run_multi_scenario(scenarios=[7, 14, 30, 60, 90])