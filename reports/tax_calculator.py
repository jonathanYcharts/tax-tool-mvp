from .models import GBMConfirmationTransaction, ExchangeRate
from collections import defaultdict
from datetime import datetime
from .utils import get_usd_to_mxn_rate


def get_usd_to_mxn_rate_cached(date: datetime.date) -> float:
    try:
        rate_obj = ExchangeRate.objects.get(date=date)
        return rate_obj.rate
    except ExchangeRate.DoesNotExist:
        rate = get_usd_to_mxn_rate(date)
        if rate is not None:
            ExchangeRate.objects.create(date=date, rate=rate)
        return rate

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

        # Build shadow copy of buy lots: (buy_tx, remaining_qty)
        buy_lots = [(tx, tx.quantity) for tx in buys]

        for sale in sales:
            remaining_qty = abs(sale.quantity)
            sale_fx = get_usd_to_mxn_rate_cached(sale.trade_date)
            sale_mxn = sale.net_amount * sale_fx

            gain_mxn = 0.0

            for i in range(len(buy_lots)):
                buy, available_qty = buy_lots[i]

                if available_qty == 0:
                    continue

                used_qty = min(remaining_qty, available_qty)
                buy_fx = get_usd_to_mxn_rate_cached(buy.trade_date)
                buy_unit_cost_mxn = (buy.net_amount / buy.quantity) * buy_fx
                buy_mxn = used_qty * buy_unit_cost_mxn

                portion_of_sale_mxn = sale_mxn * (used_qty / abs(sale.quantity))
                gain_mxn += portion_of_sale_mxn - buy_mxn

                # Update remaining qty in memory (not DB)
                buy_lots[i] = (buy, available_qty - used_qty)
                remaining_qty -= used_qty

                if remaining_qty <= 0:
                    break

            sale.capital_gain_mxn = round(gain_mxn, 2)
            sale.save()

            gains.append({
                "symbol": symbol,
                "trade_date": sale.trade_date,
                "gain_mxn": sale.capital_gain_mxn,
                "quantity": sale.quantity,
                "net_mxn": round(sale_mxn, 2)
            })

    return gains
