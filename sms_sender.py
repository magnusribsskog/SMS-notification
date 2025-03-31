import os
import logging
from datetime import datetime, timedelta, timezone  # Fixed timezone import
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient
from sms_client import SMSClient

# Initialize
load_dotenv()
logging.basicConfig(level=logging.INFO)

class SMSSender:
    def __init__(self):
        self.credential = ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )
        self.graph_client = GraphClient(
            credential=self.credential,
            scopes=['https://graph.microsoft.com/.default']
        )
        self.sms_client = SMSClient()

    def get_appointments(self):
        # Fixed UTC handling
        now = datetime.now(timezone.utc).isoformat()
        end = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        
        return self.graph_client.get(
            f"/solutions/bookingBusinesses/{os.getenv('BOOKINGS_BUSINESS_ID')}/appointments"
            f"?$filter=start/dateTime ge '{now}' and start/dateTime le '{end}'"
        ).json()

    def run(self):
        appointments = self.get_appointments()
        for appt in appointments.get('value', []):
            try:
                customer = appt['customers'][0]  # Fixed typo
                sms_number = customer.get('sms') or customer.get('phone')  # Fallback
                
                if not sms_number:
                    logging.error(f"No SMS number for {appt['id']}")
                    continue
                    
                if "SMS_SENT" not in appt.get('notes', ''):
                    self.sms_client.send_sms(
                        sms_number,
                        f"Påminnelse: kl {appt['startDateTime'][11:16]}"  # Removed serviceName
                    )
                    self.update_notes(appt)
            except KeyError as e:
                logging.error(f"Malformed appointment {appt.get('id')}: {str(e)}")
            except Exception as e:
                logging.error(f"General error for {appt.get('id')}: {str(e)}")

    def update_notes(self, appointment):
        updated_notes = f"{appointment.get('notes', '')}\nSMS_SENT_{datetime.now(timezone.utc).isoformat()}"
        self.graph_client.patch(
            f"/solutions/bookingBusinesses/{os.getenv('BOOKINGS_BUSINESS_ID')}/appointments/{appointment['id']}",
            json={"notes": updated_notes}
        )

if __name__ == "__main__":
    SMSSender().run()
