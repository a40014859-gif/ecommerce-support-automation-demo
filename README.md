# Ecommerce Support Automation Demo

A small, runnable proof-of-capability for routing ecommerce customer-support messages from channels such as WhatsApp or email.

This is a **demo**, not a claim of previous client work. It uses no private customer data, no live WhatsApp credentials, and no production APIs.

## What it demonstrates

- Normalizes inbound WhatsApp/email-style messages
- Detects common FAQ intents such as shipping, order status, returns, and business hours
- Escalates sensitive or ambiguous cases instead of inventing an answer
- Produces a minimal privacy-conscious audit event without storing message text
- Includes automated tests

## Run it

```bash
python3 support_router.py
python3 -m unittest discover -s tests -v
```

## Production architecture

```text
WhatsApp Business webhook / Email provider
                 |
                 v
        normalize inbound event
                 |
                 v
        FAQ + policy router
          /             \
  safe answer       escalation
      |                 |
      v                 v
 customer reply     human inbox / CRM
          \             /
           v           v
          audit metadata
```

A real deployment would connect the router to the merchant's approved WhatsApp Business provider, email API, helpdesk/CRM, and store/order API. Credentials belong in environment variables or a secrets manager, never in source control.

## Scope boundary

The demo escalates refunds, cancellations, damaged-item claims, payment disputes, and unclear requests. Those actions usually require authentication, store policy checks, or human approval.