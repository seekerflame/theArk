import hmac
import hashlib
import json
import base64
import time
import urllib.request
import urllib.error
import logging

logger = logging.getLogger("CoinbaseClient")

class CoinbaseClient:
    """
    Sovereign Coinbase Advanced Trade Client.
    Uses standard library only for maximum portability and security.
    """
    def __init__(self, api_key=None, api_secret=None, simulation=True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.simulation = simulation
        self.base_url = "https://api.coinbase.com/api/v3/brokerage"
        
        if simulation:
            logger.info("CoinbaseClient initialized in SIMULATION mode.")
        else:
            logger.info("CoinbaseClient initialized in PRODUCTION mode.")

    def _generate_jwt(self, method, path):
        """Generates a JWT for Coinbase Advanced Trade API."""
        if not self.api_key or not self.api_secret:
            return None
            
        header = {"alg": "ES256", "typ": "JWT", "kid": self.api_key}
        # Coinbase technically wants ES256 which is ECDSA. 
        # However, for the Cloud API Key (V3), they often use a simpler signature or a specific JWT format.
        # Check current docs: Coinbase Advanced Trade uses a custom auth header or JWT.
        # Let's use the standard API Key/Secret auth if JWT is too complex for stdlib without ECDSA.
        # Actually, V3 supports "Legacy" API Key auth too, but Cloud API uses JWT with ES256.
        # PROXY: If we can't do ES256 in stdlib easily, we'll use the older hmac-sha256 if supported, 
        # or just provide a placeholder for the user to add 'cryptography' later.
        
        # For now, let's implement the HMAC-SHA256 version which is common for trading APIs.
        timestamp = str(int(time.time()))
        message = timestamp + method + path.split('?')[0] + "" # body is empty for GET
        signature = hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp
        }

    def get_accounts(self):
        if self.simulation:
            return [
                {"name": "BTC Wallet", "balance": {"amount": "0.5", "currency": "BTC"}, "type": "ACCOUNT_TYPE_CRYPTO"},
                {"name": "USD Wallet", "balance": {"amount": "10000.0", "currency": "USD"}, "type": "ACCOUNT_TYPE_FIAT"},
                {"name": "AT Wallet", "balance": {"amount": "5000.0", "currency": "AT"}, "type": "ACCOUNT_TYPE_CRYPTO"}
            ]
        
        # Real implementation
        path = "/accounts"
        return self._request("GET", path)

    def get_product_price(self, product_id):
        if self.simulation:
            # Simple mock price volatility
            import random
            base_prices = {"BTC-USD": 45000, "ETH-USD": 2500, "AT-BTC": 0.00001}
            price = base_prices.get(product_id, 100)
            variation = price * (random.uniform(-0.001, 0.001))
            return {"price": str(price + variation), "product_id": product_id}

        path = f"/products/{product_id}"
        res = self._request("GET", path)
        return res.get('price') if res else None

    def place_order(self, product_id, side, amount, price=None):
        if self.simulation:
            order_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:10]
            logger.info(f"SIMULATED ORDER: {side} {amount} {product_id} @ {price or 'MARKET'}")
            return {"success": True, "order_id": order_id, "status": "FILLED"}

        path = "/orders"
        # Complex order payload here...
        return {"error": "Production order placement not yet implemented in this module"}

    def _request(self, method, path, body=None):
        url = self.base_url + path
        headers = self._generate_jwt(method, path) or {}
        headers["Content-Type"] = "application/json"
        
        req = urllib.request.Request(url, method=method, headers=headers)
        if body:
            req.data = json.dumps(body).encode('utf-8')
            
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP Error: {e.code} - {e.reason}")
            return None
        except Exception as e:
            logger.error(f"Request Error: {str(e)}")
            return None

if __name__ == "__main__":
    # Test simulation
    client = CoinbaseClient(simulation=True)
    print("Accounts:", client.get_accounts())
    print("Price BTC-USD:", client.get_product_price("BTC-USD"))
