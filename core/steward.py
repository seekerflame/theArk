import os
import time
import threading
import logging

logger = logging.getLogger("ArkOS.Steward")

class StewardNexus:
    def __init__(self, ledger, sensors, energy, btc_bridge, server_file='server.py'):
        self.ledger = ledger
        self.sensors = sensors
        self.energy = energy
        self.btc_bridge = btc_bridge
        self.server_file = server_file
        self.stop_event = threading.Event()
        self.last_audit = 0

    def audit_system(self):
        while not self.stop_event.is_set():
            now = time.time()
            if now - self.last_audit > 300: # Audit every 5 minutes
                self.perform_technical_audit()
                self.perform_metabolic_audit()
                self.perform_economic_audit()
                self.last_audit = now
            time.sleep(10)

    def perform_technical_audit(self):
        try:
            stats = os.stat(self.server_file)
            size_kb = stats.st_size / 1024
            if size_kb > 30:
                self.ledger.add_block('CHRONICLE', {
                    'event': 'TECH_DEBT_ALERT',
                    'message': f'System core density at {size_kb:.1f}KB. Modularization mission recommended.',
                    'source': 'STEWARD'
                })
        except: pass

    def perform_metabolic_audit(self):
        now = time.time()

        # Sensor Liveness
        for s_id, s in self.sensors.sensors.items():
            if now - s['last_seen'] > 300 and s['status'] == 'ONLINE':
                s['status'] = 'OFFLINE'
                self.ledger.add_block('CHRONICLE', {
                    'event': 'METABOLIC_FAULT',
                    'message': f'Sensor {s_id} ({s["type"]}) has flatlined. Dispatching repair proposal.',
                    'source': 'STEWARD'
                })
                self.ledger.add_block('QUEST', {
                    'quest_id': f'repair_{s_id}_{int(now)}',
                    'title': f'🔧 Repair Sensor {s_id}',
                    'reward': 25.0,
                    'owner': 'STEWARD',
                    'status': 'OPEN',
                    'created_at': now
                })
        self.sensors.save()

        # Energy / Hardware Optimization
        energy_state = self.energy.get_status()
        factor = self.energy.get_performance_factor()

        # If Overclocked, check if we have enough juice
        if factor > 1.0 and energy_state.get('node_contribution_percent', 0) < 0.0000001:
             # Just a heuristic: if we are overclocking but output is low (simulated)
             pass

    def perform_economic_audit(self):
        # Context: Energy Surplus vs BTC Rate
        energy_state = self.energy.get_status()
        btc_state = self.btc_bridge.get_exchange_rate()

        # Heuristic: High Battery + High BTC Rate = Sell Proposal
        # Since we don't have a real battery sensor in EnergyMonitor yet (it just has watts),
        # we check the sensors for 'SOLAR_GEN' or 'BATTERY'

        avg_battery = 0
        count = 0
        for s in self.sensors.sensors.values():
            if s.get('type') == 'SOLAR_GEN' and 'battery_soc' in s.get('last_value', {}):
                avg_battery += s['last_value']['battery_soc']
                count += 1

        if count > 0:
            avg_battery /= count
            if avg_battery > 95.0:
                # Propose Sell
                self.ledger.add_block('CHRONICLE', {
                    'event': 'ECONOMIC_OPPORTUNITY',
                    'message': f'Energy Surplus detected ({avg_battery:.1f}%). BTC Rate: {btc_state["rate"]}. Suggesting Lightning Channel Open.',
                    'source': 'STEWARD'
                })
            elif avg_battery < 20.0:
                 self.ledger.add_block('CHRONICLE', {
                    'event': 'ENERGY_CRITICAL',
                    'message': f'Energy Critical ({avg_battery:.1f}%). Suggesting reduced polling or grid-buy.',
                    'source': 'STEWARD'
                })

    def start(self):
        threading.Thread(target=self.audit_system, daemon=True).start()
