from .models import GBMConfirmationTransaction
from collections import defaultdict
from datetime import datetime
import requests

BANXICO_API_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos"  # Fix later with token

def get_usd_to_mxn_rate(date: datetime.date) -> float:
    # Simulated fallback (you'll replace this with real Banxico API or your own cache)
    return 19.3  # Placeholder, we'll plug real API after

def calculate_capital_gains(year: int):
    buys_by_symbol = defaultdict(list)
    sales_by_symbol = defaultdict(list)

    transactions = GBMConfirmationTransaction.objects.filter(trade_date__year=year).order_by("trade_date")

    for tx in transactions:
        if tx.action == "Buy":
            buys_by_symbol[tx.symbol].append(tx)
        elif tx.action == "Sell":
            sales_by_symbol[tx.symbol].append(tx)

    gains = []

    for symbol, sales in sales_by_symbol.items():
        buys = buys_by_symbol[symbol]
        buy_index = 0

        for sale in sales:
            remaining_qty = sale.quantity
            sale_fx = get_usd_to_mxn_rate(sale.trade_date)
            sale_mxn = sale.net_amount * sale_fx

            gain_mxn = 0.0

            while remaining_qty > 0 and buy_index < len(buys):
                buy = buys[buy_index]
                if buy.quantity == 0:
                    buy_index += 1
                    continue

                used_qty = min(remaining_qty, buy.quantity)
                buy_fx = get_usd_to_mxn_rate(buy.trade_date)
                buy_mxn = (buy.net_amount / buy.quantity) * used_qty * buy_fx

                gain_mxn += sale_mxn * (used_qty / sale.quantity) - buy_mxn

                # update quantities
                remaining_qty -= used_qty
                buy.quantity -= used_qty

            gains.append({
                "symbol": symbol,
                "trade_date": sale.trade_date,
                "gain_mxn": round(gain_mxn, 2),
                "quantity": sale.quantity,
                "net_mxn": round(sale_mxn, 2)
            })

    return gains
