# utils/generate_google_yaml.py

import os
from dotenv import load_dotenv

def gerar_google_ads_yaml():
    load_dotenv()
    content = f"""developer_token: "{os.getenv('GOOGLE_DEVELOPER_TOKEN')}"
client_id: "{os.getenv('GOOGLE_CLIENT_ID')}"
client_secret: "{os.getenv('GOOGLE_CLIENT_SECRET')}"
refresh_token: "{os.getenv('GOOGLE_REFRESH_TOKEN')}"
client_customer_id: "{os.getenv('GOOGLE_CUSTOMER_ID', '')}"
"""
    with open("google-ads.yaml", "w") as f:
        f.write(content)
