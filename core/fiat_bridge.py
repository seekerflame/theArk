"""
Fiat Bridge - Full on/off ramp for AT
Card → BTC → AT → Wallet → Merchant Bank

Uses existing Coinbase/Lightning integrations
"""

import time
from typing import Dict, Tuple

class FiatBridge:
    """
    Complete fiat on/off ramp:
    
    ON-RAMP (User buying AT):
    Card → Coinbase → BTC → Lightning → AT
    
    OFF-RAMP (Merchant cashing out):
    AT → Lightning → BTC → Coinbase → Bank
    """
    
    def __init__(self, ledger, lightning_client=None, coinbase_client=None):
        self.ledger = ledger
        self.lightning = lightning_client
        self.coinbase = coinbase_client
        
        # Current exchange rates (mocked for MVP, real API later)
        self.rates = {
            "BTC_USD": 45000.0,
            "AT_BTC": 0.00001,  # 1 AT = 0.00001 BTC (1 hour labor)
        }
        
    def get_at_price_usd(self) -> float:
        """Get current AT price in USD."""
        return self.rates["AT_BTC"] * self.rates["BTC_USD"]
    
    def estimate_purchase(self, usd_amount: float) -> Dict:
        """
        Estimate how much AT user gets for USD amount.
        Includes all fees transparently.
        """
        # Fee breakdown (honest about all costs)
        coinbase_fee = usd_amount * 0.015  # 1.5% Coinbase fee
        lightning_fee = 0.01  # ~1 cent Lightning fee
        
        net_usd = usd_amount - coinbase_fee - lightning_fee
        btc_amount = net_usd / self.rates["BTC_USD"]
        at_amount = btc_amount / self.rates["AT_BTC"]
        
        return {
            "usd_input": usd_amount,
            "coinbase_fee": round(coinbase_fee, 2),
            "lightning_fee": round(lightning_fee, 2),
            "net_usd": round(net_usd, 2),
            "btc_amount": round(btc_amount, 8),
            "at_amount": round(at_amount, 2),
            "effective_rate": round(at_amount / usd_amount, 4),
            "note": "1 AT ≈ 1 hour of human labor"
        }
    
    def buy_at_with_card(self, user: str, usd_amount: float, card_token: str) -> Tuple[bool, Dict]:
        """
        Full on-ramp flow:
        1. Charge card via Coinbase (or Stripe → Coinbase)
        2. Convert USD to BTC
        3. Send BTC to our Lightning node
        4. Credit AT to user wallet
        
        For MVP: This is SIMULATED. Real integration requires:
        - Coinbase Commerce API key
        - Lightning node with macaroon
        - Card processor (Stripe) for non-crypto cards
        """
        estimate = self.estimate_purchase(usd_amount)
        
        # Simulate the flow (real implementation would call APIs)
        if self.coinbase and hasattr(self.coinbase, 'create_charge'):
            # Real Coinbase flow
            charge = self.coinbase.create_charge(
                amount=usd_amount,
                currency="USD",
                name="Buy AT",
                description=f"Purchase {estimate['at_amount']} Abundance Tokens"
            )
            # Would wait for webhook confirmation...
        else:
            # Simulated for MVP demo
            pass
        
        # Credit AT to user
        self.ledger.add_block('FIAT_PURCHASE', {
            "user": user,
            "usd_amount": usd_amount,
            "at_credited": estimate["at_amount"],
            "btc_amount": estimate["btc_amount"],
            "fees": {
                "coinbase": estimate["coinbase_fee"],
                "lightning": estimate["lightning_fee"]
            },
            "timestamp": time.time()
        })
        
        return True, {
            "success": True,
            "at_credited": estimate["at_amount"],
            "message": f"Purchased {estimate['at_amount']} AT for ${usd_amount}"
        }
    
    def estimate_cashout(self, at_amount: float) -> Dict:
        """
        Estimate how much USD merchant gets for AT amount.
        """
        btc_amount = at_amount * self.rates["AT_BTC"]
        usd_gross = btc_amount * self.rates["BTC_USD"]
        
        # Fee breakdown
        lightning_fee = 0.01
        coinbase_fee = usd_gross * 0.015
        bank_fee = 0.25  # ACH transfer fee
        
        net_usd = usd_gross - lightning_fee - coinbase_fee - bank_fee
        
        return {
            "at_input": at_amount,
            "btc_amount": round(btc_amount, 8),
            "usd_gross": round(usd_gross, 2),
            "lightning_fee": round(lightning_fee, 2),
            "coinbase_fee": round(coinbase_fee, 2),
            "bank_fee": round(bank_fee, 2),
            "net_usd": round(net_usd, 2),
            "effective_rate": round(net_usd / at_amount, 4) if at_amount > 0 else 0
        }
    
    def cashout_to_bank(self, user: str, at_amount: float, bank_info: Dict) -> Tuple[bool, Dict]:
        """
        Full off-ramp flow:
        1. Debit AT from merchant wallet
        2. Convert AT to BTC via Lightning
        3. Sell BTC on Coinbase
        4. ACH transfer to merchant bank
        
        bank_info: {
            "account_number": str,
            "routing_number": str,
            "account_type": "checking" | "savings"
        }
        
        For MVP: SIMULATED. Real integration requires verified Coinbase account.
        """
        # Check user has enough AT
        balance = self.ledger.get_balance(user)
        if balance < at_amount:
            return False, {"error": f"Insufficient AT. Have {balance}, need {at_amount}"}
        
        estimate = self.estimate_cashout(at_amount)
        
        # Debit AT
        self.ledger.add_block('FIAT_CASHOUT', {
            "user": user,
            "at_amount": at_amount,
            "btc_amount": estimate["btc_amount"],
            "usd_net": estimate["net_usd"],
            "bank_last4": bank_info.get("account_number", "0000")[-4:],
            "fees": {
                "lightning": estimate["lightning_fee"],
                "coinbase": estimate["coinbase_fee"],
                "bank": estimate["bank_fee"]
            },
            "status": "processing",  # Would be updated by webhook
            "timestamp": time.time()
        })
        
        return True, {
            "success": True,
            "at_debited": at_amount,
            "usd_to_bank": estimate["net_usd"],
            "eta": "1-3 business days",
            "message": f"Cashout initiated. ${estimate['net_usd']} to bank ending in {bank_info.get('account_number', '0000')[-4:]}"
        }
    
    def get_exchange_status(self) -> Dict:
        """Get current exchange rates and system status."""
        return {
            "rates": {
                "AT_USD": self.get_at_price_usd(),
                "BTC_USD": self.rates["BTC_USD"],
                "AT_BTC": self.rates["AT_BTC"]
            },
            "fees": {
                "buy": "~1.5% + $0.01",
                "sell": "~1.5% + $0.26"
            },
            "status": "operational",
            "note": "Powered by Coinbase + Lightning Network"
        }


