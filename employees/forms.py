"""Forms: employee and department forms, the search/filter form and the login form."""
import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import Department, Employee


class BootstrapFormMixin:
    """Adds Bootstrap CSS classes to every widget, and marks invalid fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            css_class = "form-select" if isinstance(widget, forms.Select) else "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {css_class}".strip()

    def full_clean(self):
        super().full_clean()
        if self.is_bound and self._errors:
            for name in self._errors:
                if name in self.fields:
                    widget = self.fields[name].widget
                    css = widget.attrs.get("class", "")
                    if "is-invalid" not in css:
                        widget.attrs["class"] = f"{css} is-invalid".strip()


class StyledAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    """Login form with Bootstrap styling."""


class EmployeeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "full_name",
            "email",
            "phone_number",
            "department",
            "designation",
            "salary",
            "joining_date",
            "status",
        ]
        labels = {
            "employee_id": "Employee ID",
            "full_name": "Full name",
            "phone_number": "Phone number",
            "joining_date": "Joining date",
            "status": "Employment status",
        }
        help_texts = {
            "employee_id": "Letters, numbers and hyphens only (e.g. EMP-101).",
            "phone_number": "10 to 15 digits, optionally starting with + (e.g. +919876543210).",
            "salary": "Amount greater than zero, up to 2 decimal places.",
        }
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "name@company.com"}),
            "phone_number": forms.TextInput(attrs={"type": "tel"}),
            "salary": forms.NumberInput(attrs={"step": "0.01", "min": "0.01"}),
            "joining_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }
        error_messages = {
            "employee_id": {"unique": "An employee with this Employee ID already exists."},
            "email": {"unique": "An employee with this email address already exists."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].empty_label = "Select a department"

    def clean_employee_id(self):
        return self.cleaned_data["employee_id"].strip().upper()

    def clean_full_name(self):
        # Collapse repeated spaces: "Asha   Verma" -> "Asha Verma"
        return " ".join(self.cleaned_data["full_name"].split())

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_phone_number(self):
        # Allow "+91 98765-43210" and store it as "+919876543210".
        return re.sub(r"[\s-]", "", self.cleaned_data["phone_number"])

    def clean_designation(self):
        return " ".join(self.cleaned_data["designation"].split())


class DepartmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())
        duplicates = Department.objects.filter(name__iexact=name)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise ValidationError("A department with this name already exists.")
        return name


class EmployeeFilterForm(BootstrapFormMixin, forms.Form):
    """GET form used on the employee list for searching and filtering."""

    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "Search by name or employee ID"}),
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="All departments",
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All statuses")] + list(Employee.Status.choices),
    )
