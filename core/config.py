import os
import json
import logging

logger = logging.getLogger("ArkOS.Config")

class Config:
    """
    Centralized configuration management.
    Reads from environment variables with fallback to a local .env file logic.
    """
    
    @staticmethod
    def get(key, default=None):
        return os.environ.get(key, default)

    @staticmethod
    def is_prod():
        return os.environ.get('ENVIRONMENT') == 'production'

    @staticmethod
    def get_mermaid_key():
        return os.environ.get('MERMAID_CHART_API_KEY')

    @staticmethod
    def get_jwt_secret():
        return os.environ.get('JWT_SECRET', 'dev_only_secret_change_in_production')

def load_env_file(path='.env'):
    """Simple parser for .env files to populate os.environ"""
    if not os.path.exists(path):
        return
    
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except Exception as e:
        logger.error(f"Failed to load .env file: {e}")

# Auto-load on import
load_env_file()
