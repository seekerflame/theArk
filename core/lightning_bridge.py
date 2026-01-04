import requests
import json
import logging
import base64
import time
import os
from hashlib import sha256

logger = logging.getLogger("ArkOS.Lightning")

class LightningBridge:
    def __init__(self, node_url, macaroon_path=None, tls_cert_path=None):
        """
        Initialize connection to Lightning node (LND).

        Args:
            node_url (str): The REST API URL (e.g., https://localhost:8080)
            macaroon_path (str): Path to the admin.macaroon file
            tls_cert_path (str): Path to tls.cert (optional)
        """
        self.node_url = node_url.rstrip('/')
        self.macaroon = None
        self.tls_cert = tls_cert_path
        self.headers = {}

        # Load Macaroon
        self.mock_mode = False
        if macaroon_path == "mock" or os.environ.get('ARK_MOCK_EXCHANGE') == '1':
            self.mock_mode = True
            logger.info("LightningBridge starting in MOCK MODE")
        elif macaroon_path:
            try:
                with open(macaroon_path, 'rb') as f:
                    macaroon_bytes = f.read()
                    self.macaroon = macaroon_bytes.hex()
                    self.headers['Grpc-Metadata-macaroon'] = self.macaroon
            except Exception as e:
                logger.error(f"Failed to load macaroon: {e}")
                self.mock_mode = True
                logger.info("Falling back to MOCK MODE due to missing/invalid macaroon")

        # Fixed MVP Rate
        self.sats_per_at = 1000

    def _request(self, method, endpoint, data=None):
        """Internal helper for making HTTP requests to LND."""
        url = f"{self.node_url}{endpoint}"
        try:
            # If no TLS cert provided, we might be in dev mode or using a valid CA cert.
            # For self-signed LND without explicit cert path, we might need verify=False (insecure).
            verify = self.tls_cert if self.tls_cert else False

            response = requests.request(
                method,
                url,
                headers=self.headers,
                json=data,
                verify=verify,
                timeout=10
            )

            if response.status_code >= 400:
                logger.error(f"LND API Error {response.status_code}: {response.text}")
                return None

            return response.json()
        except Exception as e:
            logger.error(f"LND Request Failed: {e}")
            return None

    def get_info(self):
        """Check node status."""
        return self._request('GET', '/v1/getinfo')

    def get_quote(self, at_amount):
        """
        Return BTC equivalent for given AT amount.
        """
        sats = int(at_amount * self.sats_per_at)
        btc_amount = sats / 100_000_000

        return {
            "at_amount": at_amount,
            "btc_amount": btc_amount,
            "sats": sats,
            "rate": f"1 AT = {self.sats_per_at} sats",
            "expires_at": time.time() + 3600 # 1 hour expiry for quote
        }

    def create_invoice(self, at_amount, wallet_id):
        """
        Create Lightning invoice to receive BTC for AT.
        """
        quote = self.get_quote(at_amount)
        sats = quote['sats']

        payload = {
            "value": sats,
            "memo": f"Mint {at_amount} AT for {wallet_id}"
        }

        if self.mock_mode:
            # Generate a mock invoice
            return {
                "invoice": f"lnbc{sats}n1{sha256(str(time.time()).encode()).hexdigest()}",
                "payment_hash": sha256(str(time.time()).encode()).hexdigest(),
                "at_to_credit": at_amount,
                "sats_expected": sats,
                "mock": True
            }

        # LND Endpoint: POST /v1/invoices
        data = self._request('POST', '/v1/invoices', payload)

        if data and 'payment_request' in data:
            # R_hash is usually returned as base64 in LND REST response, but we might want hex for easier handling
            r_hash_b64 = data.get('r_hash', '')
            payment_hash = ''
            try:
                payment_hash = base64.b64decode(r_hash_b64).hex()
            except:
                pass

            return {
                "invoice": data['payment_request'],
                "payment_hash": payment_hash,
                "at_to_credit": at_amount,
                "sats_expected": sats
            }
        return None

    def check_invoice_status(self, payment_hash_hex):
        """
        Check if an invoice is settled.
        payment_hash_hex should be the hex string of the r_hash.
        Returns: (status_string, amount_paid_sats)
        """
        if not payment_hash_hex: return "UNKNOWN", 0

        if self.mock_mode:
            # In mock mode, we "confirm" after 5 seconds
            # For simplicity in manual UI test, we can just always return SETTLED
            # or use a small delay if we track timestamps, but "SETTLED" is fine for UI verification.
            return "SETTLED", 10000 # Mock amount

        data = self._request('GET', f'/v1/invoice/{payment_hash_hex}')

        if data:
            # LND State: OPEN=0, SETTLED=1, CANCELED=2, ACCEPTED=3
            state = data.get('state')
            settled = data.get('settled') # Boolean

            amt_paid = 0
            if 'amt_paid_sat' in data:
                amt_paid = int(data['amt_paid_sat'])

            if settled or state == "SETTLED" or state == 1:
                return "SETTLED", amt_paid
            elif state == "CANCELED" or state == 2:
                return "CANCELED", 0
            else:
                return "OPEN", 0
        return "UNKNOWN", 0

    def execute_swap(self, payment_hash_hex, ledger, user_id, expected_amount=None):
        """
        Verifies payment and mints AT if confirmed.
        Interact with the VillageLedger.

        Args:
            payment_hash_hex (str): The payment hash to check.
            ledger: The ledger instance.
            user_id: User receiving the tokens.
            expected_amount: (Optional) client claim of amount, ignored for actual minting logic in favor of proof.
        """
        status, paid_sats = self.check_invoice_status(payment_hash_hex)

        if status == "SETTLED":
            # Check if already processed to prevent double spend
            for block in ledger.blocks:
                if block['type'] == 'MINT_BTC' and block['data'].get('payment_hash') == payment_hash_hex:
                    return {"status": "already_processed", "tx_id": block['id']}

            # Calculate AT Amount from ACTUAL paid sats
            # 1 AT = 1000 Sats
            # So AT = Sats / 1000

            at_mint_amount = paid_sats / self.sats_per_at

            if at_mint_amount <= 0:
                 return {"status": "error", "message": "Zero amount paid"}

            # Mint AT
            mint_data = {
                "action": "MINT",
                "reason": "BTC_SWAP",
                "amount": at_mint_amount,
                "receiver": user_id,
                "payment_hash": payment_hash_hex,
                "sats_received": paid_sats,
                "provider": "LightningBridge"
            }

            # Add block to ledger
            ledger.add_block("MINT_BTC", mint_data)

            return {
                "status": "complete",
                "at_minted": at_mint_amount,
                "wallet_id": user_id,
                "tx_id": ledger.blocks[-1]['id'] if ledger.blocks else -1
            }

        return {"status": status}
