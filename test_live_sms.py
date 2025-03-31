import os
import unittest
from unittest.mock import patch
from dotenv import load_dotenv
from sms_sender import SMSSender

class TestLiveSMS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
        if not os.getenv("YOUR_TEST_NUMBER"):
            raise unittest.SkipTest("No test number configured")
            
    @unittest.skipUnless(
        os.getenv("LIVE_SMS_TEST") == "true", 
        "Live SMS tests disabled"
    )
    def test_real_sms_delivery(self):
        """ACTUAL SMS SENDING (use sparingly)"""
        test_number = os.getenv("YOUR_TEST_NUMBER")
        
        with patch('sms_sender.GraphClient') as mock_graph:
            # Mock Graph API response
            mock_graph.return_value.get.return_value.json.return_value = {
                "value": [{
                    "id": "TEST_ID",
                    "startDateTime": "2024-02-20T14:30:00Z",
                    "customers": [{"sms": test_number}],
                    "notes": ""
                }]
            }
            
            # REAL SMS SENDING
            result = SMSSender().run()
            
            # Simple verification (check your phone!)
            self.assertIsNone(result)  # Or your success condition
