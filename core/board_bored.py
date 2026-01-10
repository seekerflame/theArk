import time
import json
import os

class BoardBored:
    def __init__(self, ledger, storage_path='ledger/board_bored_state.json'):
        self.ledger = ledger
        self.storage_path = storage_path
        self.ads = {}
        self.load()

    def load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                self.ads = json.load(f)

    def save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.ads, f, indent=2)

    def create_ad(self, advertiser, title, content, budget_at):
        ad_id = f"ad_{int(time.time() * 1000)}"
        self.ads[ad_id] = {
            "id": ad_id,
            "advertiser": advertiser,
            "title": title,
            "content": content,
            "budget_at": budget_at,
            "spent_at": 0.0,
            "views": 0,
            "active": True
        }
        self.save()
        return ad_id

    def interact(self, user, ad_id):
        if ad_id not in self.ads or not self.ads[ad_id]['active']:
            return False, "Ad not active or not found."

        ad = self.ads[ad_id]
        reward = 0.5 # Standard interaction reward (0.5 AT)

        if ad['spent_at'] + reward > ad['budget_at']:
            ad['active'] = False
            self.save()
            return False, "Ad budget exhausted."

        # Process Reward
        self.ledger.add_block('BOARD_BORED_INTERACTION', {
            "user": user,
            "ad_id": ad_id,
            "advertiser": ad['advertiser'],
            "reward": reward,
            "timestamp": time.time()
        })

        ad['spent_at'] += reward
        ad['views'] += 1
        self.save()
        return True, reward
