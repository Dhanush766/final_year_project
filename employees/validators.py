"""
Reusable field validators.

They are plain functions so that they can be used both by the models
(and therefore the Django Admin) and by the migrations.
"""
import re

from django.core.exceptions import ValidationError
from django.utils import timezone

_EMPLOYEE_ID_RE = re.compile(r"^[A-Za-z0-9-]+$")
_PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")
_NAME_EXTRA_CHARS = " .'-"


def validate_employee_id(value):
    if not _EMPLOYEE_ID_RE.match(value):
        raise ValidationError(
            "Employee ID may contain only letters, numbers and hyphens.",
            code="invalid_employee_id",
        )


def validate_full_name(value):
    cleaned = value.strip()
    if len(cleaned) < 2:
        raise ValidationError("Name must be at least 2 characters long.", code="short_name")
    if not cleaned[0].isalpha() or not all(
        ch.isalpha() or ch in _NAME_EXTRA_CHARS for ch in cleaned
    ):
        raise ValidationError(
            "Name may contain only letters, spaces, apostrophes, hyphens and dots.",
            code="invalid_name",
        )


def validate_phone_number(value):
    if not _PHONE_RE.match(value):
        raise ValidationError(
            "Enter 10 to 15 digits, optionally starting with '+'.",
            code="invalid_phone",
        )


def validate_positive_salary(value):
    if value is not None and value <= 0:
        raise ValidationError("Salary must be greater than zero.", code="invalid_salary")


def validate_not_in_future(value):
    if value > timezone.localdate():
        raise ValidationError("Joining date cannot be in the future.", code="future_date")
