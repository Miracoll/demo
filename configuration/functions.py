import requests


def encryptClass(secret):
    new = int(secret) * 39
    return new

def unencryptClass(secret):
    new = int(secret) / 39
    return int(new)

def sendSMS(message,to):
    url = "https://app.smartsmssolutions.com/io/api/client/v1/sms/"

    payload={'token': '7pHQVZ1NY1LmG3piWKNdnlh7Mj30wBeUZ7jJupCOq3dyPr3H8W',
    'sender': 'SMHS',
    'to': str(to),
    'message': f'{message}',
    'type': 0,
    'routing': 3,}
    files=[

    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)

def sendMessage(message):
    msg = message.replace(' ','+')
    url = f'https://api.callmebot.com/whatsapp.php?phone=2349034210056&text={msg}&apikey=3426545'
    x = requests.post(url)

def telegramMessage(message):
    TOKEN = "8087178435:AAG7l0Yy4zzNbLNg82l-S8oyTxkoc5xMRvE"
    chat_id = ['1322959136']
    for i in chat_id:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={i}&text={message}"
        requests.get(url)
