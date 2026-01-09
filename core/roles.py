"""
Role System Implementation
Maps all SOPs to active roles with capabilities
"""

# Core Roles Based on SOPs
ROLE_DEFINITIONS = {
    # ===== PRODUCTION ROLES (Direct Value Creation) =====
    "BUILDER": {
        "title": "Builder",
        "base_multiplier": 1.5,
        "sops": ["MBD_001", "HK_001"],
        "capabilities": [
            "construct_infrastructure",
            "repair_equipment",
            "install_hardware",
            "fabricate_parts"
        ],
        "quest_tags": ["construction", "repair", "fabrication", "infrastructure"],
        "onboarding": "Build physical infrastructure for village sovereignty",
        "value_metric": "Square footage built, repairs completed"
    },
    
    "FARMER": {
        "title": "Farmer / Food Producer",
        "base_multiplier": 1.8,
        "sops": ["HK_001", "PSY_001"],
        "capabilities": [
            "grow_food",
            "manage_greenhouse",
            "harvest_crops",
            "soil_management"
        ],
        "quest_tags": ["agriculture", "food", "harvest", "greenhouse"],
        "onboarding": "Produce food for village self-sufficiency",
        "value_metric": "Calories produced, crops harvested"
    },
    
    "ENERGY_TECH": {
        "title": "Energy Technician",
        "base_multiplier": 2.0,
        "sops": ["DEF_001", "NET_001"],
        "capabilities": [
            "install_solar",
            "maintain_battery",
            "monitor_grid",
            "optimize_power"
        ],
        "quest_tags": ["solar", "energy", "power", "kardashev"],
        "onboarding": "Maintain and optimize village energy systems",
        "value_metric": "kWh generated, uptime maintained"
    },
    
    "DEVELOPER": {
        "title": "Software Developer",
        "base_multiplier": 2.5,
        "sops": ["MBD_001", "TNP_001", "FILE_TAXONOMY"],
        "capabilities": [
            "write_code",
            "fix_bugs",
            "build_features",
            "test_systems"
        ],
        "quest_tags": ["code", "software", "api", "automation"],
        "onboarding": "Build software infrastructure for The Ark",
        "value_metric": "Lines of code, features shipped"
    },
    
    # ===== GOVERNANCE ROLES (System Integrity) =====
    "ORACLE": {
        "title": "Oracle / Validator",
        "base_multiplier": 1.8,
        "sops": ["SDP_001", "PSY_001", "PHILOSOPHY_001"],
        "capabilities": [
            "validate_labor",
            "audit_quality",
            "resolve_disputes",
            "certify_users"
        ],
        "quest_tags": ["validation", "audit", "quality", "governance"],
        "onboarding": "Validate labor and maintain system integrity",
        "value_metric": "Validations performed, disputes resolved",
        "requires_certification": True
    },
    
    "HEARTH_KEEPER": {
        "title": "Hearth Keeper",
        "base_multiplier": 1.6,
        "sops": ["HK_001", "PSY_001"],
        "capabilities": [
            "provide_meals",
            "maintain_morale",
            "coordinate_logistics",
            "ensure_wellness"
        ],
        "quest_tags": ["meals", "wellness", "logistics", "morale"],
        "onboarding": "Keep the village fed, rested, and thriving",
        "value_metric": "Meals served, morale score"
    },
    
    "CHRONICLER": {
        "title": "Chronicler / Documenter",
        "base_multiplier": 1.4,
        "sops": ["SDP_001", "DATA_001"],
        "capabilities": [
            "document_knowledge",
            "maintain_wiki",
            "create_guides",
            "preserve_history"
        ],
        "quest_tags": ["documentation", "wiki", "chronicle", "knowledge"],
        "onboarding": "Preserve and organize village knowledge",
        "value_metric": "Pages documented, guides created"
    },
    
    # ===== SPECIALIZED ROLES =====
    "EDUCATOR": {
        "title": "Educator / Trainer",
        "base_multiplier": 1.7,
        "sops": ["YOS_001", "PSY_001"],
        "capabilities": [
            "teach_skills",
            "onboard_members",
            "create_curriculum",
            "mentor_apprentices"
        ],
        "quest_tags": ["education", "training", "onboarding", "mentorship"],
        "onboarding": "Train new members and level up skills",
        "value_metric": "Students trained, skills transferred"
    },
    
    "HARDWARE_ENGINEER": {
        "title": "Hardware Engineer",
        "base_multiplier": 2.2,
        "sops": ["DEF_001", "MBD_001"],
        "capabilities": [
            "design_hardware",
            "build_sensors",
            "integrate_iot",
            "maintain_systems"
        ],
        "quest_tags": ["hardware", "iot", "sensors", "electronics"],
        "onboarding": "Build and maintain physical computing systems",
        "value_metric": "Devices built, sensors deployed"
    },
    
    "AI_STEWARD": {
        "title": "AI Steward / Automation Engineer",
        "base_multiplier": 2.3,
        "sops": ["ASG_001", "AUTO_001", "AUTO_002", "MULTI_AGENT"],
        "capabilities": [
            "build_workflows",
            "train_models",
            "optimize_automation",
            "coordinate_agents"
        ],
        "quest_tags": ["ai", "automation", "n8n", "workflows"],
        "onboarding": "Automate village operations with AI",
        "value_metric": "Workflows created, hours automated"
    },
    
    "FEDERATION_COORDINATOR": {
        "title": "Federation Coordinator",
        "base_multiplier": 1.9,
        "sops": ["ECP_001", "CRP_001", "NET_001"],
        "capabilities": [
            "manage_mesh",
            "coordinate_nodes",
            "facilitate_trade",
            "plan_mitosis"
        ],
        "quest_tags": ["federation", "networking", "mesh", "coordination"],
        "onboarding": "Connect villages in the global mesh",
        "value_metric": "Nodes connected, trades facilitated"
    },
    
    "ECONOMIST": {
        "title": "Village Economist",
        "base_multiplier": 2.0,
        "sops": ["ECONOMIC_MODEL", "TOKENOMICS", "FCP_001"],
        "capabilities": [
            "manage_treasury",
            "analyze_flows",
            "optimize_pricing",
            "plan_economy"
        ],
        "quest_tags": ["economy", "treasury", "tokenomics", "finance"],
        "onboarding": "Optimize village economic health",
        "value_metric": "AT velocity, treasury health",
        "requires_certification": True
    },
    
    "GHOST": {
        "title": "The Ghost / Pseudonymous Agent",
        "base_multiplier": 0.8, # Anonymity tax
        "sops": ["SEC_001"],
        "capabilities": [
            "anonymous_contribution",
            "private_research",
            "shielded_transactions"
        ],
        "quest_tags": ["security", "anonymity", "low-trust"],
        "onboarding": "Contribute from the shadows with high-audit verification",
        "value_metric": "Verified anonymous impact",
        "is_ghost": True
    },
    
    # ===== FOUNDERS NODE SPECIALIZED ROLES =====
    "FOUNDER": {
        "title": "Founder (The Lab)",
        "base_multiplier": 3.0,
        "sops": ["HK_001", "MBD_001"],
        "capabilities": [
            "access_hardware_lab",
            "access_media_studio",
            "submit_equity_milestone",
            "mint_high_output_labor"
        ],
        "quest_tags": ["startup", "equity", "milestone", "innovation"],
        "onboarding": "Build the future of decentralized civilization",
        "value_metric": "Key milestones reached"
    },
    
    "NODE_ADMIN": {
        "title": "Lab Administrator",
        "base_multiplier": 2.0,
        "sops": ["HK_001", "FCP_001"],
        "capabilities": [
            "manage_lab_access",
            "schedule_resources",
            "verify_startup_labor"
        ],
        "quest_tags": ["admin", "logistics", "scheduling"],
        "onboarding": "Ensure the high-bar environment remains optimized",
        "value_metric": "Resource utilization, user satisfaction"
    }
}


