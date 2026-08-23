import os
import threading
import time
import requests
import telebot

# Load environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
API_URL = (
    "https://api.weezevent.com/ticket/widgets/resale-sephoria-london-2026?locale=en-gb"
)

bot = telebot.TeleBot(BOT_TOKEN)


def check_availability():
  headers = {"User-Agent": "Mozilla/5.0"}
  try:
    response = requests.get(API_URL, headers=headers, timeout=10)
    payload = response.json()

    # Traverse JSON structure safely
    first_step = payload.get("first_step", {})
    data_node = first_step.get("data", {})
    market_rates = data_node.get("ticket-market-rates", {})

    rates = market_rates.get("rates", [])
    event_info = market_rates.get("event", {})
    on_resale = event_info.get("on_resale", False)

    # Triggers if rates array becomes populated OR on_resale flag turns True
    if len(rates) > 0 or on_resale is True:
      return (
          True,
          "🚨 *SEPHORiA Ticket Alert!*\n\nTickets might be available!\nBuy"
          " here: https://sites.weezevent.com/sephoria-london/",
      )
    else:
      return False, "Checked: No tickets available yet."

  except Exception as e:
    return False, f"Error checking API: {e}"


# Command Handler for /check in Telegram
@bot.message_handler(commands=["check", "start"])
def handle_manual_check(message):
  print(f"Received /{message.text} command from Telegram")
  bot.reply_to(message, "🔍 Checking Weezevent API now...")
  is_available, status_msg = check_availability()
  bot.send_message(message.chat.id, status_msg, parse_mode="Markdown")


def auto_checker_loop():
  while True:
    is_available, status_msg = check_availability()
    print(f"Auto-check result: {status_msg}")

    if is_available:
      try:
        bot.send_message(CHAT_ID, status_msg, parse_mode="Markdown")
        print("Alert notification sent to Telegram!")
      except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

      # Pause for 30 mins after finding a ticket so it doesn't spam you
      time.sleep(1800)
    else:
      # Wait 5 minutes between checks
      time.sleep(300)


if __name__ == "__main__":
  print("Testing Telegram connection...")

  # 1. Send an immediate test message on startup
  try:
    bot.send_message(
        CHAT_ID,
        "🤖 *SEPHORiA Ticket Monitor is online!*\nUse /check anytime to test"
        " status.",
        parse_mode="Markdown",
    )
    print("Startup test message successfully sent to Telegram!")
  except Exception as e:
    print(
        f"ERROR: Could not send startup message. Check BOT_TOKEN and CHAT_ID."
        f" Details: {e}"
    )

  # 2. Start automated checking in background
  threading.Thread(target=auto_checker_loop, daemon=True).start()

  # 3. Start listening for incoming /check commands from Telegram
  print("Bot is listening for commands...")
  bot.infinity_polling()
