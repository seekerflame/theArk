import time

def register_social_routes(router, ledger, requires_auth):

    @router.get('/api/messages')
    def h_get_messages(h):
        import urllib.parse
        query = urllib.parse.urlparse(h.path).query
        params = urllib.parse.parse_qs(query)
        channel = params.get('channel', ['general'])[0]
        msgs = [b['data'] for b in ledger.blocks if b['type'] == 'MESSAGE' and b['data'].get('channel', 'general') == channel]
        h.send_json(msgs[-100:])

    @router.post('/api/messages')
    @requires_auth
    def h_post_message(h, user, p):
        content = p.get('content')
        if not content: return h.send_error("Message content required")
        channel = p.get('channel', 'general')
        data = {'sender': user['sub'], 'content': content, 'channel': channel, 'timestamp': time.time()}
        block_hash = ledger.add_block('MESSAGE', data)
        h.send_json({"hash": block_hash, "data": data})

    @router.get('/api/bounties')
    def h_bounties(h):
        h.send_json({"bounties": ledger.get_bounties()})

    @router.post('/api/bounties/create')
    @requires_auth
    def h_bounty_create(h, user, p):
        data = {
            "id": str(int(time.time())),
            "title": p.get('title'),
            "description": p.get('description'),
            "reward": float(p.get('reward', 0)),
            "owner": user['sub'],
            "status": "OPEN",
            "worker": None,
            "proof": None
        }
        ledger.add_block('BOUNTY', data)
        h.send_json({"status": "success"})

    @router.post('/api/quest/create')
    @requires_auth
    def h_quest_create(h, user, p):
        title = p.get('title')
        reward = p.get('bounty_at', 10)
        if not title: return h.send_error("Quest must have a title")
        q_id = f"quest_{int(time.time())}"
        block_hash = ledger.add_block('QUEST', {
            'quest_id': q_id, 'title': title, 'reward': reward, 
            'owner': user['sub'], 'status': 'OPEN', 'created_at': time.time()
        })
        h.send_json({"quest_id": q_id, "hash": block_hash})
