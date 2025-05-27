from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pdfplumber
import os
from .gbm_parser import parse_gbm_confirmation_text

@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('file'):
        pdf_file = request.FILES['file']
        with pdfplumber.open(pdf_file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        print('=== PDF TEXT START ===')
        print(text)
        print('=== PDF TEXT END ===')
        transactions = parse_gbm_confirmation_text(text)
        return JsonResponse({'transactions': transactions})

    return JsonResponse({'error': 'No file uploaded'}, status=400)
