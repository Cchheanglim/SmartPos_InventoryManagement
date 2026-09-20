from app.repositories.sales.held_order_repository import HeldOrderRepository


class HeldOrderService:
    def __init__(self):
        self.held_order_repo = HeldOrderRepository()

    def hold(self, cashier_id, cart_items, discount_percent, customer_phone=None, customer_name=None, note=None):
        if not cart_items:
            raise ValueError("Cannot hold an empty cart.")
        return self.held_order_repo.create(cashier_id, cart_items, discount_percent, customer_phone, customer_name, note)

    def list_all(self):
        return self.held_order_repo.list_all()

    def count_all(self):
        return self.held_order_repo.count_all()

    def resume(self, held_order_id):
        """
        Returns the held order's cart data and removes it from the held
        list in the same step — once resumed, it belongs to the active
        checkout, not the held-orders list, so it can't be resumed twice.
        """
        order = self.held_order_repo.find_by_id(held_order_id)
        if order is None:
            raise ValueError("This held order no longer exists — it may have already been resumed.")
        self.held_order_repo.delete(held_order_id)
        return order

    def discard(self, held_order_id):
        order = self.held_order_repo.find_by_id(held_order_id)
        if order is None:
            raise ValueError("This held order no longer exists.")
        self.held_order_repo.delete(held_order_id)
