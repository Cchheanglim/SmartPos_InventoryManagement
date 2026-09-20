"""
Sends notification messages to a Telegram chat via a bot.

Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from app config (set via
environment variables — see README). If either is missing, every method
here silently no-ops instead of raising, so the rest of the app works
normally before a bot has been created.

To set one up later: message @BotFather on Telegram, run /newbot, copy the
token it gives you into TELEGRAM_BOT_TOKEN. Add the bot to your group/
channel, then get the chat ID (e.g. via @userinfobot or the getUpdates API)
and set TELEGRAM_CHAT_ID.
"""
import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)


class TelegramService:
    def _config(self):
        token = current_app.config.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = current_app.config.get("TELEGRAM_CHAT_ID", "")
        return token, chat_id

    def is_configured(self):
        token, chat_id = self._config()
        return bool(token) and bool(chat_id)

    def send_message(self, text):
        if not self.is_configured():
            logger.info("Telegram not configured yet — skipping notification: %s", text)
            return False
        token, chat_id = self._config()
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code != 200:
                logger.warning("Telegram API error: %s", response.text)
                return False
            return True
        except requests.RequestException as e:
            logger.warning("Telegram send failed: %s", e)
            return False

    @staticmethod
    def _escape(value):
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def notify_new_transaction(self, sale_id, total_amount, item_summary, cashier_name):
        message = (
            "🧾 <b>NEW TRANSACTION</b>\n\n"
            f"🆔 <b>Receipt:</b> #{self._escape(sale_id)}\n"
            f"💵 <b>Total:</b> ${self._escape(f'{total_amount:.2f}')}\n"
            f"🛒 <b>Items:</b> {self._escape(item_summary)}\n"
            f"👤 <b>Cashier:</b> {self._escape(cashier_name)}"
        )
        self.send_message(message)

    def notify_low_stock(self, product_name, current_stock, reorder_qty, supplier_name, supplier_contact):
        message = (
            "⚠️ <b>LOW STOCK ALERT</b>\n\n"
            f"📦 <b>Product:</b> {self._escape(product_name)}\n"
            f"📉 <b>Current Stock:</b> {self._escape(current_stock)}\n"
            f"🔄 <b>Suggested Reorder:</b> {self._escape(reorder_qty)}\n"
            f"🏭 <b>Supplier:</b> {self._escape(supplier_name or 'N/A')}\n"
            f"📞 <b>Contact:</b> {self._escape(supplier_contact or 'N/A')}"
        )
        self.send_message(message)

    def notify_password_reset(self, user_name, reset_url, expires_minutes):
        message = (
            "🔑 <b>PASSWORD RESET REQUESTED</b>\n\n"
            f"👤 <b>Account:</b> {self._escape(user_name)}\n"
            f"🔗 <b>Link:</b> {self._escape(reset_url)}\n"
            f"⏱ <b>Expires in:</b> {self._escape(expires_minutes)} minutes\n\n"
            "If you didn't request this, ignore this message — your password won't change."
        )
        self.send_message(message)

    def notify_refund(self, sale_id, refund_amount, item_summary, reason=None):
        message = (
            "↩️ <b>REFUND PROCESSED</b>\n\n"
            f"🆔 <b>Sale:</b> #{self._escape(sale_id)}\n"
            f"💵 <b>Refunded:</b> ${self._escape(f'{refund_amount:.2f}')}\n"
            f"🛒 <b>Items:</b> {self._escape(item_summary)}\n"
            f"📝 <b>Reason:</b> {self._escape(reason or 'Not specified')}"
        )
        self.send_message(message)

    def notify_restock(self, product_name, added_qty, staff_name):
        message = (
            "📥 <b>INVENTORY RESTOCKED</b>\n\n"
            f"📦 <b>Product:</b> {self._escape(product_name)}\n"
            f"➕ <b>Quantity Added:</b> {self._escape(added_qty)}\n"
            f"👤 <b>By:</b> {self._escape(staff_name)}"
        )
        self.send_message(message)

    def notify_purchase_order(self, product_name, quantity, supplier_name, staff_name):
        message = (
            "📝 <b>PURCHASE ORDER CREATED</b>\n\n"
            f"📦 <b>Product:</b> {self._escape(product_name)}\n"
            f"🔢 <b>Quantity Ordered:</b> {self._escape(quantity)}\n"
            f"🏭 <b>Supplier:</b> {self._escape(supplier_name or 'N/A')}\n"
            f"👤 <b>Ordered by:</b> {self._escape(staff_name)}"
        )
        self.send_message(message)
