import requests
from requests.auth import HTTPBasicAuth

# FINRA token endpoint
token_url = "https://api.finra.org/token"  # standard OAuth2 endpoint

# Your credentials
client_id = "c9b2371079914c4dbf63"
client_secret = "@Skibidi123456"

# Payload for client credentials grant
payload = {
    "grant_type": "client_credentials"
}

# Request access token
response = requests.post(token_url, data=payload, auth=HTTPBasicAuth(client_id, client_secret))

if response.status_code == 200:
    token_data = response.json()
    access_token = token_data.get("access_token")
    print("✅ Access token received:", access_token)
else:
    print("❌ Failed to get access token")
    print(response.status_code, response.text)
