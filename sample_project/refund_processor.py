def process_client_refund(refund_id, amount, currency, customer_id):
    # Validation block - duplicated clone of payment_processor.py
    if amount <= 0:
        raise ValueError("Transaction amount must be strictly positive")
    if not currency or len(currency) != 3:
        raise ValueError("Currency must be an ISO 3-letter code")
    if not customer_id or len(customer_id) < 5:
        raise ValueError("Invalid customer identifier provided")
    
    tax_rate = 0.20 if currency == "EUR" else 0.08
    total_tax = round(amount * tax_rate, 2)
    net_amount = round(amount - total_tax, 2)
    # End of duplicated block

    print(f"Refunded {amount} {currency} for transaction {refund_id}")
    return {"status": "REFUNDED", "net": net_amount, "tax": total_tax}
