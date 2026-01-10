import time
import logging

logger = logging.getLogger("TreasuryBridge")

class TreasuryBridge:
    def __init__(self, ledger):
        self.ledger = ledger
        self.conversion_rate = 70.0  # $70 USD (in BTC) = 1 AT (1 Hour Labor Equivalent)

    def process_ingress(self, sender, amount_usd, asset="BTC"):
        """
        Simulates the logic of receiving crypto and minting AT.
        In production, this would watch a wallet address.
        """
        at_to_mint = amount_usd / self.conversion_rate
        
        logger.info(f"🌉 INGRESS DETECTED: {amount_usd} {asset} from {sender}. Minting {at_to_mint:.2f} AT.")
        
        # Add to ledger as a TREASURY_INGRESS block
        block = self.ledger.add_block('TREASURY_INGRESS', {
            "sender": sender,
            "amount_fiat": amount_usd,
            "asset": asset,
            "at_minted": at_to_mint,
            "timestamp": time.time(),
            "status": "FINALIZED"
        })
        
        return {
            "status": "success",
            "at_minted": at_to_mint,
            "tx_hash": block['hash']
        }

    def get_market_metrics(self):
        return {
            "at_floor_price": self.conversion_rate,
            "bridge_status": "ACTIVE",
            "supported_assets": ["BTC", "SOL", "ETH"]
        }
