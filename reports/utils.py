import requests
from datetime import datetime

BANXICO_SERIES_ID = "SF43718"  # FIX exchange rate
BANXICO_TOKEN = "f3febce729e3f0681314eed48d454a8097e469538c400b84f7558e08bbf815dc"

def get_usd_to_mxn_rate(trade_date: datetime.date) -> float:
    formatted_date = trade_date.strftime('%Y-%m-%d')
    url = (
        f'https://www.banxico.org.mx/SieAPIRest/service/v1/series/'
        f'{BANXICO_SERIES_ID}/datos/{formatted_date}/{formatted_date}?mediaType=json'
    )

    headers = {
        'Bmx-Token': BANXICO_TOKEN
    }

    response = requests.get(url, headers=headers)
    try:
        data = response.json()
        return float(data['bmx']['series'][0]['datos'][0]['dato'])
    except Exception as e:
        print(f"[Banxico ERROR] Could not fetch rate for {formatted_date}:", e)
        return None
