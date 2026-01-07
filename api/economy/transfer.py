import time

def register_transfer_routes(router, ledger, requires_auth):
    @router.post('/api/transfer')
    @requires_auth
    def h_transfer(h, user, p):
        sender = user['sub']
        recv, amt = p.get('receiver'), float(p.get('amount', 0))
        if ledger.get_balance(sender) < amt: return h.send_json_error("Insufficient life wealth (AT)")
        h_res = ledger.add_block('TX', {'sender': sender, 'receiver': recv, 'amount': amt, 'timestamp': time.time()})
        h.send_json({"hash": h_res})
