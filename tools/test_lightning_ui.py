import json
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock the environment for core.lightning_bridge
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from core.lightning_bridge import LightningBridge

class TestLightningUIIntegration(unittest.TestCase):
    def setUp(self):
        self.bridge = LightningBridge("https://localhost:8080", "mock.macaroon")
        self.bridge.headers = {'Grpc-Metadata-macaroon': 'mock_macaroon'}
        
    @patch('requests.request')
    def test_get_quote(self, mock_request):
        # Quote shouldn't even need a network call in the current implementation
        quote = self.bridge.get_quote(10)
        self.assertEqual(quote['at_amount'], 10)
        self.assertEqual(quote['sats'], 10000)
        
    @patch('requests.request')
    def test_create_invoice(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'payment_request': 'lnbc100u1...',
            'r_hash': 'YmFzZTY0cmhhc2g=' # "base64rhash"
        }
        mock_request.return_value = mock_response
        
        invoice_data = self.bridge.create_invoice(10, "test_user")
        self.assertIsNotNone(invoice_data)
        self.assertEqual(invoice_data['invoice'], 'lnbc100u1...')
        # payment_hash should be b64decode('YmFzZTY0cmhhc2g=').hex()
        # "base64rhash" in hex: 6261736536347268617368
        self.assertEqual(invoice_data['payment_hash'], '6261736536347268617368')

    @patch('requests.request')
    def test_check_invoice_status_settled(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'state': 'SETTLED',
            'settled': True,
            'amt_paid_sat': '10000'
        }
        mock_request.return_value = mock_response
        
        status, amt = self.bridge.check_invoice_status("hash")
        self.assertEqual(status, "SETTLED")
        self.assertEqual(amt, 10000)

    @patch('requests.request')
    def test_execute_swap(self, mock_request):
        # Mock status check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'state': 'SETTLED',
            'settled': True,
            'amt_paid_sat': '10000'
        }
        mock_request.return_value = mock_response
        
        # Mock ledger
        mock_ledger = MagicMock()
        mock_ledger.blocks = []
        
        result = self.bridge.execute_swap("new_hash", mock_ledger, "test_user", 10)
        
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['at_minted'], 10)
        mock_ledger.add_block.assert_called_once()
        
if __name__ == '__main__':
    unittest.main()
