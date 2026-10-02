import csv
from datetime import datetime
from core.paths import OUTPUT_DIR

def output(*, items_list: list):
    """
    Создание CSV файла из полученных данных.
    """
    
    headers = [
        'САЙТ', 
        'НОМЕР ПРОДУКТА', 
        'НАЧАЛО ПРИЁМА ЗАКАЗОВ', 
        'КОНЕЦ ПРИЁМА ЗАЯВОК', 
        'НАЗВАНИЕ ПРОДУКТА', 
        'ЗАКАЗЧИК ПРОДУКТА', 
        'ОБЩАЯ СУММА ЛОТОВ'
    ]

    now = datetime.now()
    text = f"data-{now:%d.%m.%Y}-{now:%H_%M}.csv"

    OUTPUT_DIR.mkdir(exist_ok=True)
        
    path = OUTPUT_DIR / text

    with open(path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        for item in items_list:
            writer.writerow([
                item.get("URL", ""),
                item.get("ID", ""),
                item.get("START_DATE", ""),
                item.get("END_DATE", ""),
                item.get("NAME", ""),
                item.get("OWNER", ""),
                item.get("PRICE", ""),
            ])
            
    return path
