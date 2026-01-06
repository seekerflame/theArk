from core.btc_bridge import bridge

def register_bridge_routes(router):

    @router.get('/api/bridge/status')
    def h_bridge_status(h):
        h.send_json(bridge.get_status())

    @router.get('/api/bridge/rate')
    def h_bridge_rate(h):
        h.send_json(bridge.get_exchange_rate())

    @router.post('/api/bridge/swap')
    def h_bridge_swap(h, p):
        direction = p.get('direction') # AT_TO_BTC or BTC_TO_AT
        amount = p.get('amount')
        wallet = p.get('wallet')

        if not all([direction, amount, wallet]):
            return h.send_error("Missing parameters: direction, amount, wallet")

        try:
            amount = float(amount)
        except ValueError:
             return h.send_error("Invalid amount")

        result = bridge.request_swap(direction, amount, wallet)
        h.send_json(result)
