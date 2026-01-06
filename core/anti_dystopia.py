"""
Anti-Dystopia Code Constraints
Hard rules that CANNOT be violated without forking
"""

class DystopiaViolation(Exception):
    """Raised when code attempts to violate anti-dystopia principles"""
    pass

# CONSTRAINT 1: No Central Ban Authority
def enforce_no_central_bans(ledger):
    """
    Verify that no single entity can freeze/ban accounts
    """
    if hasattr(ledger, 'freeze_account'):
        raise DystopiaViolation(
            "VIOLATION: Central freeze authority detected. "
            "Ark OS does not allow account freezing. "
            "Users control their own keys."
        )
    
    if hasattr(ledger, 'ban_user'):
        raise DystopiaViolation(
            "VIOLATION: Central ban authority detected. "
            "Ark OS is peer-to-peer. No central authority can ban."
        )

# CONSTRAINT 2: Pseudonymity Enforced
def enforce_pseudonymity(user_data):
    """
    Verify that real identity is OPTIONAL, not required
    """
    required_fields = ['wallet_id']
    forbidden_required_fields = ['ssn', 'real_name', 'government_id', 'email']
    
    for field in user_data.get('required', []):
        if field in forbidden_required_fields:
            raise DystopiaViolation(
                f"VIOLATION: {field} is required. "
                "Ark OS operates on pseudonymous wallets. "
                "Real identity must be OPTIONAL."
            )

# CONSTRAINT 3: Self-Custody Only
def enforce_self_custody(auth_system):
    """
    Verify that ONLY the user holds their private key
    """
    if hasattr(auth_system, 'master_key'):
        raise DystopiaViolation(
            "VIOLATION: Master key detected. "
            "Ark OS does not allow backdoors. "
            "Users must hold their own keys."
        )
    
    if hasattr(auth_system, 'reset_password'):
        raise DystopiaViolation(
            "VIOLATION: Password reset detected. "
            "Ark OS does not allow key recovery. "
            "If you lose your key, you lose your wallet. No exceptions."
        )

# CONSTRAINT 4: No Surveillance Tracking
def enforce_minimal_data(tracking_config):
    """
    Verify that only NECESSARY data is collected
    """
    forbidden_tracking = [
        'browsing_history',
        'location_always_on',
        'social_graph',
        'device_fingerprint',
        'biometric_data'
    ]
    
    for track in tracking_config.get('enabled', []):
        if track in forbidden_tracking:
            raise DystopiaViolation(
                f"VIOLATION: {track} tracking enabled. "
                "Ark OS collects ONLY what's needed for labor verification. "
                "No surveillance tracking allowed."
            )

# CONSTRAINT 5: Open Source Enforced
def enforce_open_source(codebase):
    """
    Verify that all code is visible and forkable
    """
    if codebase.get('license') not in ['AGPLv3', 'GPLv3', 'MIT']:
        raise DystopiaViolation(
            "VIOLATION: Proprietary license detected. "
            "Ark OS must be open source. "
            "Users must be able to audit and fork."
        )
    
    if codebase.get('source_available') != True:
        raise DystopiaViolation(
            "VIOLATION: Source code not public. "
            "Ark OS requires full transparency. "
            "No closed-source components."
        )

# CONSTRAINT 6: Exit Rights
def enforce_exit_rights(platform):
    """
    Verify that users can export data and leave
    """
    if not hasattr(platform, 'export_data'):
        raise DystopiaViolation(
            "VIOLATION: No data export function. "
            "Users must be able to export their entire history. "
            "No lock-in allowed."
        )
    
    # Handle both dict and object
    export_cost = getattr(platform, 'export_cost', platform.get('export_cost', 0) if hasattr(platform, 'get') else 0)
    
    if export_cost > 0:
        raise DystopiaViolation(
            "VIOLATION: Data export costs money. "
            "Export must be FREE. No ransom for your own data."
        )

# CONSTRAINT 7: No Algorithmic Manipulation
def enforce_chronological_feeds(feed_system):
    """
    Verify that content is shown chronologically, not algorithmically
    """
    if feed_system.get('sort_by') == 'algorithmic':
        raise DystopiaViolation(
            "VIOLATION: Algorithmic feed detected. "
            "Ark OS shows content CHRONOLOGICALLY. "
            "No manipulation, no engagement optimization."
        )

