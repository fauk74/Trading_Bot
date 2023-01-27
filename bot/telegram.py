
import requests

TOKEN= "5971931671:AAGUBXtAlFm4RJV0tXr8qMvIECRtOAYsWto"
chat_id="2029160776"


def send_message(message):


    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    try:
        requests.get(url).json()
    except:
        print("Error in sending Telegram")