# Ghost Reputation Tiers
GHOST_TIERS = {
    "FULL_TRANSPARENT": {"trust": 1.0, "audit_level": "standard"},
    "SEMI_TRANSPARENT": {"trust": 0.6, "audit_level": "high"},
    "FULL_GHOST": {"trust": 0.1, "audit_level": "critical"}
}

# Role Progression Paths
ROLE_PROGRESSION = {
    "WORKER": ["BUILDER", "FARMER", "DEVELOPER", "CHRONICLER"],
    "BUILDER": ["HARDWARE_ENGINEER", "ENERGY_TECH"],
    "DEVELOPER": ["AI_STEWARD", "HARDWARE_ENGINEER"],
    "FARMER": ["HEARTH_KEEPER", "EDUCATOR"],
    "CHRONICLER": ["EDUCATOR", "ORACLE"]
}

# SOP-to-Role Mapping (Reverse Index)
SOP_OWNERSHIP = {
    "GAP_001": ["ORACLE", "FEDERATION_COORDINATOR"],
    "GAP_002": ["ENERGY_TECH", "FEDERATION_COORDINATOR"],
    "MBD_001": ["DEVELOPER", "BUILDER", "HARDWARE_ENGINEER"],
    "ECP_001": ["FEDERATION_COORDINATOR", "ORACLE"],
    "ECONOMIC_MODEL": ["ECONOMIST", "ORACLE"],
    "TOKENOMICS": ["ECONOMIST", "DEVELOPER"],
    "FCP_001": ["ECONOMIST"],
    "TNP_001": ["AI_STEWARD", "DEVELOPER"],
    "DEF_001": ["HARDWARE_ENGINEER", "ENERGY_TECH"],
    "NET_001": ["FEDERATION_COORDINATOR", "ENERGY_TECH"],
    "SEC_001": ["DEVELOPER", "ORACLE"],
    "SDP_001": ["CHRONICLER", "ORACLE"],
    "DATA_001": ["CHRONICLER", "DEVELOPER"],
    "FILE_TAXONOMY": ["DEVELOPER", "CHRONICLER"],
    "ASG_001": ["AI_STEWARD"],
    "AGENT_RULES": ["AI_STEWARD", "DEVELOPER"],
    "AUTO_001": ["AI_STEWARD"],
    "AUTO_002": ["AI_STEWARD"],
    "AUTO_003": ["AI_STEWARD", "DEVELOPER"],
    "MULTI_AGENT": ["AI_STEWARD"],
    "CRP_001": ["FEDERATION_COORDINATOR", "EDUCATOR"],
    "HK_001": ["HEARTH_KEEPER", "FARMER"],
    "MP_001": ["WORKER", "ORACLE"],
    "YOS_001": ["EDUCATOR", "HEARTH_KEEPER"],
    "PHILOSOPHY_001": ["ORACLE", "EDUCATOR"],
    "PSY_001": ["HEARTH_KEEPER", "ORACLE", "EDUCATOR"],
    "ROADMAP_001": ["ORACLE", "FEDERATION_COORDINATOR"]
}

def get_role_info(role_name):
    """Get full information about a role"""
    return ROLE_DEFINITIONS.get(role_name, ROLE_DEFINITIONS["WORKER"])

def get_roles_for_sop(sop_code):
    """Find which roles are responsible for implementing an SOP"""
    return SOP_OWNERSHIP.get(sop_code, [])

def get_progression_path(current_role):
    """Get available next roles for progression"""
    return ROLE_PROGRESSION.get(current_role, [])

def get_all_active_roles():
    """Get list of all roles that users can be assigned"""
    return list(ROLE_DEFINITIONS.keys())

def filter_quests_by_role(quests, user_roles):
    """Filter quests that match user's role capabilities"""
    matching = []
    user_tags = set()
    
    for role in user_roles:
        role_info = get_role_info(role)
        user_tags.update(role_info.get("quest_tags", []))
    
    for quest in quests:
        quest_tags = set(quest.get('tags', []))
        if quest_tags.intersection(user_tags):
            matching.append(quest)
    
    return matching
