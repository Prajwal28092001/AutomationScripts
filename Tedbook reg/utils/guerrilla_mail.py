import requests
import time
import re

class GuerrillaMailClient:
    BASE_URL = "http://api.guerrillamail.com/ajax.php"

    def __init__(self):
        self.session = requests.Session()
        self.sid_token = ""
        self.email_addr = ""

    def get_email_address(self):
        """Generates and returns a random temporary email from GuerrillaMail."""
        params = {"f": "get_email_address"}
        response = self.session.get(self.BASE_URL, params=params)
        data = response.json()
        self.sid_token = data.get("sid_token")
        self.email_addr = data.get("email_addr")
        return self.email_addr

    def wait_for_pin_email(self, timeout_seconds=120):
        """Polls the inbox until an email arrives, then extracts and returns the 4-digit PIN."""
        start_time = time.time()
        print(f"Waiting up to {timeout_seconds}s for PIN email at {self.email_addr}...")
        
        while time.time() - start_time < timeout_seconds:
            time.sleep(5)
            params = {
                "f": "get_email_list",
                "offset": 0,
                "sid_token": self.sid_token
            }
            try:
                response = self.session.get(self.BASE_URL, params=params)
                data = response.json()
            except Exception as e:
                print("Error checking inbox:", e)
                continue
                
            if "list" in data and len(data["list"]) > 0:
                for mail in data["list"]:
                    # Ignore the default welcome email that Guerrilla places in every new inbox
                    if mail.get("mail_from") != "no-reply@guerrillamail.com":
                        mail_id = mail["mail_id"]
                        return self._fetch_and_extract_pin(mail_id)
                        
        raise Exception("Timed out waiting for PIN email from GuerrillaMail.")

    def _fetch_and_extract_pin(self, mail_id):
        """Fetches the specific email by ID and regex extracts the PIN."""
        params = {
            "f": "fetch_email",
            "email_id": mail_id,
            "sid_token": self.sid_token
        }
        response = self.session.get(self.BASE_URL, params=params)
        body = response.json().get("mail_body", "")
        
        # Look for exactly 4 digits. If your PIN is different length (like 6), change to \d{6}
        pin_match = re.search(r'\b\d{4}\b', body)
        if pin_match:
            pin = pin_match.group(0)
            print(f"Successfully extracted PIN: {pin}")
            return pin
        else:
            print("Full email body:\n", body)
            raise Exception("Successfully found email but couldn't find a 4-digit PIN inside it.")
