import re
from app.repositories.sales.customer_repository import CustomerRepository


class CRMService:
    """
    Owns customer lookup/registration for the checkout screen. The full
    phone number is used internally as the customer's unique ID, but this
    service is the only thing allowed to build the masked tag (e.g.
    "Sara012" — first name + first 3 digits of phone) that actually reaches
    the UI. Nothing above this layer should ever see a raw phone number.
    """

    def __init__(self):
        self.customer_repo = CustomerRepository()

    @staticmethod
    def _clean_phone(phone):
        return re.sub(r"\D", "", phone or "")

    @staticmethod
    def build_masked_tag(name, phone):
        clean_phone = re.sub(r"\D", "", phone or "")
        first_three = clean_phone[:3]
        first_name = (name or "Guest").split(" ")[0]
        return f"{first_name}{first_three}"

    def lookup(self, phone):
        """Returns {'found': True, 'masked_tag': ...} or {'found': False}."""
        clean_phone = self._clean_phone(phone)
        if not clean_phone:
            return {"found": False, "message": "Enter a phone number to search."}
        customer = self.customer_repo.find_by_phone(clean_phone)
        if customer is None:
            return {"found": False, "message": "No customer found with that phone number."}
        return {
            "found": True,
            "phone": customer.phone,
            "masked_tag": self.build_masked_tag(customer.name, customer.phone),
        }

    def register(self, name, phone):
        clean_phone = self._clean_phone(phone)
        clean_name = (name or "").strip()
        if not clean_name or not clean_phone:
            raise ValueError("Name and phone number are required.")
        if self.customer_repo.find_by_phone(clean_phone) is not None:
            raise ValueError("A customer with this phone number is already registered.")
        self.customer_repo.create(clean_phone, clean_name)
        return {"phone": clean_phone, "masked_tag": self.build_masked_tag(clean_name, clean_phone)}

    def find_or_none(self, phone):
        """Used internally by SalesService — returns the Customer row or None."""
        clean_phone = self._clean_phone(phone)
        if not clean_phone:
            return None
        return self.customer_repo.find_by_phone(clean_phone)

    def masked_tag_for_phone(self, phone):
        """Used by the receipt page to display a masked tag from a stored phone."""
        customer = self.find_or_none(phone)
        if customer is None:
            return None
        return self.build_masked_tag(customer.name, customer.phone)
