
import time

class TradeEngine:
    def __init__(self, ledger):
        self.ledger = ledger
        self.active_trades = {}

    def propose_trade(self, initiator_node, target_node, offer, request):
        trade_id = f"trade_{int(time.time())}_{initiator_node}"
        trade = {
            "id": trade_id,
            "initiator": initiator_node,
            "target": target_node,
            "offer": offer,     # e.g., {"type": "AT", "amount": 10}
            "request": request, # e.g., {"type": "CODE", "uri": "core/fusion.py"}
            "status": "pending",
            "timestamp": time.time()
        }
        self.active_trades[trade_id] = trade
        return trade

    def accept_trade(self, trade_id):
        if trade_id in self.active_trades:
            self.active_trades[trade_id]['status'] = 'accepted'
            # Trigger atomic swap logic here
            return True
        return False

def register_trade_routes(router, ledger, auth_decorator):
    engine = TradeEngine(ledger)

    @router.post('/api/trade/propose')
    @auth_decorator
    def h_propose_trade(h, user, p):
        # p should contain target_node, offer, request
        trade = engine.propose_trade(user['sub'], p.get('target_node'), p.get('offer'), p.get('request'))
        h.send_json({"status": "success", "trade": trade})

    @router.post('/api/trade/accept')
    @auth_decorator
    def h_accept_trade(h, user, p):
        success = engine.accept_trade(p.get('trade_id'))
        if success:
            h.send_json({"status": "success"})
        else:
            h.send_json_error("Trade not found or invalid")
