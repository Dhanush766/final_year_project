from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from employees.forms import DepartmentForm, EmployeeFilterForm, EmployeeForm
from employees.models import Department

from .base import make_department, make_employee, valid_employee_data


class EmployeeFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.department = make_department()

    def make_form(self, **overrides):
        return EmployeeForm(data=valid_employee_data(self.department, **overrides))

    def test_valid_data_is_accepted(self):
        self.assertTrue(self.make_form().is_valid())

    def test_input_is_cleaned_and_normalised(self):
        form = self.make_form(
            employee_id=" emp050 ",
            email="NEW@Example.com",
            phone_number="+91 98765-43210",
            full_name="Mary   Jane",
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["employee_id"], "EMP050")
        self.assertEqual(form.cleaned_data["email"], "new@example.com")
        self.assertEqual(form.cleaned_data["phone_number"], "+919876543210")
        self.assertEqual(form.cleaned_data["full_name"], "Mary Jane")

    def test_name_with_apostrophe_and_hyphen_is_valid(self):
        self.assertTrue(self.make_form(full_name="Mary-Jane O'Neil").is_valid())

    def test_name_with_digits_is_rejected(self):
        self.assertIn("full_name", self.make_form(full_name="John123").errors)

    def test_required_fields(self):
        form = EmployeeForm(data={})
        self.assertFalse(form.is_valid())
        for name in form.fields:
            self.assertIn(name, form.errors)

    def test_invalid_employee_id_characters(self):
        self.assertIn("employee_id", self.make_form(employee_id="EMP 1!").errors)

    def test_invalid_email(self):
        self.assertIn("email", self.make_form(email="not-an-email").errors)

    def test_invalid_phone(self):
        self.assertIn("phone_number", self.make_form(phone_number="12345").errors)

    def test_zero_negative_and_text_salary_are_rejected(self):
        for bad_value in ("0", "-5", "abc"):
            with self.subTest(salary=bad_value):
                self.assertIn("salary", self.make_form(salary=bad_value).errors)

    def test_salary_with_too_many_digits_is_rejected(self):
        self.assertIn("salary", self.make_form(salary="100000000").errors)

    def test_future_joining_date_is_rejected(self):
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        self.assertIn("joining_date", self.make_form(joining_date=tomorrow).errors)

    def test_unknown_status_is_rejected(self):
        self.assertIn("status", self.make_form(status="UNKNOWN").errors)

    def test_duplicate_employee_id_is_rejected_ignoring_case(self):
        make_employee(self.department, employee_id="EMP100", email="first@example.com")
        form = self.make_form(employee_id="emp100", email="second@example.com")
        self.assertIn("employee_id", form.errors)

    def test_duplicate_email_is_rejected_ignoring_case(self):
        make_employee(self.department, employee_id="EMP001", email="first@example.com")
        form = self.make_form(employee_id="EMP002", email="FIRST@example.com")
        self.assertIn("email", form.errors)

    def test_editing_an_employee_does_not_clash_with_itself(self):
        employee = make_employee(self.department, employee_id="EMP100", email="ravi@example.com")
        form = EmployeeForm(
            data=valid_employee_data(self.department, designation="Senior Analyst"),
            instance=employee,
        )
        self.assertTrue(form.is_valid(), form.errors)


class DepartmentFormTests(TestCase):
    def test_valid_department(self):
        self.assertTrue(DepartmentForm(data={"name": "Finance", "description": ""}).is_valid())

    def test_name_is_required(self):
        self.assertIn("name", DepartmentForm(data={"name": "  ", "description": ""}).errors)

    def test_duplicate_name_is_rejected_ignoring_case(self):
        Department.objects.create(name="Finance")
        form = DepartmentForm(data={"name": "finance", "description": ""})
        self.assertIn("name", form.errors)

    def test_editing_a_department_keeps_its_own_name(self):
        department = Department.objects.create(name="Finance")
        form = DepartmentForm(
            data={"name": "Finance", "description": "Updated"}, instance=department
        )
        self.assertTrue(form.is_valid(), form.errors)


class EmployeeFilterFormTests(TestCase):
    def test_empty_filters_are_valid(self):
        self.assertTrue(EmployeeFilterForm(data={}).is_valid())

    def test_unknown_department_is_invalid(self):
        self.assertFalse(EmployeeFilterForm(data={"department": "abc"}).is_valid())

    def test_unknown_status_is_invalid(self):
        self.assertFalse(EmployeeFilterForm(data={"status": "NOPE"}).is_valid())
