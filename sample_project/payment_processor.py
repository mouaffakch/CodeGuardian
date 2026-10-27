def process_client_payment(transaction_id, amount, currency, customer_id):
    if amount <= 0:
        raise ValueError("Transaction amount must be strictly positive")
    if not currency or len(currency) != 3:
        raise ValueError("Currency must be an ISO 3-letter code")
    if not customer_id or len(customer_id) < 5:
        raise ValueError("Invalid customer identifier provided")
    
    tax_rate = 0.20 if currency == "EUR" else 0.08
    total_tax = round(amount * tax_rate, 2)
    net_amount = round(amount - total_tax, 2)

    print(f"Charged {amount} {currency} for transaction {transaction_id}")
    return {"status": "SUCCESS", "net": net_amount, "tax": total_tax}
