import os
import unittest
from unittest.mock import patch, MagicMock  # Corrected import
from dotenv import load_dotenv
from sms_sender import SMSSender

class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()  # Load real .env
        
    def test_real_sms_delivery(self):
        """Integration test with real SMS (run manually)"""
        test_number = os.getenv("YOUR_TEST_NUMBER")  # Your .env number
        
        # Mock appointment data
        test_appointment = {
            "id": "TEST_ID",
            "startDateTime": "2024-02-20T14:30:00Z",
            "customers": [{"sms": test_number}],
            "notes": ""
        }
        
        # Mock GraphClient to return our test appointment
        with patch('sms_sender.GraphClient') as mock_graph:
            mock_graph.return_value.get.return_value.json.return_value = {
                "value": [test_appointment]
            }
            
            # Mock SMSClient to avoid real SMS sending
            with patch('sms_sender.SMSClient') as mock_sms:
                SMSSender().run()
                
                # Verify SMS would have been sent
                mock_sms.return_value.send_sms.assert_called_once_with(
                    test_number,
                    "Påminnelse: kl 14:30"
                )

if __name__ == "__main__":
    unittest.main()
