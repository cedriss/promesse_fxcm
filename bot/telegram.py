import requests


class TelegramBot:
    def __init__(self, bot_token, channel_id):
        self.bot_token = bot_token
        self.channel_id = channel_id

    def _parse_signal(self, signal):

        parsed_text = f'''
<b>Symbol:</b> <code>{signal['symbol']}</code>
<b>Direction:</b> <code>{signal['direction']}</code>
<b>Status:</b> <code>{signal['status']}</code>
<b>Create an Order ?:</b> <code>{signal['position']}</code>
<b>ATR (pips):</b> <code>{signal['atr']}</code>
<b>Datetime:</b> <code>{signal['datetime']}</code>
'''

        return parsed_text

    def send_text(self, message):
        message = self._parse_signal(message)
        send_text = f'https://api.telegram.org/bot{self.bot_token}/sendMessage?chat_id={self.channel_id}&text={message}&parse_mode=HTML'
        response = requests.get(send_text)

        return response.json()
