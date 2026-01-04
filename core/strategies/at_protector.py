import logging
from core.strategy_engine import BaseStrategy

logger = logging.getLogger("ATProtector")

class ATProtector(BaseStrategy):
    """
    Protects the value of the Abundance Token (AT).
    Monitors market price relative to a 'Mission Floor'.
    If price < floor, uses treasury reserves to buy AT (Market Support).
    """
    def __init__(self, client, floor_btc=0.000008, reserve_allocation=0.3):
        super().__init__("ATProtector", client)
        self.floor_btc = floor_btc # 1 AT should be at least this much BTC
        self.reserve_allocation = reserve_allocation # Max % of treasury to use for protection

    def execute(self):
        # 1. Fetch current price
        price_info = self.client.get_product_price("AT-BTC")
        if not price_info:
            logger.warning("Could not fetch AT-BTC price for protection check.")
            return
            
        current_price = float(price_info['price'])
        
        # 2. Compare with floor
        if current_price < self.floor_btc:
            logger.info(f"PROTECTION TRIGGERED: AT Price {current_price:.8f} BTC < Floor {self.floor_btc:.8f} BTC")
            self._apply_buy_pressure(current_price)
        else:
            logger.info(f"AT Stability: {current_price:.8f} BTC (Above Floor)")

    def _apply_buy_pressure(self, price):
        # In a real bot, we'd calculate how much to buy based on available reserves
        # For now, just simulated action.
        logger.info(f"Simulating market-making buy order for AT to restore floor.")
        # self.client.place_order("AT-BTC", "BUY", 1000, price * 1.001) 
