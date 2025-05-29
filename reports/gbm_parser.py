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
        parts = line.split()

        # Look for 'Buy' or 'Sell' in the parts
        if "Buy" in parts or "Sell" in parts:
            try:
                action_index = parts.index("Buy") if "Buy" in parts else parts.index("Sell")
                symbol = parts[0]
                action = parts[action_index]
                execution_time = parts[action_index + 1] + " " + parts[action_index + 2]
                quantity = float(parts[action_index + 3])
                price = float(parts[action_index + 4])
                trade_date = parse_date(parts[action_index + 5])
                settle_date = parse_date(parts[action_index + 6])
                capacity = " ".join(parts[action_index + 7:])  # e.g. 'Principal' or 'Riskless Principal'
                security_name = " ".join(parts[1:action_index])  # everything between symbol and action

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
