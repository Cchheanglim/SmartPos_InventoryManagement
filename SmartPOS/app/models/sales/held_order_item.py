"""
No separate HeldOrderItem class exists because held_orders doesn't have
a line-items table — see sql/schema.sql, CREATE TABLE held_orders. A
held order's cart is stored as a single JSON TEXT column (`cart_json`),
decoded on demand by HeldOrder.cart_items (app/models/sales/held_order.py).

That's a deliberate, working design (a held order is a temporary,
short-lived snapshot of an in-progress cart — it never needs the kind of
relational querying a real line-items table exists for), not a gap. A
HeldOrderItem class with no repository or table behind it would be
misleading dead code, so this file intentionally has no class.
"""
