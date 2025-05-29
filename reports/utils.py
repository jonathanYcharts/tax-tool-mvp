# reports/utils.py
import requests
from datetime import datetime

def get_usd_to_mxn_rate(trade_date: datetime.date):
    formatted_date = trade_date.strftime('%Y-%m-%d')
    series_id = 'SF43718'  # Tipo de cambio FIX
    url = f'https://www.banxico.org.mx/SieAPIRest/service/v1/series/{series_id}/datos/{formatted_date}/{formatted_date}?mediaType=json'

    headers = {
        'Bmx-Token': 'YOUR_BANXICO_API_KEY'
    }

    response = requests.get(url, headers=headers)
    try:
        data = response.json()
        return float(data['bmx']['series'][0]['datos'][0]['dato'])
    except:
        return None
