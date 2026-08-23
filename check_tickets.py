import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
API_URL = "https://api.weezevent.com/ticket/widgets/resale-sephoria-london-2026?locale=en-gb"

def send_telegram_alert(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing Telegram credentials.")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

def check_tickets():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Trigger alert if the unavailable state changes
            if "unavailable" in content and "no tickets" not in content:
                alert_text = (
                    "🚨 *SEPHORiA London Ticket Alert!*\n\n"
                    "Resale availability detected on Weezevent.\n"
                    "Buy now: https://sites.weezevent.com/sephoria-london/"
                )
                send_telegram_alert(alert_text)
                print("Ticket availability detected! Alert sent.")
            else:
                print("Checked: No tickets available yet.")
        else:
            print(f"API returned status code: {response.status_code}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    check_tickets()
