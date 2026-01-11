# Economy API Package
# Central hub for all economic sub-modules

from .roles import register_role_routes
from .mint import register_mint_routes
from .market import register_market_routes
from .transfer import register_transfer_routes
from .stats import register_stats_routes

def register_economy_routes(router, ledger, sensors, identity, justice, requires_auth, quest_system=None, verification=None):
    """
    Registers all economy-related routes by delegating to sub-modules.
    """
    
    # 1. Role & Certification Routes
    register_role_routes(router, identity, ledger, requires_auth)
    
    # 2. Minting Routes (Labor & Code)
    register_mint_routes(router, ledger, identity, justice, requires_auth)
    
    # 3. Market Routes (Store & Purchase)
    register_market_routes(router, ledger, requires_auth)
    
    # 4. Transfer Routes
    register_transfer_routes(router, ledger, identity, requires_auth)
    
    # 5. Stats/Evolution Routes
    register_stats_routes(router, ledger, sensors)
    
    # Note: Quest-related routes are handled entirely by api/quests.py
    # Legacy inline quest logic has been removed during refactor.