# CONSTRAINT 8: No Third-Party Data Sales
def enforce_no_data_sales(revenue_model):
    """
    Verify that user data is NEVER sold
    """
    if 'data_sales' in revenue_model.get('sources', []):
        raise DystopiaViolation(
            "VIOLATION: Data sales revenue stream detected. "
            "Ark OS NEVER sells user data. "
            "Revenue must come from voluntary contributions or services."
        )

# CONSTRAINT 9: No Truth Policing
def enforce_no_misinformation_bans(moderation_policy):
    """
    Ark OS can NEVER ban for "misinformation" or "fake news"
    This is a slippery slope to thought police
    """
    forbidden_ban_reasons = [
        'misinformation',
        'fake_news',
        'conspiracy_theory',
        'unverified_claim',
        'disinformation'
    ]
    
    for reason in moderation_policy.get('ban_reasons', []):
        if any(forbidden in reason.lower() for forbidden in forbidden_ban_reasons):
            raise DystopiaViolation(
                f"VIOLATION: Truth policing detected ({reason}). "
                "Ark OS does NOT moderate 'misinformation'. "
                "Counter bad ideas with good ideas, not censorship."
            )

# CONSTRAINT 10: Recursive Verification Required
def enforce_verify_verifiers(oracle_system):
    """
    Oracles must be verified by meta-oracles
    Power = Scrutiny (inverted incentive)
    """
    if not oracle_system.get('meta_oracle_enabled'):
        raise DystopiaViolation(
            "VIOLATION: No meta-oracle verification. "
            "Who watches the watchmen? "
            "Oracles must be audited by higher layer."
        )
    
    if not oracle_system.get('inverted_incentive'):
        raise DystopiaViolation(
            "VIOLATION: Power scales without accountability. "
            "More verifications = More audits required. "
            "Prevent concentration of power."
        )

# Run all constraint checks
def verify_anti_dystopia_compliance(system):
    """
    Run all anti-dystopia checks
    Fails hard if ANY constraint is violated
    """
    print("🔒 Running Anti-Dystopia Compliance Checks...")
    
    try:
        enforce_no_central_bans(system.ledger)
        print("✅ No central ban authority")
        
        enforce_pseudonymity(system.user_model)
        print("✅ Pseudonymity enforced")
        
        enforce_self_custody(system.auth)
        print("✅ Self-custody only")
        
        enforce_minimal_data(system.tracking)
        print("✅ Minimal data collection")
        
        enforce_open_source(system.codebase)
        print("✅ Open source verified")
        
        enforce_exit_rights(system.platform)
        print("✅ Exit rights preserved")
        
        enforce_chronological_feeds(system.feeds)
        print("✅ Chronological feeds only")
        
        enforce_no_data_sales(system.revenue)
        print("✅ No data sales")
        
        enforce_no_misinformation_bans(system.moderation)
        print("✅ No truth policing")
        
        enforce_verify_verifiers(system.oracles)
        print("✅ Recursive verification enforced")
        
        print("\n🎉 COMPLIANCE VERIFIED: Not dystopian (yet)")
        return True
        
    except DystopiaViolation as e:
        print(f"\n❌ DYSTOPIA DETECTED: {e}")
        print("\n🚨 FORK THE CODE IMMEDIATELY 🚨")
        raise

if __name__ == "__main__":
    # This should be run on EVERY deployment
    # If it fails, deployment is BLOCKED
    print("Ark OS Anti-Dystopia Compliance Check\n")
    
    # Simulated system for testing
    test_system = {
        'ledger': {},  # No freeze/ban methods
        'user_model': {'required': ['wallet_id']},
        'auth': {},  # No master key or reset
        'tracking': {'enabled': ['transaction_hash', 'timestamp']},
        'codebase': {'license': 'AGPLv3', 'source_available': True},
        'platform': type('obj', (object,), {'export_data': lambda: None, 'export_cost': 0})(),
        'feeds': {'sort_by': 'chronological'},
        'revenue': {'sources': ['voluntary_contributions']},
        'moderation': {'ban_reasons': ['violence', 'csam', 'fraud']},  # No misinformation
        'oracles': {'meta_oracle_enabled': True, 'inverted_incentive': True}
    }
    
    class System:
        def __init__(self, config):
            for key, value in config.items():
                setattr(self, key, value)
    
    system = System(test_system)
    verify_anti_dystopia_compliance(system)
