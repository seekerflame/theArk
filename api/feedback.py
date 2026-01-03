import time
import json
import os

def register_feedback_routes(router, ledger, requires_auth):

    @router.post('/api/feedback')
    def h_submit_feedback(h, p):
        # Allow anonymous feedback if user not logged in (p might not have username verified by token)
        # But app.js sends 'username' in body.

        user = p.get('username', 'Anonymous')
        f_type = p.get('type', 'GENERAL')
        msg = p.get('message')

        if not msg:
            return h.send_error("Message required")

        # Create a Feedback Block
        data = {
            "type": f_type,
            "submitter": user,
            "content": msg,
            "status": "OPEN",
            "timestamp": time.time()
        }

        # We store it in the ledger to ensure it's immutable and visible to the "Steward"
        block_hash = ledger.add_block('FEEDBACK', data)

        # Also log to a file for easy grep
        try:
            with open('feedback.log', 'a') as f:
                f.write(f"[{time.ctime()}] [{f_type}] {user}: {msg}\n")
        except:
            pass

        h.send_json({
            "status": "success",
            "message": "Feedback recorded on ledger.",
            "hash": block_hash,
            "reward": 10 if f_type == 'BUG' else 0 # Instant gratification simulation
        })
