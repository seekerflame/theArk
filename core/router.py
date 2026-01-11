import time
from functools import wraps

class Router:
    def __init__(self): 
        self.routes = {'GET': {}, 'POST': {}}
    
    def get(self, path):
        def d(f): self.routes['GET'][path] = f; return f
        return d
    
    def post(self, path):
        def d(f): self.routes['POST'][path] = f; return f
        return d

# Global rates
USER_RATE_LIMITS = {}

def requires_auth(identity_manager):
    def decorator(f):
        @wraps(f)
        def wrapper(handler, payload=None, *args, **kwargs):
            u = handler.get_auth_user()
            if not u: return handler.send_json_error("Unauthorized", status=401)
            uname = u['sub']
            now = time.time()
            if uname not in USER_RATE_LIMITS: USER_RATE_LIMITS[uname] = []
            USER_RATE_LIMITS[uname] = [t for t in USER_RATE_LIMITS[uname] if now - t < 60]
            if len(USER_RATE_LIMITS[uname]) > 5000: return handler.send_json_error("Too many requests (User)", status=429)
            USER_RATE_LIMITS[uname].append(now)
            
            return f(handler, u, payload, *args, **kwargs)
        return wrapper
    return decorator

def admin_only(f):
    @wraps(f)
    def wrapper(handler, user, *args, **kwargs):
        if user.get('role') != 'ADMIN': return handler.send_json_error("Admin access required", status=403)
        return f(handler, user, *args, **kwargs)
    return wrapper
