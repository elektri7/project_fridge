from datetime import datetime
from decimal import Decimal


goods = {}
DATE_FORMAT = '%Y-%m-%d'


def add(items, title, amount, expiration_date=None):
    if title not in items:
        items[title] = []
    parsed_date = None
    if expiration_date:
        parsed_date = datetime.strptime(expiration_date, DATE_FORMAT).date()
    batch = {'amount': Decimal(amount), 'expiration_date': parsed_date}
    items[title].append(batch)


def add_by_note(items, note):
    parts = note.strip().split()
    if len(parts[-1].split('-')) == 3:
        expiration_date = parts[-1]
        amount = Decimal(parts[-2])
        title = ' '.join(parts[:-2])
    else:
        expiration_date = None
        amount = Decimal(parts[-1])
        title = ' '.join(parts[:-1])
    add(goods, title, amount, expiration_date)


def find(items, needle):
    result = []
    for key in items:
        if needle.strip().lower() in key.lower():
            result.append(key)
    return result
