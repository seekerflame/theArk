import threading
import time
import json
import logging
import os
from core.coinbase_client import CoinbaseClient
from core.strategy_engine import StrategyEngine, GridTrader
from core.risk_manager import RiskManager
from core.strategies.yield_farmer import YieldFarmer
from core.strategies.at_protector import ATProtector


logger = logging.getLogger("TreasuryBot")

class TreasuryBot(threading.Thread):
    def __init__(self, ledger, config_file='config/treasury_config.json'):
        super().__init__(daemon=True)
        self.ledger = ledger
        self.config_file = config_file
        self.config = self._load_config()
        
        # Initialize components
        self.client = CoinbaseClient(
            api_key=self.config.get('api_key'),
            api_secret=self.config.get('api_secret'),
            simulation=self.config.get('simulation', True)
        )
        self.risk = RiskManager(
            max_drawdown=self.config.get('max_drawdown', 0.1),
            max_exposure_per_asset=self.config.get('max_exposure', 0.2)
        )
        self.engine = StrategyEngine(self.client)
        self.engine.tick_interval = self.config.get('tick_interval', 60)

        
        # Load strategies based on config
        if self.config.get('enable_grid_trader', True):
            self.engine.add_strategy(GridTrader("GridTrader-Alpha", self.client))
        
        if self.config.get('enable_yield_farmer', True):
            self.engine.add_strategy(YieldFarmer(self.client))
            
        if self.config.get('enable_at_protector', True):
            self.engine.add_strategy(ATProtector(self.client))

            
        self.running = False

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                logger.error("Failed to load treasury config. Using defaults.")
        return {"simulation": True, "max_drawdown": 0.1, "max_exposure": 0.2, "enable_grid_trader": True}

    def run(self):
        self.running = True
        logger.info("The Sovereign Trader is ONLINE.")
        
        # Start the strategy engine
        # In a real setup, engine.run() might be blocking, so we handle it here or in its own thread
        self.engine.run()

    def get_status(self):
        return {
            "status": "ONLINE" if self.running else "OFFLINE",
            "simulation": self.client.simulation,
            "active_strategies": [s.name for s in self.engine.strategies],
            "accounts": self.client.get_accounts()
        }

    def stop(self):
        self.running = False
        self.engine.stop()
        logger.info("TreasuryBot shutting down.")
