# ========== SOCIAL & NIGHTLIFE (Bored Board Archives) ==========

SOCIAL_TEMPLATES = [
    {
        "title": "Bar Crawl Bingo",
        "description": "Visit 3 local spots, collect a stamp at each. Socialize and support local.",
        "reward_per_person": 0.5,
        "quest_type": "party",
        "category": "social",
        "child_friendly": False,
        "max_duration_hours": 4,
        "verification": "Photos of 3 drink/food receipts or stamps"
    },
    {
        "title": "Art Walk Scavenger Hunt",
        "description": "Find the 5 hidden murals in the downtown district.",
        "reward_per_person": 1.0,
        "quest_type": "solo",
        "category": "social",
        "child_friendly": True,
        "max_duration_hours": 2,
        "verification": "5 photos of murals"
    },
    {
        "title": "Third Space Assembly",
        "description": "Host a gathering at a local park or cafe to discuss community goals.",
        "reward_per_person": 2.0,
        "quest_type": "raid",
        "category": "social",
        "child_friendly": True,
        "max_duration_hours": 3,
        "verification": "Group photo + summary of discussion"
    }
]

def register_party_routes(router, party_quests, harvest, auth_decorator):
    """Register party quests and harvest marketplace endpoints."""
    
    @router.get('/api/social/templates')
    def h_social_templates(h):
        """Get social/nightlife quest templates."""
        h.send_json({"templates": SOCIAL_TEMPLATES})
    
    # ========== PARTY QUESTS ==========
    
    @router.get('/api/party/templates')
    def h_party_templates(h):
        """Get pre-built family quest templates."""
        from core.party_quests import FAMILY_TEMPLATES
        h.send_json({"templates": FAMILY_TEMPLATES})
    
    @router.get('/api/party/family')
    def h_family_quests(h):
        """Get child-friendly quests."""
        quests = party_quests.get_family_quests()
        h.send_json({"quests": quests})
    
    @router.post('/api/party/create')
    @auth_decorator
    def h_create_party(h, user, p):
        """Create a party quest."""
        success, result = party_quests.create_party_quest(user['sub'], p)
        if success:
            h.send_json({"status": "success", "party_id": result})
        else:
            h.send_error(result)
    
    @router.post('/api/party/join')
    @auth_decorator
    def h_join_party(h, user, p):
        """Join an existing party."""
        party_id = p.get('party_id')
        is_child = p.get('is_child', False)
        parent_id = p.get('parent_id')
        
        success, msg = party_quests.join_party(party_id, user['sub'], is_child, parent_id)
        if success:
            h.send_json({"status": "success", "message": msg})
        else:
            h.send_error(msg)
    
    @router.post('/api/party/start')
    @auth_decorator
    def h_start_party(h, user, p):
        """Start a party quest (leader only)."""
        party_id = p.get('party_id')
        success, msg = party_quests.start_party(party_id, user['sub'])
        if success:
            h.send_json({"status": "success", "message": msg})
        else:
            h.send_error(msg)
    
    @router.post('/api/party/complete')
    @auth_decorator
    def h_complete_party(h, user, p):
        """Submit party for verification."""
        party_id = p.get('party_id')
        proof = p.get('proof', {})
        success, msg = party_quests.complete_party(party_id, user['sub'], proof)
        if success:
            h.send_json({"status": "success", "message": msg})
        else:
            h.send_error(msg)
    
    @router.post('/api/party/verify')
    @auth_decorator
    def h_verify_party(h, user, p):
        """Verify party completion (oracle/admin)."""
        party_id = p.get('party_id')
        approved = p.get('approved', False)
        success, msg = party_quests.verify_party(party_id, user['sub'], approved)
        if success:
            h.send_json({"status": "success", "message": msg})
        else:
            h.send_error(msg)
    
    @router.get('/api/child/wallet')
    @auth_decorator
    def h_child_wallet(h, user, p):
        """Get child wallet info."""
        child_id = p.get('child_id', user['sub'])
        info = party_quests.get_child_wallet_info(child_id)
        if info:
            h.send_json(info)
        else:
            h.send_error("Child wallet not found")
    
    # ========== HARVEST MARKETPLACE ==========
    
    @router.get('/api/harvest/templates')
    def h_harvest_templates(h):
        """Get pre-built harvest listing templates."""
        from core.harvest_marketplace import HARVEST_TEMPLATES
        h.send_json({"templates": HARVEST_TEMPLATES})
    
    @router.get('/api/harvest/available')
    def h_harvest_available(h, p):
        """Get available harvest listings."""
        category = p.get('category')
        listings = harvest.get_available(category=category)
        h.send_json({"listings": listings})
    
    @router.post('/api/harvest/list')
    @auth_decorator
    def h_harvest_list(h, user, p):
        """Post produce for sale."""
        success, result = harvest.post_listing(user['sub'], p)
        if success:
            h.send_json({"status": "success", "listing_id": result})
        else:
            h.send_error(result)
    
    @router.post('/api/harvest/buy')
    @auth_decorator
    def h_harvest_buy(h, user, p):
        """Buy a listing."""
        listing_id = p.get('listing_id')
        success, msg = harvest.buy_listing(listing_id, user['sub'])
        if success:
            h.send_json({"status": "success", "message": msg})
        else:
            h.send_error(msg)
    
    @router.get('/api/harvest/my')
    @auth_decorator
    def h_my_harvest(h, user, p):
        """Get my listings."""
        listings = harvest.get_my_listings(user['sub'])
        h.send_json({"listings": listings})
    
    @router.post('/api/harvest/cancel')
    @auth_decorator
    def h_cancel_harvest(h, user, p):
        """Cancel a listing."""
        listing_id = p.get('listing_id')
        success, msg = harvest.cancel_listing(listing_id, user['sub'])
        if success:
            h.send_json({"status": "success", "message": msg})
        else:
            h.send_error(msg)
    
    @router.get('/api/harvest/provenance')
    def h_harvest_provenance(h, p):
        """Get provenance of a listing."""
        listing_id = p.get('listing_id')
        provenance = harvest.get_provenance(listing_id)
        if provenance:
            h.send_json({"provenance": provenance})
        else:
            h.send_error("Listing not found")
