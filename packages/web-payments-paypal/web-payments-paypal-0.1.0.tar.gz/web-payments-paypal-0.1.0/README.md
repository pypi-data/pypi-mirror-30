web-payments-paydirekt
======================

Usage:

add to PAYMENT_VARIANTS_API:

``` python
PAYMENT_VARIANTS_API = {
    ...
    'paydirekt': ('web_payments_paydirekt.PaydirektProvider', {
        "client_id": "<clientid>",
        "secret": "<secret>",
        "endpoint": 'https://api.sandbox.paypal.com'
        "capture": True
      }
    )
  }
```
