import os
import requests
from dotenv import load_dotenv

class SMSClient:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("LINK_MOBILITY_USERNAME")
        self.client_secret = os.getenv("LINK_MOBILITY_API_KEY")
        self.platformPartnerId = os.getenv("PLATFORM_PARTNER_ID")
        self.platformId = os.getenv("PLATFORM_ID")
        self.token_url = "https://n-eu.linkmobility.io/auth/token"
        self.sms_url = "https://n-eu.linkmobility.io/sms/send"
        self.access_token = self.get_access_token()

    def get_access_token(self):
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(self.token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            raise Exception(f"Failed to get token: {response.status_code}, {response.text}")

    def send_sms(self, phone, message):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "source": "Display_Name_For_the_SMS",
            "sourceTON": "ALPHANUMERIC",
            "destination": phone,
            "destinationTON": "MSISDN",
            "userData": message,
            "useDeliveryReport": False,  # Gates must be specified for logging
            "platformId": self.platformId,
            "platformPartnerId": self.platformPartnerId
        }
        response = requests.post(self.sms_url, json=payload, headers=headers)
        return response.status_code, response.text
