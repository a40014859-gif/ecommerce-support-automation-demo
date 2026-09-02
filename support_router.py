"""Minimal ecommerce support message router using only the Python standard library."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Dict, Optional
import json

FAQS: Dict[str, tuple[tuple[str, ...], str]] = {
    "shipping": (("shipping", "delivery", "how long", "arrive"), "Standard shipping times depend on destination. Please share your order number through the store's secure support channel for an exact status."),
    "order_status": (("where is my order", "track order", "tracking", "order status"), "I can help with order tracking. Please provide your order number through the store's secure support channel."),
    "returns_policy": (("return policy", "return window", "can i return", "returns"), "I can explain the store's return policy once the merchant's approved policy text is connected to this workflow."),
    "hours": (("business hours", "opening hours", "when are you open", "support hours"), "Support hours should be pulled from the merchant's configured business-hours source."),
}

ESCALATION_TERMS = ("refund", "cancel order", "chargeback", "fraud", "damaged", "wrong item", "payment failed", "legal")

@dataclass(frozen=True)
class InboundMessage:
    channel: str
    customer_id: str
    text: str
    external_id: Optional[str] = None

@dataclass(frozen=True)
class RouteResult:
    category: str
    reply: str
    escalated: bool
    audit: dict

def _customer_fingerprint(customer_id: str) -> str:
    return sha256(customer_id.encode("utf-8")).hexdigest()[:12]

def normalize_event(payload: dict) -> InboundMessage:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    channel = str(payload.get("channel", "")).strip().lower()
    customer_id = str(payload.get("customer_id", "")).strip()
    text = str(payload.get("text", "")).strip()
    external_id = payload.get("external_id")
    if channel not in {"whatsapp", "email"}:
        raise ValueError("channel must be 'whatsapp' or 'email'")
    if not customer_id:
        raise ValueError("customer_id is required")
    if not text:
        raise ValueError("text is required")
    return InboundMessage(channel, customer_id, text, str(external_id) if external_id else None)

def route_message(message: InboundMessage) -> RouteResult:
    lowered = message.text.casefold()
    category = "unknown"
    escalated = False
    reply = "I'm not confident enough to answer this automatically. I've routed it for human review."
    if any(term in lowered for term in ESCALATION_TERMS):
        category = "sensitive_action"
        escalated = True
        reply = "This request needs a support specialist to verify the order and store policy. I've routed it for human review."
    else:
        for name, (keywords, answer) in FAQS.items():
            if any(keyword in lowered for keyword in keywords):
                category = name
                reply = answer
                break
        else:
            escalated = True
    audit = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "channel": message.channel,
        "customer_ref": _customer_fingerprint(message.customer_id),
        "external_id": message.external_id,
        "category": category,
        "escalated": escalated,
    }
    return RouteResult(category, reply, escalated, audit)

def process(payload: dict) -> dict:
    return asdict(route_message(normalize_event(payload)))

if __name__ == "__main__":
    examples = [
        {"channel": "whatsapp", "customer_id": "demo-123", "text": "Where is my order?", "external_id": "wa-1"},
        {"channel": "email", "customer_id": "demo-456", "text": "I need a refund for a damaged item", "external_id": "mail-2"},
    ]
    for example in examples:
        print(json.dumps(process(example), indent=2))
