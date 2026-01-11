import time

def register_transfer_routes(router, ledger, identity, requires_auth):
    @router.post('/api/transfer')
    @requires_auth
    def h_transfer(h, user, p):
        sender = user['sub']
        recv_input = p.get('receiver')
        amt = float(p.get('amount', 0))
        
        # Resolve handle (@alias or username)
        recv = identity.resolve_handle(recv_input)
        if not recv:
            return h.send_json_error(f"Recipient '{recv_input}' not found in the Ark.")

        if ledger.get_balance(sender) < amt: 
            return h.send_json_error("Insufficient life wealth (AT)")
            
        category = p.get('category', 'COMMUNITY') # DEFAULT TO COMMUNITY
        tx_data = {
            'sender': sender, 
            'receiver': recv, 
            'amount': amt, 
            'category': category,
            'timestamp': time.time()
        }
        
        h_res = ledger.add_block('TX', tx_data)
        h.send_json({"hash": h_res, "receiver": recv, "category": category})
