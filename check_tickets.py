import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
API_URL = "https://api.weezevent.com/ticket/widgets/resale-sephoria-london-2026?locale=en-gb"

def send_telegram_alert(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables.")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        print("Telegram alert sent successfully!")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def check_tickets():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        payload = response.json()
        
        # Safely extract ticket availability parameters
        first_step = payload.get("first_step", {})
        data_node = first_step.get("data", {})
        market_rates = data_node.get("ticket-market-rates", {})
        
        rates = market_rates.get("rates", [])
        event_info = market_rates.get("event", {})
        on_resale = event_info.get("on_resale", False)
        
        # Trigger condition: rates list is populated or resale flag turns True
        if len(rates) > 0 or on_resale is True:
            alert_text = (
                "🚨 *SEPHORiA London Ticket Alert!*\n\n"
                "Resale ticket availability detected on Weezevent!\n"
                "Buy now: https://sites.weezevent.com/sephoria-london/"
            )
            send_telegram_alert(alert_text)
            print("Ticket detected! Alert sent.")
        else:
            print("Checked: No tickets available yet.")
            
    except Exception as e:
        print(f"Error checking API: {e}")

if __name__ == "__main__":
    check_tickets()
