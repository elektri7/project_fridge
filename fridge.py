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

add(goods, 'Пельмени Универсальные', 0.5, '2023-7-15')
add(goods, 'Пельмени Универсальные', 2, '2023-8-1')
add(goods, 'Вода', 1.5)
print(goods)    
    