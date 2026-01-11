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
    def get_jwt_key():
        key = os.environ.get('JWT_TOKEN_KEY', 'dev_only_key_change_in_production')
        if Config.is_prod() and key == 'dev_only_key_change_in_production':
            logger.critical("🚨 PRODUCTION SECURITY BREACH: Using default JWT_KEY!")
            raise RuntimeError("Cannot start production server with default JWT_KEY")
        return key

def load_env_file(path='.env'):
    """Simple parser for .env files to populate os.environ"""
    # Try current dir then parent dir
    if not os.path.exists(path):
        alt_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(alt_path):
            path = alt_path
        else:
            return
    
    try:
        with open(path, 'r') as f:
            logger.info(f"💡 Loading config from {os.path.abspath(path)}")
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Don't overwrite existing env vars
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()
    except Exception as e:
        logger.error(f"Failed to load .env file: {e}")

# Auto-load on import
load_env_file()
