from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pdfplumber
import os
from datetime import datetime

from .models import GBMConfirmationTransaction
from .gbm_parser import parse_gbm_confirmation_text
from .tax_calculator import calculate_capital_gains
from .utils import get_usd_to_mxn_rate

@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('file'):
        pdf_file = request.FILES['file']
        with pdfplumber.open(pdf_file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'

        transactions = parse_gbm_confirmation_text(text)

        # Save transactions - Avoid duplicate instances
        rates_cache = {}
        for tx in transactions:
            trade_date = tx['trade_date']
            exists = GBMConfirmationTransaction.objects.filter(
                symbol=tx['symbol'],
                execution_time=tx['execution_time'],
                quantity=tx['quantity'],
                price=tx['price'],
                trade_date=trade_date,
                action=tx['action']
            ).exists()

            if not exists:
                # Save rates in cache if already fetched
                if trade_date not in rates_cache:
                    rates_cache[trade_date] = get_usd_to_mxn_rate(trade_date)

                rate = rates_cache[trade_date]
                if rate is not None:
                    tx['mxn_amount'] = round(tx['net_amount'] * rate, 2)
                else:
                    print('Error retrieving the correct rate for', tx['symbol'])
                    tx['mxn_amount'] = None

                GBMConfirmationTransaction.objects.create(**tx)
        return JsonResponse({'transactions': transactions})

    return JsonResponse({'error': 'No file uploaded'}, status=400)


def tax_summary_view(request):
    year = int(request.GET.get("year", datetime.now().year))
    results = calculate_capital_gains(year)
    return JsonResponse({"year": year, "capital_gains": results})

