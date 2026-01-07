"""
Financial Model Validator
Simulates Ark OS economics at various scales to prove 1.5% fee sustainability.
"""

def simulate_economics(users, avg_volume_per_user, fee_percent=0.015):
    """
    Run monthly simulation.
    
    Assumptions:
    - Hosting cost: $45k/year fixed (Phase 1)
    - Variable cost: $0.01 per user/mo (bandwidth/storage)
    - Legal Reserve: 10% of revenue
    - Treasury: 90% of revenue (surplus)
    """
    
    monthly_volume = users * avg_volume_per_user
    gross_revenue = monthly_volume * fee_percent
    
    # Costs
    fixed_hosting = 3750  # $45k / 12
    variable_cost = users * 0.01
    total_costs = fixed_hosting + variable_cost
    
    # Allocations
    legal_reserve = gross_revenue * 0.10
    net_surplus = gross_revenue - total_costs - legal_reserve
    
    return {
        "users": users,
        "volume": f"${monthly_volume:,.2f}",
        "gross_revenue": f"${gross_revenue:,.2f}",
        "costs": f"${total_costs:,.2f}",
        "legal_reserve": f"${legal_reserve:,.2f}",
        "surplus": f"${net_surplus:,.2f}",
        "sustainable": net_surplus > 0
    }

print("Ark OS Financial Viability Simulation (1.5% Fee)\n")

scenarios = [
    (100, 100),       # Alpha (Friends)
    (1000, 200),      # Beta (Village)
    (10000, 500),     # Launch (City) - Target for Year 1
    (100000, 1000),   # Growth (Region)
    (1000000, 1000)   # Scale (Nation)
]

for users, vol in scenarios:
    res = simulate_economics(users, vol)
    status = "✅" if res['sustainable'] else "❌"
    print(f"Scale: {users:,} users @ ${vol}/mo volume")
    print(f"  Revenue: {res['gross_revenue']} | Costs: {res['costs']}")
    print(f"  Surplus: {res['surplus']} {status}")
    print("-" * 40)
