import datetime
import os
import time
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
API_URL = (
    "https://api.weezevent.com/ticket/widgets/resale-sephoria-london-2026?locale=en-gb"
)


def send_telegram_alert(message):
  if not BOT_TOKEN or not CHAT_ID:
    print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID credentials.")
    return

  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {
      "chat_id": CHAT_ID,
      "text": message,
      "parse_mode": "Markdown",
      "disable_web_page_preview": False,
  }

  try:
    res = requests.post(url, json=payload, timeout=10)
    res.raise_for_status()
    print("Telegram alert sent successfully!")
  except Exception as e:
    print(f"Failed to send Telegram message: {e}")


def check_tickets():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  try:
    response = requests.get(API_URL, headers=headers, timeout=15)

    # Print request details and raw response snippet for every check
    print(f"[{timestamp}] Request URL: {API_URL}")
    print(f"[{timestamp}] Status Code: {response.status_code}")
    print(f"[{timestamp}] Raw Output: {response.text[:250]}...")

    response.raise_for_status()
    payload = response.json()

    # Traverse JSON structure safely
    first_step = payload.get("first_step", {})
    data_node = first_step.get("data", {})
    market_rates = data_node.get("ticket-market-rates", {})

    rates = market_rates.get("rates", [])
    event_info = market_rates.get("event", {})
    on_resale = event_info.get("on_resale", False)

    # Trigger condition: rates list is populated OR resale flag turns True
    if len(rates) > 0 or on_resale is True:
      alert_text = (
          "🚨 *SEPHORiA London Ticket Alert!*\n\n"
          "Resale ticket availability detected on Weezevent!\n"
          "Buy now: https://sites.weezevent.com/sephoria-london/"
      )
      send_telegram_alert(alert_text)
      print(f"[{timestamp}] Ticket detected! Alert sent.")
      return True
    else:
      print(
          f"[{timestamp}] Check complete: No tickets available yet (rates:"
          f" {len(rates)}, on_resale: {on_resale}).\n"
      )
      return False

  except Exception as e:
    print(f"[{timestamp}] Error checking API: {e}\n")
    return False


def run_loop(duration_minutes=60, check_interval_seconds=30):
  """Runs continuous checks for a given duration."""
  start_time = time.time()
  end_time = start_time + (duration_minutes * 60)

  print(
      f"Starting check loop for {duration_minutes} minutes (checking every"
      f" {check_interval_seconds}s)...\n"
  )

  while time.time() < end_time:
    ticket_found = check_tickets()
    if ticket_found:
      # Sleep for 10 minutes if a ticket is detected to avoid spamming alerts
      time.sleep(600)
    else:
      time.sleep(check_interval_seconds)


if __name__ == "__main__":
  # Run loop for 50 minutes, polling every 30 seconds
  run_loop(duration_minutes=50, check_interval_seconds=30)
