import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from sms_sender import SMSSender

class TestSMSSenderMinimal(unittest.TestCase):
    def setUp(self):
        self.mock_appointment = {
            "id": "AAMkAGM1...",
            "startDateTime": datetime.now(timezone.utc).isoformat(),
            "customers": [{
                "name": "Kari Nordman",
                "sms": "+4712345678"
            }],
            "notes": ""
        }

    def _mock_graph_get(self, appointments):
        mock_response = MagicMock()
        mock_response.json.return_value = {"value": appointments}
        return mock_response

    @patch('sms_sender.GraphClient')
    def test_sends_sms_when_no_notes_flag(self, mock_graph):
        """Test SMS sends when no SMS_SENT marker exists"""
        mock_graph.return_value.get.return_value = self._mock_graph_get([self.mock_appointment])
        mock_sms = MagicMock()
        
        with patch('sms_sender.SMSClient', return_value=mock_sms):
            SMSSender().run()
        
        mock_sms.send_sms.assert_called_once_with(
            "+4712345678",
            f"Påminnelse: kl {self.mock_appointment['startDateTime'][11:16]}"
        )

    @patch('sms_sender.GraphClient')
    def test_handles_missing_sms_field(self, mock_graph):
        """Test fallback to 'phone' if 'sms' is missing"""
        appt = self.mock_appointment.copy()
        appt["customers"][0] = {"phone": "+4798765432"}
        mock_graph.return_value.get.return_value = self._mock_graph_get([appt])
        
        mock_sms = MagicMock()
        with patch('sms_sender.SMSClient', return_value=mock_sms):
            SMSSender().run()
        
        mock_sms.send_sms.assert_called_once_with("+4798765432", unittest.mock.ANY)

    @patch('sms_sender.GraphClient')
    def test_updates_notes_after_sending(self, mock_graph):
        """Verify notes are updated with SMS_SENT timestamp"""
        mock_graph.return_value.get.return_value = self._mock_graph_get([self.mock_appointment])
        mock_patch = MagicMock()
        mock_graph.return_value.patch = mock_patch
        
        with patch('sms_sender.SMSClient'):
            SMSSender().run()
        
        # Extract the 'json' argument from the first call
        _, kwargs = mock_patch.call_args
        self.assertIn("SMS_SENT_", kwargs['json']['notes'])

if __name__ == "__main__":
    unittest.main()
