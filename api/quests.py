"""
Quest System API - The Atomic Loop
==================================
Handles the full quest lifecycle:
1. POST (Create): Buyer posts quest with proposed AT
2. CLAIM: Worker claims quest 
3. NEGOTIATE: Worker/Buyer negotiate terms (optional)
4. SUBMIT: Worker submits proof of completion
5. VALIDATE: Oracle/Buyer validates and triggers AT mint
"""
import time
import json

def register_quest_routes(router, ledger, identity, requires_auth):

    
    # =====================
    # QUEST CRUD
    # =====================
    
    @router.get('/api/quests')
    def h_list_quests(h):
        """List all quests, filterable by status"""
        import urllib.parse
        query = urllib.parse.urlparse(h.path).query
        params = urllib.parse.parse_qs(query)
        status_filter = params.get('status', [None])[0]
        
        quests = []
        for b in ledger.blocks:
            if b['type'] == 'QUEST':
                quest = b['data'].copy()
                quest['hash'] = b['hash']
                # Get current status from latest update
                quest_id = quest.get('quest_id')
                # Check for status updates
                for update in ledger.blocks:
                    if update['type'] == 'QUEST_UPDATE' and update['data'].get('quest_id') == quest_id:
                        quest.update(update['data'])
                if status_filter is None or quest.get('status') == status_filter:
                    quests.append(quest)
        h.send_json(quests)
    
    @router.get('/api/quests/mine')
    def h_my_quests(h):
        """List quests I posted or am working on"""
        user = h.get_auth_user()
        if not user: return h.send_json_error("Auth Required", status=401)
        username = user['sub']
        
        my_quests = {'posted': [], 'working': [], 'completed': []}
        quest_states = {}
        
        # Build current state of all quests
        for b in ledger.blocks:
            if b['type'] == 'QUEST':
                q = b['data'].copy()
                quest_states[q['quest_id']] = q
            elif b['type'] == 'QUEST_UPDATE':
                qid = b['data'].get('quest_id')
                if qid in quest_states:
                    quest_states[qid].update(b['data'])
        
        for q in quest_states.values():
            if q.get('owner') == username:
                my_quests['posted'].append(q)
            if q.get('worker') == username:
                if q.get('status') == 'COMPLETED':
                    my_quests['completed'].append(q)
                else:
                    my_quests['working'].append(q)
        h.send_json(my_quests)
    
    @router.post('/api/quests/post')
    @requires_auth
    def h_post_quest(h, user, p):
        """
        Buyer posts a new quest with offer type:
        - FIXED: Set AT reward, no negotiation
        - ROLE_MULTIPLIED: Base AT × role multiplier (requires certification)
        - BARTER: Open-ended, worker proposes value after completion
        - NEGOTIATE: Buyer proposes, worker can counter-offer
        """
        title = p.get('title')
        description = p.get('description', '')
        offer_type = p.get('offer_type', 'FIXED')  # FIXED | ROLE_MULTIPLIED | BARTER | NEGOTIATE
        base_at = float(p.get('base_at', 10))
        required_role = p.get('required_role')  # For ROLE_MULTIPLIED
        deadline = p.get('deadline')
        skills_required = p.get('skills', [])
        
        if not title:
            return h.send_json_error("Quest must have a title")
        if offer_type not in ['FIXED', 'ROLE_MULTIPLIED', 'BARTER', 'NEGOTIATE']:
            return h.send_json_error("Invalid offer_type. Use: FIXED, ROLE_MULTIPLIED, BARTER, NEGOTIATE")
        
        quest_id = f"quest_{int(time.time())}_{user['sub'][:4]}"
        quest_data = {
            'quest_id': quest_id,
            'title': title,
            'description': description,
            'offer_type': offer_type,
            'base_at': base_at,
            'required_role': required_role,
            'skills_required': skills_required,
            'deadline': deadline,
            'owner': user['sub'],
            'status': 'OPEN',
            'worker': None,
            'agreed_at': base_at if offer_type == 'FIXED' else None,
            'negotiation_history': [],
            'created_at': time.time()
        }
        
        block_hash = ledger.add_block('QUEST', quest_data)
        h.send_json({'quest_id': quest_id, 'hash': block_hash, 'status': 'OPEN', 'offer_type': offer_type})
    
    # =====================
    # CLAIM & NEGOTIATION
    # =====================
    
    @router.post('/api/quests/claim')
    @requires_auth
    def h_claim_quest(h, user, p):
        """Worker claims a quest - can accept or counter-offer"""
        quest_id = p.get('quest_id')
        accept_terms = p.get('accept_terms', True)
        counter_offer = p.get('counter_offer')  # Optional AT counter-offer
        message = p.get('message', '')
        
        if not quest_id:
            return h.send_json_error("quest_id required")
        
        # Find the quest
        quest = _get_quest_state(ledger, quest_id)
        if not quest:
            return h.send_json_error("Quest not found", status=404)
        
        if quest.get('status') != 'OPEN':
            return h.send_json_error("Quest not available")
        offer_type = quest.get('offer_type', 'FIXED')
        
        if offer_type == 'FIXED':
            # Apply Holistic Multiplier
            hm = identity.get_holistic_multiplier(user['sub'], quest.get('required_role', 'WORKER'), ledger)
            agreed_at = quest.get('base_at', 10) * hm
            
            update_data = {
                'quest_id': quest_id,
                'worker': user['sub'],
                'status': 'IN_PROGRESS',
                'claimed_at': time.time(),
                'agreed_at': agreed_at,
                'hm_applied': hm
            }
            ledger.add_block('QUEST_UPDATE', update_data)
            return h.send_json({'status': 'claimed', 'quest_id': quest_id, 'agreed_at': agreed_at, 'hm': hm})

        
        elif offer_type == 'BARTER':
            # Worker can claim, will propose value after completion
            update_data = {
                'quest_id': quest_id,
                'worker': user['sub'],
                'status': 'IN_PROGRESS',
                'claimed_at': time.time(),
                'agreed_at': None  # TBD after completion
            }
            ledger.add_block('QUEST_UPDATE', update_data)
            return h.send_json({'status': 'claimed_barter', 'quest_id': quest_id, 'note': 'Propose value after completion'})
        
        elif offer_type == 'NEGOTIATE':
            if accept_terms:
                update_data = {
                    'quest_id': quest_id,
                    'worker': user['sub'],
                    'status': 'IN_PROGRESS',
                    'claimed_at': time.time(),
                    'agreed_at': quest.get('base_at', 10)
                }
                ledger.add_block('QUEST_UPDATE', update_data)
                return h.send_json({'status': 'claimed', 'quest_id': quest_id})
            else:
                # Worker counter-offers
                negotiation_entry = {
                    'from': user['sub'],
                    'type': 'counter_offer',
                    'proposed_at': counter_offer,
                    'message': message,
                    'timestamp': time.time()
                }
                update_data = {
                    'quest_id': quest_id,
                    'status': 'NEGOTIATING',
                    'pending_worker': user['sub'],
                    'pending_counter_offer': counter_offer,
                    'negotiation_entry': negotiation_entry
                }
                ledger.add_block('QUEST_UPDATE', update_data)
                return h.send_json({'status': 'negotiating', 'quest_id': quest_id})

    
    @router.post('/api/quests/respond')
    @requires_auth
    def h_respond_negotiation(h, user, p):
        """Owner responds to negotiation - accept, reject, or counter"""
        quest_id = p.get('quest_id')
        action = p.get('action')  # 'accept', 'reject', 'counter'
        counter_offer = p.get('counter_offer')
        message = p.get('message', '')
        
        quest = _get_quest_state(ledger, quest_id)
        if not quest:
            return h.send_json_error("Quest not found", status=404)
        if quest.get('owner') != user['sub']:
            return h.send_json_error("Only quest owner can respond")
        
        if action == 'accept':
            # Accept worker's terms
            agreed_at = quest.get('pending_counter_offer', quest.get('proposed_at'))
            update_data = {
                'quest_id': quest_id,
                'worker': quest.get('pending_worker'),
                'status': 'IN_PROGRESS',
                'agreed_at': agreed_at,
                'accepted_at': time.time()
            }
            ledger.add_block('QUEST_UPDATE', update_data)
            h.send_json({'status': 'accepted', 'worker': quest.get('pending_worker')})
        
        elif action == 'reject':
            update_data = {
                'quest_id': quest_id,
                'status': 'OPEN',
                'pending_worker': None
            }
            ledger.add_block('QUEST_UPDATE', update_data)
            h.send_json({'status': 'rejected_reopened'})
        
        elif action == 'counter':
            negotiation_entry = {
                'from': user['sub'],
                'type': 'counter_offer',
                'proposed_at': counter_offer,
                'message': message,
                'timestamp': time.time()
            }
            update_data = {
                'quest_id': quest_id,
                'pending_counter_offer': counter_offer,
                'negotiation_entry': negotiation_entry
            }
            ledger.add_block('QUEST_UPDATE', update_data)
            h.send_json({'status': 'counter_sent'})
        else:
            h.send_json_error("Invalid action. Use: accept, reject, counter")
    
    # =====================
    # SUBMISSION & VALIDATION
    # =====================
    
    @router.post('/api/quests/submit')
    @requires_auth
    def h_submit_proof(h, user, p):
        """Worker submits proof of completion"""
        quest_id = p.get('quest_id')
        proof = p.get('proof', {})  # Can include: description, photo_url, gps, etc.
        
        quest = _get_quest_state(ledger, quest_id)
        if not quest:
            return h.send_json_error("Quest not found", status=404)
        if quest.get('worker') != user['sub']:
            return h.send_json_error("Only assigned worker can submit")
        if quest.get('status') != 'IN_PROGRESS':
            return h.send_json_error("Quest not in progress")
        
        proof_data = {
            'quest_id': quest_id,
            'submitted_by': user['sub'],
            'proof': proof,
            'submitted_at': time.time()
        }
        update_data = {
            'quest_id': quest_id,
            'status': 'PENDING_VALIDATION',
            'proof': proof_data
        }
        block_hash = ledger.add_block('QUEST_UPDATE', update_data)
        h.send_json({'status': 'submitted', 'hash': block_hash})
    
    @router.post('/api/quests/validate')
    @requires_auth
    def h_validate_quest(h, user, p):
        """Owner/Oracle validates and triggers AT mint to worker"""
        quest_id = p.get('quest_id')
        approved = p.get('approved', True)
        feedback = p.get('feedback', '')
        
        quest = _get_quest_state(ledger, quest_id)
        if not quest:
            return h.send_json_error("Quest not found", status=404)
        
        # Oracle role check: Owner OR certified Oracle can validate
        user_roles = identity.get_user_roles(user['sub'], ledger)
        is_oracle = 'ORACLE' in user_roles
        is_owner = quest.get('owner') == user['sub']
        
        if not (is_owner or is_oracle):
            return h.send_json_error("Only quest owner or Oracle can validate")
        if quest.get('status') != 'PENDING_VALIDATION':
            return h.send_json_error("Quest not pending validation")
        
        if approved:
            # Apply Holistic Multiplier on Validation (Final Check)
            worker = quest.get('worker')
            role = quest.get('required_role', 'WORKER')
            hm = identity.get_holistic_multiplier(worker, role, ledger)
            
            reward = quest.get('agreed_at', 10)
            
            # If terms were negotiated but not settled by HM, ensure HM logic applies
            if quest.get('offer_type') == 'ROLE_MULTIPLIED':
                reward = quest.get('base_at', 10) * hm

            # Record the labor proof
            labor_data = {
                'minter': worker,
                'quest_id': quest_id,
                'reward': reward,
                'hm_applied': hm,
                'validated_by': user['sub'],
                'description': quest.get('title'),
                'timestamp': time.time()
            }
            mint_hash = ledger.add_block('LABOR', labor_data)
            
            # Update Tier Progress
            # We assume quest duration or difficulty maps to hours
            # For simplicity, base_at / 10 = hours liberated
            hours_liberated = reward / 10.0
            identity.add_verified_hours(worker, hours_liberated)

            # Calculate Time to Finish (Sovereign Efficiency)
            claimed_at = quest.get('claimed_at', quest.get('created_at', time.time()))
            completed_at = time.time()
            duration_sec = completed_at - claimed_at
            duration_hr = round(duration_sec / 3600.0, 2)

            # Update quest status
            update_data = {
                'quest_id': quest_id,
                'status': 'COMPLETED',
                'completed_at': completed_at,
                'duration_seconds': duration_sec,
                'duration_hours': duration_hr,
                'mint_hash': mint_hash,
                'feedback': feedback,
                'reward_final': reward,
                'hm_final': hm
            }
            ledger.add_block('QUEST_UPDATE', update_data)

            return h.send_json({
                'status': 'completed',
                'worker': worker,
                'at_minted': reward,
                'duration_hours': duration_hr,
                'mint_hash': mint_hash
            })

        else:
            # Reject submission, reopen for more work
            update_data = {
                'quest_id': quest_id,
                'status': 'IN_PROGRESS',
                'rejection_feedback': feedback,
                'rejected_at': time.time()
            }
            ledger.add_block('QUEST_UPDATE', update_data)
            h.send_json({'status': 'rejected', 'feedback': feedback})
    
    # =====================
    # QUEST DISCOVERY
    # =====================
    
    @router.get('/api/quests/recommended')
    def h_recommended_quests(h):
        """Get quests recommended for the user based on skills"""
        user = h.get_auth_user()
        # For now, just return open quests sorted by reward
        open_quests = []
        for b in ledger.blocks:
            if b['type'] == 'QUEST':
                quest = _get_quest_state(ledger, b['data']['quest_id'])
                if quest and quest.get('status') == 'OPEN':
                    open_quests.append(quest)
        
        # Sort by reward (highest first)
        open_quests.sort(key=lambda q: q.get('base_at', q.get('proposed_at', 0)), reverse=True)
        h.send_json(open_quests[:20])


def _get_quest_state(ledger, quest_id):
    """Build current state of a quest from all updates"""
    quest = None
    for b in ledger.blocks:
        if b['type'] == 'QUEST' and b['data'].get('quest_id') == quest_id:
            quest = b['data'].copy()
            quest['hash'] = b['hash']
    if not quest:
        return None
    # Apply updates
    for b in ledger.blocks:
        if b['type'] == 'QUEST_UPDATE' and b['data'].get('quest_id') == quest_id:
            quest.update(b['data'])
    return quest
