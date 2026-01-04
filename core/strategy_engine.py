import time
import logging

logger = logging.getLogger("StrategyEngine")

class BaseStrategy:
    """
    Base Strategy interface. All trading strategies must inherit from this.
    """
    def __init__(self, name, client, params=None):
        self.name = name
        self.client = client
        self.params = params or {}
        self.active = False

    def on_tick(self):
        """Called on every engine tick (e.g., every 60s)"""
        if not self.active:
            return
        self.execute()

    def execute(self):
        """Logic to check conditions and place trades"""
        raise NotImplementedError

    def start(self):
        self.active = True
        logger.info(f"Strategy {self.name} STARTED.")

    def stop(self):
        self.active = False
        logger.info(f"Strategy {self.name} STOPPED.")

class StrategyEngine:
    """
    Orchestrates multiple strategies and the main trading loop.
    """
    def __init__(self, client):
        self.client = client
        self.strategies = []
        self.running = False
        self.tick_interval = 60 # Default 1 minute

    def add_strategy(self, strategy):
        self.strategies.append(strategy)
        logger.info(f"Added strategy: {strategy.name}")

    def run(self):
        self.running = True
        logger.info("StrategyEngine main loop STARTING.")
        while self.running:
            try:
                for strategy in self.strategies:
                    if not strategy.active:
                        strategy.start()
                    strategy.on_tick()

            except Exception as e:
                logger.error(f"Error in strategy execution: {str(e)}")
            
            time.sleep(self.tick_interval)

    def stop(self):
        self.running = False
        logger.info("StrategyEngine main loop STOPPED.")

# Placeholder for the first actual strategy: Grid Trader
class GridTrader(BaseStrategy):
    def execute(self):
        # Example: Fetch price, check grid levels, place buy/sell
        price_info = self.client.get_product_price("BTC-USD")
        if not price_info:
            return
            
        price = float(price_info['price'])
        logger.info(f"[GridTrader] Tick - BTC Price: ${price:.2f}")
        
        # Grid logic would go here:
        # 1. Define range (e.g., $40k-$50k)
        # 2. Define number of tiers
        # 3. If price hits a tier and no open order, place limit order
        # For now, just logging price.
        pass
