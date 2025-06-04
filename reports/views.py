import os
import pdfplumber
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.db.models import Count, Sum
from collections import defaultdict
from datetime import datetime

from .models import GBMConfirmationTransaction
from .gbm_parser import parse_gbm_confirmation_text
from .tax_calculator import calculate_capital_gains, get_usd_to_mxn_rate_cached

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
                if trade_date not in rates_cache:
                    rate = get_usd_to_mxn_rate_cached(trade_date)
                    rates_cache[trade_date] = rate
                else:
                    rate = rates_cache[trade_date]

                if rate is not None:
                    tx['mxn_amount'] = round(tx['net_amount'] * rate, 2)
                else:
                    print('Error retrieving the correct rate for', tx['symbol'])
                    tx['mxn_amount'] = None

                GBMConfirmationTransaction.objects.create(**tx)
            else:
                existing = GBMConfirmationTransaction.objects.get(
                    symbol=tx['symbol'],
                    execution_time=tx['execution_time'],
                    quantity=tx['quantity'],
                    price=tx['price'],
                    trade_date=trade_date,
                    action=tx['action']
                )
                print('====== OKAY GOT THE EXISTENT INSTANCES =========')
                if existing.mxn_amount is None:
                    print('yeap its none')
                    if trade_date not in rates_cache:
                        rate = get_usd_to_mxn_rate_cached(trade_date)
                        rates_cache[trade_date] = rate
                        print('rate does not exist!:', rate)
                    else:
                        rate = rates_cache[trade_date]
                        print('rate exists!:', rate)

                    if rate is not None:
                        existing.mxn_amount = round(tx['net_amount'] * rate, 2)
                        existing.save()

        return JsonResponse({'transactions': transactions})

    return JsonResponse({'error': 'No file uploaded'}, status=400)


def tax_summary_view(request):
    year = int(request.GET.get("year", datetime.now().year))
    results = calculate_capital_gains(year)
    return JsonResponse({"year": year, "capital_gains": results})

def tax_dashboard_view(request):
    selected_year = int(request.GET.get("year", datetime.now().year))

    # Calculate and set capital gains for sell instances before fetching
    if not GBMConfirmationTransaction.objects.filter(
        trade_date__year=selected_year,
        action="Sell",
        capital_gain_mxn__isnull=False,
    ).exists():
        print('Calculating capital gains!!! because we faound null values jiji')
        calculate_capital_gains(selected_year)

    if selected_year:
        transactions = GBMConfirmationTransaction.objects.filter(
            trade_date__year=selected_year
        ).order_by("-trade_date")
    else:
        transactions = GBMConfirmationTransaction.objects.all().order_by("-trade_date")

    grouped = defaultdict(lambda: {"Buy": [], "Sell": []})
    for tx in transactions:
        year = tx.trade_date.year if tx.trade_date else "Unknown"
        grouped[year][tx.action].append(tx)

    all_years = sorted({tx.trade_date.year for tx in GBMConfirmationTransaction.objects.all()})

    context = {
        "grouped_transactions": dict(grouped),
        "selected_year": int(selected_year) if selected_year else None,
        "all_years": all_years,
    }

    return render(request, "tax_dashboard.html", context)
