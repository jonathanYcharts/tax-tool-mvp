import re
from datetime import datetime

import re
from datetime import datetime

import re
from datetime import datetime

def parse_gbm_confirmation_text(text: str):
    transactions = []
    lines = text.splitlines()

    for i, line in enumerate(lines):
        line = line.strip()

        if re.search(r'\s+M\s+(Buy|Sell)\s+', line):
            try:
                line = re.sub(r'\s+M\s+(Buy|Sell)', r' \1', line)
                parts = line.split()
                symbol = parts[0]

                # Last fields (always in same order):
                capacity = parts[-1]
                settle_date = parse_date(parts[-2])
                trade_date = parse_date(parts[-3])
                price = float(parts[-4])
                quantity = float(parts[-5])
                execution_time = parts[-7] + " " + parts[-6]  # ← fix: combine HH:MM:SS + AM/PM
                action = parts[-8]

                # The rest is the security name (everything between symbol and action)
                security_name = " ".join(parts[1:-8])

                current = {
                    'symbol': symbol,
                    'security_name': security_name,
                    'action': action,
                    'execution_time': execution_time,
                    'quantity': quantity,
                    'price': price,
                    'trade_date': trade_date,
                    'settle_date': settle_date,
                    'capacity': capacity,
                    'commission': 0.0,
                    'transaction_fee': 0.0,
                    'other_fees': 0.0,
                    'net_amount': 0.0,
                }

                # Look ahead for fee lines
                for offset in range(1, 10):
                    if i + offset >= len(lines):
                        break
                    fee_line = lines[i + offset].strip()
                    if fee_line.startswith("Commission"):
                        current["commission"] = extract_dollar(fee_line)
                    elif fee_line.startswith("Transaction Fee"):
                        current["transaction_fee"] = extract_dollar(fee_line)
                    elif fee_line.startswith("Other Fees"):
                        current["other_fees"] = extract_dollar(fee_line)
                    elif fee_line.startswith("Net Amount"):
                        current["net_amount"] = extract_dollar(fee_line)
                        transactions.append(current)
                        break

            except Exception as e:
                print("Skipping line due to parse error:", line)
                print("Error:", e)
                continue

    return transactions


def extract_dollar(line):
    match = re.search(r'\$([\d,]+\.\d{2})', line)
    return float(match.group(1).replace(',', '')) if match else 0.0

def parse_date(val):
    try:
        return datetime.strptime(val.strip(), '%m/%d/%Y').date()
    except:
        return None
