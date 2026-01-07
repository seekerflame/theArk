import os
import json

def register_treasury_routes(router, treasury_bot, auth_decorator):
    
    @router.get('/api/treasury/status')
    @auth_decorator
    def h_treasury_status(h, user):
        """Returns the current status of the Treasury Bot."""
        h.send_json(treasury_bot.get_status())

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
