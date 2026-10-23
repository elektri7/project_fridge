"""Модуль для учёта товаров в холодильнике.

Содержит функции:
- add: добавляет партию товара в словарь.
- add_by_note: парсит текстовую заметку и вызывает add.
"""

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

goods = {}
DATE_FORMAT = "%Y-%m-%d"


def add(items, title, amount, expiration_date=None):
    """Добавляет партию товара в словарь холодильника.

    Функция добавляет новую партию (количество и срок годности)
    для указанного товара.
    Если товара ещё нет в словаре, создаётся пустой список,
    затем в него добавляется партия.

    Args:
        items (dict): Словарь товаров, где ключ — название товара,
        значение — список партий.
        title (str): Название товара.
        amount (int | float | str | Decimal): Количество товара.
        Будет приведено к Decimal.
        expiration_date (str | date | None): Дата истечения срока годности.
        Если строка — ожидается формат 'YYYY-MM-DD'.
        Если None — срок не ограничен.

    Returns:
        None: Функция изменяет словарь items на месте.
    """
    # Гарантируем, что для товара есть список партий.
    batches = items.setdefault(title, [])
    # Приводим amount к Decimal
    amount_decimal = Decimal(str(amount))
    # Нормализуем дату: если строка - парсим, если date - оставляем как есть,
    # если None - оставляем None.
    parsed_date = None
    if expiration_date is not None:
        if isinstance(expiration_date, date):
            parsed_date = expiration_date
        elif isinstance(expiration_date, str):
            # Ожидаем формат YYYY-MM-DD
            try:
                parsed_date = date.fromisoformat(expiration_date)
            except ValueError as err:
                raise ValueError(
                    f'Неверный формат даты: "{expiration_date}". '
                    'Используйте YYYY-MM-DD') from err
        else:
            raise TypeError(
                'expiration_date должен быть строкой (YYYY-MM-DD), '
                'объектом date или None.')
    batches.append({"amount": amount_decimal, "expiration_date": parsed_date})


def add_by_note(items, note):
    """Преобразует введённую строку с информацией о товаре.

    Формат строки: <название> <количество> [<дата в формате YYYY-MM-DD>]
    Название может содержать пробелы. Количество — число (int/float/str).
    Дата — необязательный параметр.

    Примеры:
        "Пельмени 2"
        "Пельмени Универсальные 2 2026-10-22"
        "Сок-яблоко 1.5"

    Args:
        items (dict): Словарь товаров, где ключ — название товара,
        значение — список партий.
        note (str): Строка с информацией о товарах.

    Returns:
        None: Вызывает функцию add и передает в нее аргументы.

    Raises:
        ValueError: Если формат строки некорректен
        или количество не является числом.

    """
    # Отлавливаем пустую строку.
    if not note or not note.strip():
        raise ValueError('Строка с информацией о товаре не может быть пустой.')
    parts = note.strip().split()
    if len(parts) < 2:
        raise ValueError(
            'Недостаточно данных. Укажите хотя бы название товара '
            'и количество.')
    # Пытаемся определить, есть ли дата в конце.
    # Дата должна быть в формате YYYY-MM-DD: ровно 3 части, все — цифры.
    last = parts[-1]
    has_date = False
    expiration_date = None
    if '-' in last:
        date_parts = last.split('-')
        if len(date_parts) == 3 and all(part.isdigit() for part in date_parts):
            # Дополнительная проверка диапазона (опционально, но полезно)
            _, month, day = map(int, date_parts)
            if 1 <= month <= 12 and 1 <= day <= 31:
                has_date = True
                expiration_date = last
    if has_date:
        if len(parts) < 3:
            raise ValueError('Если указана дата, должны быть и название,'
                             ' и количество.')
        amount_str = parts[-2]
        title = ' '.join(parts[:-2])
    else:
        amount_str = parts[-1]
        title = ' '.join(parts[:-1])
    # Безопасное преобразование количества
    try:
        amount = Decimal(amount_str)
    except InvalidOperation:
        raise ValueError(
            f'Некорректное количество: "{amount_str}".'
            'Должно быть числом.') from None
    add(items, title, amount, expiration_date)


def find(items, needle):
    """Ищет подстроку в ключах словаря товаров.

    Возвращает список ключей (названий товаров), которые содержат указанную
    подстроку (регистронезависимо)

    Args:
        items (dict[str, any]): Словарь товаров, где ключ — название товара.
        needle (str): Подстрока для поиска (регистронезависимая).

    Returns:
        list[str]: Список ключей, содержащих подстроку.

    Raises:
        TypeError: Если needle не является строкой.
    """
    # Защита от некорректного типа.
    if not isinstance(needle, str):
        raise TypeError("needle должен быть строкой")
    # Нормализуем поисковый запрос: убираем пробелы по краям и приводим к
    # нижнему регистру.
    # Это позволяет искать без учёта регистра и игнорировать случайные пробелы.
    search_term = needle.strip().lower()
    # Пустой запрос не должен возвращать все товары: это неинтуитивно
    # для пользователя.
    # Ранний выход (early return) делает логику понятнее и экономит ресурсы.
    if not search_term:
        return []
    # Фильтруем ключи словаря:
    # 1) Проверяем, что ключ — строка (защита от ключей-чисел и других типов).
    # 2) Приводим ключ к нижнему регистру и проверяем вхождение search_term.
    return [key for key in items if isinstance(key, str)
            and search_term in key.lower()]


def get_amount(items, needle):
    """Суммирует общее колличество найденных продуктов.

    Находит товары, названия которых содержат заданную
    подстроку (регистронезависимо),
    итерирует по всем партиям этих товаров и суммирует значения поля 'amount'.

    Args:
        items (dict): Словарь, который содержит названия
                      продуктов в качестве ключей, и информацию о каждом
                      продукте в виде списка словарей;
        needle (str): Подстрока, которую необходимо обнаружить
                      в названиях продуктов.

    Returns:
        Decimal: Общая сумма продуктов.
    """
    product_amount = Decimal(0)
    for title in find(items, needle):
        for batch in items[title]:
            if "amount" in batch:
                product_amount += Decimal(batch["amount"])
    return product_amount


def get_expired(items, in_advance_days=0):
    """Проверяет продукты на истечение срока годности.

    Принимает название словаря и колличество дней.

    Args:
        items(dict): Словарь, который содержит названия продуктов в качестве
                     ключей, и информацию о каждом продукте в виде списка
                     словарей.
        in_advance_days (int): количество дней, на которое нужно
                     учитывать истечение срока годности (по умолчанию — 0).
    Returns:
        list[()]: список кортежей, содержащий названия продуктов и остаточное
                  количество, у которых истекает срок годности.
    """
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
