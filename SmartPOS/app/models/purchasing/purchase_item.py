"""
No separate PurchaseItem class exists because a purchase order in this
schema is for exactly one product — see sql/schema.sql, CREATE TABLE
purchase_orders: `product_id` and `quantity_ordered` are columns directly
on the purchase_orders row itself, not a separate line-items table.

That matches how purchasing actually works in this app (restocking one
product at a time from Products > Purchase Orders), not an omission. A
PurchaseItem class with no repository or table behind it would be
misleading dead code, so this file intentionally has no class. If
multi-product purchase orders are ever needed, that's a schema change
(a real purchase_order_items table) this file would then back.
"""