def register_fiat_routes(router, ledger, fiat_bridge, requires_auth):
    """Register fiat bridge API endpoints."""
    
    @router.get('/api/fiat/rates')
    def h_rates(h):
        """Get current exchange rates."""
        h.send_json(fiat_bridge.get_exchange_status())
    
    @router.post('/api/fiat/estimate-buy')
    def h_estimate_buy(h, p):
        """Estimate AT purchase."""
        usd_amount = float(p.get('usd_amount', 0))
        if usd_amount <= 0:
            return h.send_error("usd_amount must be positive")
        h.send_json(fiat_bridge.estimate_purchase(usd_amount))
    
    @router.post('/api/fiat/buy')
    @requires_auth
    def h_buy(h, user, p):
        """Buy AT with card."""
        usd_amount = float(p.get('usd_amount', 0))
        card_token = p.get('card_token', 'simulated')
        
        if usd_amount <= 0:
            return h.send_error("usd_amount must be positive")
        
        success, result = fiat_bridge.buy_at_with_card(user['sub'], usd_amount, card_token)
        if success:
            h.send_json(result)
        else:
            h.send_error(result.get('error', 'Purchase failed'))
    
    @router.post('/api/fiat/estimate-cashout')
    @requires_auth
    def h_estimate_cashout(h, user, p):
        """Estimate cashout to bank."""
        at_amount = float(p.get('at_amount', 0))
        if at_amount <= 0:
            return h.send_error("at_amount must be positive")
        h.send_json(fiat_bridge.estimate_cashout(at_amount))
    
    @router.post('/api/fiat/cashout')
    @requires_auth
    def h_cashout(h, user, p):
        """Cashout AT to bank."""
        at_amount = float(p.get('at_amount', 0))
        bank_info = p.get('bank_info', {})
        
        if at_amount <= 0:
            return h.send_error("at_amount must be positive")
        if not bank_info.get('account_number') or not bank_info.get('routing_number'):
            return h.send_error("bank_info must include account_number and routing_number")
        
        success, result = fiat_bridge.cashout_to_bank(user['sub'], at_amount, bank_info)
        if success:
            h.send_json(result)
        else:
            h.send_error(result.get('error', 'Cashout failed'))
