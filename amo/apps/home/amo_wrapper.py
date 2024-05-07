import requests
from .models import Company


class AmoCRMWrapper:
    def __init__(self, company_id):
        company = Company.objects.get(pk=company_id)
        self.base_url = company.amo_base_url
        self.client_id = company.amo_client_id
        self.client_secret = company.amo_client_secret
        self.redirect_uri = company.amo_redirect_url
        self.access_token = company.amo_access_token
        self.refresh_token = company.amo_refresh_token

    def authenticate(self, code):
        auth_url = f"{self.base_url}/oauth2/access_token"
        auth_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        response = requests.post(auth_url, data=auth_data)
        if response.status_code == 200:
            auth_info = response.json()
            self.access_token = auth_info.get('access_token')
            self.refresh_token = auth_info.get('refresh_token')
            return True
        else:
            return False

    def get_contacts(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{self.base_url}/api/v4/contacts", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def create_contact(self, data):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.post(f"{self.base_url}/api/v4/contacts", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def update_contact(self, contact_id, data):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.patch(f"{self.base_url}/api/v4/contacts/{contact_id}", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def delete_contact(self, contact_id):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.delete(f"{self.base_url}/api/v4/contacts/{contact_id}", headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False

    def create_deal(self, data):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.post(f"{self.base_url}/api/v4/leads", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def update_deal(self, deal_id, data):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.patch(f"{self.base_url}/api/v4/leads/{deal_id}", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return None
