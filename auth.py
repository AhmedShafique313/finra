import requests
from requests.auth import HTTPBasicAuth

# Correct FIP OAuth token endpoint
token_url = "https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token?grant_type=client_credentials"

# Your credentials
client_id = "fake"
client_secret = "fake"

response = requests.post(token_url, auth=HTTPBasicAuth(client_id, client_secret))

if response.status_code == 200:
    token_data = response.json()
    access_token = token_data["access_token"]
    print("✅ Access Token:", access_token)
else:
    print("❌ Failed to get token")
    print(response.status_code, response.text)
