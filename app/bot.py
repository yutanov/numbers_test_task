import logging
import requests
import config

CHAT_ID = config.settings.chat_id
TOKEN = config.settings.token

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def send_notice(date, order_n):
    '''
    Отправка сообщения об истечении срока доставки заказа
    '''
    try:
        text = f"Срок доставки заказа № {order_n} истек {date}"
        send_text = "https://api.telegram.org/bot" + TOKEN + "/sendMessage?chat_id=" + CHAT_ID + "&text=" + text
        requests.get(send_text)

    except Exception as e:
        print(e.args)

    return
