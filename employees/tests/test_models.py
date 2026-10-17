from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.utils import timezone

from employees.models import Department, Employee

from .base import make_department, make_employee


class DepartmentModelTests(TestCase):
    def test_string_representation_is_the_name(self):
        self.assertEqual(str(Department(name="Finance")), "Finance")

    def test_department_names_are_unique(self):
        Department.objects.create(name="Finance")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Department.objects.create(name="Finance")

    def test_department_with_employees_cannot_be_deleted(self):
        employee = make_employee()
        with self.assertRaises(ProtectedError):
            employee.department.delete()


class EmployeeModelTests(TestCase):
    def test_string_representation(self):
        employee = make_employee()
        self.assertEqual(str(employee), "EMP001 - Asha Verma")

    def test_default_status_is_active(self):
        self.assertEqual(make_employee().status, Employee.Status.ACTIVE)

    def test_employee_id_and_email_are_normalised_on_save(self):
        employee = make_employee(employee_id="emp9", email="Mixed@Example.COM")
        employee.refresh_from_db()
        self.assertEqual(employee.employee_id, "EMP9")
        self.assertEqual(employee.email, "mixed@example.com")

    def test_employee_id_must_be_unique(self):
        make_employee()
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_employee(email="other@example.com")

    def test_email_must_be_unique(self):
        make_employee()
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_employee(employee_id="EMP002")

    def test_future_joining_date_is_rejected(self):
        employee = make_employee()
        employee.joining_date = timezone.localdate() + timedelta(days=1)
        with self.assertRaises(ValidationError) as context:
            employee.full_clean()
        self.assertIn("joining_date", context.exception.message_dict)

    def test_zero_salary_is_rejected(self):
        employee = make_employee()
        employee.salary = 0
        with self.assertRaises(ValidationError) as context:
            employee.full_clean()
        self.assertIn("salary", context.exception.message_dict)

    def test_invalid_phone_is_rejected(self):
        employee = make_employee()
        employee.phone_number = "12ab"
        with self.assertRaises(ValidationError) as context:
            employee.full_clean()
        self.assertIn("phone_number", context.exception.message_dict)

    def test_employees_are_ordered_by_employee_id(self):
        department = make_department()
        make_employee(department, employee_id="EMP003", email="c@example.com")
        make_employee(department, employee_id="EMP001", email="a@example.com")
        make_employee(department, employee_id="EMP002", email="b@example.com")
        ids = list(Employee.objects.values_list("employee_id", flat=True))
        self.assertEqual(ids, ["EMP001", "EMP002", "EMP003"])
