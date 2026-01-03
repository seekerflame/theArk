import unittest
from unittest.mock import MagicMock, patch
import json
import time
from core.lightning_bridge import LightningBridge

class MockLedger:
    def __init__(self):
        self.blocks = []

    def add_block(self, b_type, data):
        self.blocks.append({"id": len(self.blocks) + 1, "type": b_type, "data": data})

class TestLightningBridge(unittest.TestCase):
    def setUp(self):
        self.bridge = LightningBridge("https://mock-node:8080")
        self.ledger = MockLedger()

    def test_get_quote(self):
        quote = self.bridge.get_quote(10)
        self.assertEqual(quote['at_amount'], 10)
        self.assertEqual(quote['sats'], 10000) # 1 AT = 1000 Sats
        self.assertEqual(quote['btc_amount'], 0.0001)

    @patch('core.lightning_bridge.requests.request')
    def test_create_invoice(self, mock_req):
        # Mock LND response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "payment_request": "lnbc123...",
            "r_hash": "YWJjMTIz" # base64 for 'abc123'
        }
        mock_req.return_value = mock_response

        result = self.bridge.create_invoice(5, "user1")

        self.assertIsNotNone(result)
        self.assertEqual(result['at_to_credit'], 5)
        self.assertEqual(result['sats_expected'], 5000)
        self.assertEqual(result['payment_hash'], "616263313233") # hex of 'abc123'

    @patch('core.lightning_bridge.requests.request')
    def test_execute_swap_settled_correct_amount(self, mock_req):
        # Mock LND check status response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "settled": True,
            "state": "SETTLED",
            "amt_paid_sat": 10000 # Paid 10000 sats
        }
        mock_req.return_value = mock_response

        # Execute
        # Client claims they want 10 AT.
        res = self.bridge.execute_swap("hash123", self.ledger, "user1", expected_amount=10)

        self.assertEqual(res['status'], "complete")
        self.assertEqual(res['at_minted'], 10.0) # 10000 / 1000 = 10
        self.assertEqual(len(self.ledger.blocks), 1)

    @patch('core.lightning_bridge.requests.request')
    def test_execute_swap_prevents_inflation_exploit(self, mock_req):
        """
        Test that if a user pays less than claimed, they only get what they paid for.
        """
        # Mock LND: User only paid 1000 sats (1 AT)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "settled": True,
            "state": "SETTLED",
            "amt_paid_sat": 1000 # ONLY 1000 SATS PAID
        }
        mock_req.return_value = mock_response

        # Execute
        # Client claims they want 1,000,000 AT (The Exploit)
        res = self.bridge.execute_swap("hash123", self.ledger, "user1", expected_amount=1000000)

        self.assertEqual(res['status'], "complete")
        self.assertEqual(res['at_minted'], 1.0) # Should be 1.0, NOT 1,000,000
        self.assertNotEqual(res['at_minted'], 1000000)
        self.assertEqual(self.ledger.blocks[0]['data']['amount'], 1.0)

    @patch('core.lightning_bridge.requests.request')
    def test_execute_swap_open(self, mock_req):
        # Mock LND check status response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "settled": False,
            "state": "OPEN"
        }
        mock_req.return_value = mock_response

        # Execute
        res = self.bridge.execute_swap("hash123", self.ledger, "user1", 10)

        self.assertEqual(res['status'], "OPEN")
        self.assertEqual(len(self.ledger.blocks), 0)

    @patch('core.lightning_bridge.requests.request')
    def test_double_spend_prevention(self, mock_req):
        # Add a processed block
        self.ledger.add_block("MINT_BTC", {"payment_hash": "hash_spent"})

        # Mock LND to return SETTLED
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "settled": True,
            "state": "SETTLED",
            "amt_paid_sat": 5000
        }
        mock_req.return_value = mock_response

        # Execute
        res = self.bridge.execute_swap("hash_spent", self.ledger, "user1", 5)

        self.assertEqual(res['status'], "already_processed")
        self.assertEqual(len(self.ledger.blocks), 1) # No new block added

if __name__ == '__main__':
    unittest.main()
