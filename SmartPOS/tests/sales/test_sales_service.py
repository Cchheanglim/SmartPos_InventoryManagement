"""
Sample test cases for SmartPOS's core business rules, per Section 11
of the proposal ("core business rules verified through service-level
tests"). These use a fake repository instead of a real MySQL connection,
so they run without a database.

Run with: python -m pytest tests/
(requires `pip install pytest` — not in requirements.txt since it's a
dev-only dependency)
"""
import pytest
from app.services.sales.sales_service import SalesService, InsufficientStockError


class FakeProduct:
    def __init__(self, id, name, price, quantity_in_stock):
        self.id = id
        self.name = name
        self.price = price
        self.quantity_in_stock = quantity_in_stock


class FakeProductRepo:
    def __init__(self, products):
        self._products = {p.id: p for p in products}
        self.adjustments = []

    def find_by_id(self, product_id):
        return self._products.get(product_id)

    def adjust_stock(self, product_id, change_amount):
        self.adjustments.append((product_id, change_amount))
        self._products[product_id].quantity_in_stock += change_amount


class FakeSaleRepo:
    def __init__(self):
        self.created = None

    def create_sale_with_items(self, cashier_id, discount_percent, payment_method,
                                total_amount, line_items, customer_phone=None, tax_percent=0):
        self.created = {
            "cashier_id": cashier_id, "discount_percent": discount_percent,
            "payment_method": payment_method, "total_amount": total_amount,
            "line_items": line_items, "customer_phone": customer_phone,
            "tax_percent": tax_percent,
        }
        return 1

    def find_by_id(self, sale_id):
        return self.created


class FakeStockRepo:
    def __init__(self):
        self.logged = []

    def create(self, product_id, change_amount, reason):
        self.logged.append((product_id, change_amount, reason))


def make_service():
    service = SalesService()
    service.product_repo = FakeProductRepo([
        FakeProduct(1, "Rice 5kg", 12.00, 10),
        FakeProduct(2, "Cooking Oil 1L", 4.50, 2),
    ])
    service.sale_repo = FakeSaleRepo()
    service.stock_repo = FakeStockRepo()
    return service


def test_checkout_deducts_stock_correctly():
    service = make_service()
    service.checkout(cashier_id=1, cart_items=[{"product_id": 1, "quantity": 3}])
    assert service.product_repo._products[1].quantity_in_stock == 7


def test_checkout_rejects_quantity_exceeding_stock():
    service = make_service()
    with pytest.raises(InsufficientStockError):
        service.checkout(cashier_id=1, cart_items=[{"product_id": 2, "quantity": 5}])


def test_checkout_applies_discount_to_total():
    service = make_service()
    sale = service.checkout(
        cashier_id=1,
        cart_items=[{"product_id": 1, "quantity": 2}],  # 2 x 12.00 = 24.00
        discount_percent=25,
    )
    assert sale["total_amount"] == 18.00  # 24.00 * 0.75


def test_checkout_rejects_empty_cart():
    service = make_service()
    with pytest.raises(ValueError):
        service.checkout(cashier_id=1, cart_items=[])


def test_checkout_rejects_invalid_discount():
    service = make_service()
    with pytest.raises(ValueError):
        service.checkout(cashier_id=1, cart_items=[{"product_id": 1, "quantity": 1}],
                          discount_percent=150)
