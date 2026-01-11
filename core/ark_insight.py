import time

class ArkAnalytics:
    """
    Ark Insight (Anti-Palantir).
    Processes node data locally to provide abundance insights.
    Goal: Feed 150 people for $0.
    """
    def __init__(self, ledger):
        self.ledger = ledger

    def get_abundance_metrics(self):
        """
        Calculates local autonomy levels.
        """
        # 1. Labor Hours (Total vs Burn)
        total_labor = 0
        for b in self.ledger.blocks:
            if b['type'] == 'LABOR':
                total_labor += b['data'].get('hours', 0)

        # 2. Migration Status
        liberated_count = 0
        for b in self.ledger.blocks:
            if b['type'] == 'EXODUS_GRANT':
                liberated_count += 1

        # 3. Autonomy Score (Local Production / External Need)
        # Mocking for now based on labor density
        autonomy_score = min(100, (total_labor / 1000) * 100) if total_labor > 0 else 0

        return {
            "autonomy_score": round(autonomy_score, 2),
            "liberated_citizens": liberated_count,
            "total_labor_hours": round(total_labor, 2),
            "stone_schedule_health": self._calculate_stone_health(),
            "timestamp": time.time()
        }

    def _calculate_stone_health(self):
        """Prioritizes Food, Shelter, and Power."""
        # This would analyze sensor data in a real setup
        return {
            "food": 65, # %
            "shelter": 40,
            "power": 85
        }

    def generate_recommendation(self):
        """Predictive optimization for the node."""
        metrics = self.get_abundance_metrics()
        if metrics['autonomy_score'] < 50:
            return "RECOMMENDATION: Increase Labor Minting for 'SHELTER' tasks. Current density is below survival threshold."
        return "RECOMMENDATION: Autonomous systems stable. Focus on 'EXODUS' waves to expand the federation."
