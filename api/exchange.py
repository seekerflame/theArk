from core.lightning_bridge import LightningBridge
import os

def register_exchange_routes(router, ledger, requires_auth):

    # Initialize Lightning Bridge
    # In a real setup, these would be env vars or config
    LND_URL = os.environ.get('LND_URL', 'https://localhost:8080')
    MACAROON_PATH = os.environ.get('LND_MACAROON_PATH', 'admin.macaroon')
    TLS_PATH = os.environ.get('LND_TLS_PATH', None)

    bridge = LightningBridge(LND_URL, MACAROON_PATH, TLS_PATH)

    @router.get('/api/exchange/quote')
    def h_quote(h):
        try:
            from urllib.parse import urlparse, parse_qs
            query = urlparse(h.path).query
            params = parse_qs(query)
            amount = float(params.get('amount', [1.0])[0])
            h.send_json(bridge.get_quote(amount))
        except ValueError:
            h.send_json_error("Invalid amount")

    @router.post('/api/exchange/buy')
    @requires_auth
    def h_buy(h, p, user):
        # User wants to buy AT with BTC
        # Payload: {"amount": 10} (Amount of AT to buy)
        try:
            amount = float(p.get('amount'))
            if amount <= 0: raise ValueError
        except:
            return h.send_json_error("Invalid amount")

        username = user['username']

        result = bridge.create_invoice(amount, username)
        if result:
            h.send_json(result)
        else:
            h.send_json_error("Failed to create invoice (Node offline?)", status=503)

    @router.get('/api/exchange/status')
    @requires_auth
    def h_status(h, user, p=None):
        # Check status of a swap and execute mint if settled
        # Query param: hash=<payment_hash>
        # Additional param: amount=<at_amount> (Since we don't store pending invoices in DB yet,
        # the client needs to pass back the expected amount to mint.
        # In a robust system, we'd store pending invoices in a DB table.)

        # For this MVP/Constraint 3 (Append-only ledger), we rely on the client or an in-memory queue.
        # Let's require the client to send the amount they expect.

        from urllib.parse import urlparse, parse_qs
        query = urlparse(h.path).query
        params = parse_qs(query)
        p_hash = params.get('hash', [None])[0]
        amount_str = params.get('amount', [None])[0]

        if not p_hash or not amount_str:
            return h.send_json_error("Missing hash or amount")

        try:
            amount = float(amount_str)
        except:
            return h.send_json_error("Invalid amount")

        # Execute Swap Logic (Checks LND, then updates Ledger)
        result = bridge.execute_swap(p_hash, ledger, user['username'], amount)
        h.send_json(result)
