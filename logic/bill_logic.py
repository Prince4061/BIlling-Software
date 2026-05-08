def calculate_item_total(qty, rate):
    try:
        qty = float(qty)
        rate = float(rate)
        return qty * rate
    except ValueError:
        return 0.0

def calculate_grand_total(items, tax=0.0):
    """
    items: list of dictionaries, e.g., [{"amount": 1000}, ...]
    """
    total = 0.0
    for item in items:
        total += float(item.get("amount", 0))
    
    try:
        tax = float(tax)
    except ValueError:
        tax = 0.0
        
    grand_total = total + tax
    return total, grand_total
