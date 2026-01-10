from core.board_bored import BoardBored

def register_board_bored_routes(router, ledger, auth_decorator):
    bb = BoardBored(ledger)

    @router.get('/api/bored/ads')
    def list_ads(h):
        active_ads = [ad for ad in bb.ads.values() if ad['active']]
        h.send_json({"ads": active_ads})

    @router.post('/api/bored/interact')
    @auth_decorator
    def interact_ad(h, user, p):
        ad_id = p.get('ad_id')
        success, result = bb.interact(user['sub'], ad_id)
        
        if success:
            h.send_json({
                "status": "success",
                "reward": result,
                "message": f"Interaction verified. Received {result} AT."
            })
        else:
            h.send_json_error(result)

    @router.post('/api/bored/create')
    @auth_decorator
    def create_ad(h, user, p):
        # Only FOUNDERs can create for now in demo
        title = p.get('title')
        content = p.get('content')
        budget = float(p.get('budget', 10.0))
        
        ad_id = bb.create_ad(user['sub'], title, content, budget)
        h.send_json({"status": "success", "ad_id": ad_id})
