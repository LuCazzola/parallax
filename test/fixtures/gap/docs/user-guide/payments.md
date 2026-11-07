# Payments

Code: `src/shop/payments.py`

Charges run inside the request, so a customer waits for the bank's reply before seeing
the confirmation page. We chose this so a failed charge is shown at once.
