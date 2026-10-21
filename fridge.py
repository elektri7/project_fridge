from datetime import date, datetime, timedelta
from decimal import Decimal

goods = {}
DATE_FORMAT = "%Y-%m-%d"


def add(items, title, amount, expiration_date=None):
    if title not in items:
        items[title] = []
    parsed_date = None
    if expiration_date:
        parsed_date = datetime.strptime(expiration_date, DATE_FORMAT).date()
    batch = {"amount": Decimal(amount), "expiration_date": parsed_date}
    items[title].append(batch)


def add_by_note(items, note):
    parts = note.strip().split()
    if len(parts[-1].split("-")) == 3:
        expiration_date = parts[-1]
        amount = Decimal(parts[-2])
        title = " ".join(parts[:-2])
    else:
        expiration_date = None
        amount = Decimal(parts[-1])
        title = " ".join(parts[:-1])
    add(items, title, amount, expiration_date)


def find(items, needle):
    result = []
    for key in items:
        if needle.strip().lower() in key.lower():
            result.append(key)
    return result


def get_amount(items, needle):
    product_amount = Decimal(0)
    for title in find(items, needle):
        for batch in items[title]:
            if "amount" in batch:
                product_amount += batch["amount"]
    return product_amount


def get_expired(items, in_advance_days=0):
    result = []
    today = date.today()
    threshold = today + timedelta(days=in_advance_days)
    for title, batches in items.items():
        amount = Decimal(0)
        for batch in batches:
            exp_date = batch.get("expiration_date")
            if exp_date is None:
                continue
            if threshold >= exp_date:
                amount += batch.get("amount", Decimal(0))
        if amount > 0:
            result.append((title, amount))
    return result
