# ─────────────────────────────────────────────
# GHANA ENERGY COST DATA
# Based on IRENA 2024 and Ghana Energy Commission figures
# All costs in USD per MWh
# ─────────────────────────────────────────────

COST_DATA = {
    "Solar": {
        "lcoe":          45.00,   # Levelised Cost of Energy ($/MWh)
        "om":             8.00,   # Operations & Maintenance ($/MWh)
        "carbon_kg_mwh":  0.00,   # Carbon emissions (kg CO2 per MWh)
        "carbon_price":   0.00,   # Carbon cost at $15/tonne ($/MWh)
        "total_cost":    53.00,   # Total cost per MWh
        "capacity_mw":  186.00,   # Maximum capacity (MW)
        "source":       "IRENA West Africa Solar Report 2024"
    },
    "Wind": {
        "lcoe":          60.00,
        "om":            12.00,
        "carbon_kg_mwh":  0.00,
        "carbon_price":   0.00,
        "total_cost":    72.00,
        "capacity_mw":  100.00,
        "source":       "IRENA West Africa Wind Report 2024"
    },
    "Hydro": {
        "lcoe":          30.00,
        "om":             5.00,
        "carbon_kg_mwh":  4.00,   # Small methane emissions from reservoir
        "carbon_price":   0.06,   # 4kg * $15/tonne = $0.06/MWh
        "total_cost":    35.06,
        "capacity_mw": 1580.00,   # Akosombo Dam capacity
        "source":       "Ghana Energy Commission 2024"
    }
}

# Carbon price assumption
CARBON_PRICE_PER_TONNE = 15.00  # USD per tonne CO2

# Ghana grid electricity price for comparison
GHANA_GRID_PRICE_MWH = 85.00  # USD per MWh (Ghana grid average)

def get_cost(source):
    """Returns full cost data for a given source."""
    return COST_DATA.get(source, {})

def get_total_cost_per_mwh(source):
    """Returns total cost per MWh for a given source."""
    return COST_DATA.get(source, {}).get("total_cost", 0)

def get_all_costs():
    """Returns the full cost dictionary."""
    return COST_DATA