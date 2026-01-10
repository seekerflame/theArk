import os
import json

from core.treasury_bridge import TreasuryBridge

def register_treasury_routes(router, treasury_bot, ledger, auth_decorator):
    
    bridge = TreasuryBridge(ledger)

    @router.get('/api/treasury/status')
    @auth_decorator
    def h_treasury_status(h, user):
        """Returns the current status of the Treasury Bot and Bridge."""
        status = treasury_bot.get_status()
        status['bridge'] = bridge.get_market_metrics()
        h.send_json(status)

    @router.post('/api/treasury/ingress')
    @auth_decorator
    def h_treasury_ingress(h, p, user):
        """Processes a simulated crypto deposit."""
        sender = user['sub']
        amount = float(p.get('amount_usd', 0))
        asset = p.get('asset', 'BTC')
        
        if amount <= 0:
            return h.send_json_error("Amount must be greater than zero.")
            
        result = bridge.process_ingress(sender, amount, asset)
        h.send_json(result)

    @router.post('/api/treasury/config')
    @auth_decorator
    def h_treasury_config(h, p, user):
        """Updates the Treasury Bot configuration."""
        # Only admin can update config (simple check)
        if user.get('role') != 'admin':
            return h.send_json_error("Unauthorized", status=403)
            
        # Update config logic
        new_config = p
        # Save to file...
        config_path = 'config/treasury_config.json'
        try:
            with open(config_path, 'w') as f:
                json.dump(new_config, f, indent=2)
            # Potentially restart/refresh bot
            h.send_json({"status": "Config updated. Restart required for some changes."})
        except Exception as e:
            h.send_json_error(f"Failed to update config: {str(e)}")
