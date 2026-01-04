import logging

logger = logging.getLogger("RiskManager")

class RiskManager:
    """
    Ensures trading activities stay within user-defined bounds.
    """
    def __init__(self, max_drawdown=0.1, max_exposure_per_asset=0.2):
        self.max_drawdown = max_drawdown # 10% max loss from peak
        self.max_exposure_per_asset = max_exposure_per_asset # 20% of treasury per asset
        self.peak_value = 0
        self.current_value = 0

    def check_trade(self, asset, amount_usd, treasury_total_usd):
        """
        Validates if a trade is safe to execute.
        Returns: (bool, str) - (Allowed, Reason)
        """
        # 1. Exposure Check
        potential_exposure = amount_usd / treasury_total_usd
        if potential_exposure > self.max_exposure_per_asset:
            return False, f"Exposure limit exceeded: {potential_exposure:.1%} > {self.max_exposure_per_asset:.1%}"
            
        # 2. Drawdown Check
        if self.peak_value > 0:
            drawdown = (self.peak_value - self.current_value) / self.peak_value
            if drawdown > self.max_drawdown:
                return False, f"Max drawdown hit: {drawdown:.1%} > {self.max_drawdown:.1%}"
                
        return True, "Safe"

    def update_portfolio_value(self, total_usd):
        self.current_value = total_usd
        if total_usd > self.peak_value:
            self.peak_value = total_usd
            logger.info(f"New Treasury Peak: ${self.peak_value:.2f}")
