"""
Tests for the CRM phone-masking logic. build_masked_tag is a pure static
method, so these run with no database or app context needed.
"""
from app.services.sales.crm_service import CRMService


def test_masked_tag_uses_first_name_and_first_three_digits():
    assert CRMService.build_masked_tag("Sara Chan", "012345678") == "Sara012"


def test_masked_tag_strips_non_digit_characters_from_phone():
    assert CRMService.build_masked_tag("David", "(012) 345-678") == "David012"


def test_masked_tag_falls_back_to_guest_when_name_missing():
    assert CRMService.build_masked_tag("", "099888777") == "Guest099"


def test_masked_tag_handles_short_phone_gracefully():
    assert CRMService.build_masked_tag("Ann", "12") == "Ann12"
