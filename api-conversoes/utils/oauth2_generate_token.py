import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

# 🔄 Carrega variáveis do .env
load_dotenv()

client_config = {
    "installed": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
    }
}

# Escopo para acesso à Google Ads API
scopes = ["https://www.googleapis.com/auth/adwords"]

# Inicia autenticação com porta 8080
flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)
creds = flow.run_local_server(port=8080)

print("\n✅ ACCESS TOKEN:", creds.token)
print("🔁 REFRESH TOKEN:", creds.refresh_token)
print("⏳ EXPIRA EM:", creds.expiry)
