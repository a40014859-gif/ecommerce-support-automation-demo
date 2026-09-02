import unittest

from support_router import normalize_event, process

class SupportRouterTests(unittest.TestCase):
    def test_order_tracking_is_answered_without_escalation(self):
        result = process({"channel": "whatsapp", "customer_id": "c1", "text": "Where is my order?"})
        self.assertEqual(result["category"], "order_status")
        self.assertFalse(result["escalated"])

    def test_refund_is_escalated(self):
        result = process({"channel": "email", "customer_id": "c2", "text": "Please refund my order"})
        self.assertEqual(result["category"], "sensitive_action")
        self.assertTrue(result["escalated"])

    def test_unknown_question_is_escalated(self):
        result = process({"channel": "email", "customer_id": "c3", "text": "Can you make this blue next Tuesday?"})
        self.assertTrue(result["escalated"])

    def test_raw_customer_id_is_not_in_audit_log(self):
        customer_id = "private-customer@example.com"
        result = process({"channel": "email", "customer_id": customer_id, "text": "What are your business hours?"})
        self.assertNotIn(customer_id, str(result["audit"]))
        self.assertEqual(len(result["audit"]["customer_ref"]), 12)

    def test_invalid_channel_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_event({"channel": "telegram", "customer_id": "c4", "text": "hello"})

if __name__ == "__main__":
    unittest.main()
