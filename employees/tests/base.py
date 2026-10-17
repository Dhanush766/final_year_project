"""Shared helpers for the test-suite.

All passwords, e-mails and names used in the tests are fictional,
test-only values and are never used outside the temporary test database.
"""
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase

from employees.models import Department, Employee

User = get_user_model()


def make_department(name="Engineering"):
    return Department.objects.get_or_create(name=name)[0]


def make_employee(department=None, **overrides):
    """Create and return an Employee with sensible defaults."""
    data = {
        "employee_id": "EMP001",
        "full_name": "Asha Verma",
        "email": "asha@example.com",
        "phone_number": "9876543210",
        "department": department or make_department(),
        "designation": "Developer",
        "salary": Decimal("50000.00"),
        "joining_date": date(2024, 1, 15),
        "status": Employee.Status.ACTIVE,
    }
    data.update(overrides)
    return Employee.objects.create(**data)


def valid_employee_data(department, **overrides):
    """Return a dictionary that is a valid POST payload for EmployeeForm."""
    data = {
        "employee_id": "EMP100",
        "full_name": "Ravi Kumar",
        "email": "ravi@example.com",
        "phone_number": "9123456780",
        "department": department.pk,
        "designation": "Analyst",
        "salary": "45000.00",
        "joining_date": "2024-02-01",
        "status": "ACTIVE",
    }
    data.update(overrides)
    return data


class BaseTestCase(TestCase):
    password = "Test-only-pass-12345"

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("admin", "admin@example.com", cls.password)
        # A read-only user: may view employees and departments, nothing else.
        cls.viewer = User.objects.create_user("viewer", "viewer@example.com", cls.password)
        cls.viewer.user_permissions.add(
            *Permission.objects.filter(
                content_type__app_label="employees",
                codename__in=["view_employee", "view_department"],
            )
        )
        # A logged-in user with no permissions at all.
        cls.nobody = User.objects.create_user("nobody", "nobody@example.com", cls.password)
        cls.department = make_department()
