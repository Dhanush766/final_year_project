"""Database models: Department and Employee."""
from django.db import models

from .validators import (
    validate_employee_id,
    validate_full_name,
    validate_not_in_future,
    validate_phone_number,
    validate_positive_salary,
)


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ON_LEAVE = "ON_LEAVE", "On Leave"
        RESIGNED = "RESIGNED", "Resigned"
        TERMINATED = "TERMINATED", "Terminated"

    employee_id = models.CharField(
        max_length=20, unique=True, validators=[validate_employee_id]
    )
    full_name = models.CharField(max_length=150, validators=[validate_full_name])
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=16, validators=[validate_phone_number])
    # PROTECT: a department that still has employees cannot be deleted.
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="employees"
    )
    designation = models.CharField(max_length=100)
    salary = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_positive_salary]
    )
    joining_date = models.DateField(validators=[validate_not_in_future])
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee_id"]
        indexes = [models.Index(fields=["status"], name="emp_status_idx")]

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"

    def _normalise(self):
        """Store IDs in upper case and e-mails in lower case."""
        self.employee_id = (self.employee_id or "").strip().upper()
        self.email = (self.email or "").strip().lower()

    def clean(self):
        # Runs for ModelForms and the Django Admin, before the uniqueness check.
        self._normalise()

    def save(self, *args, **kwargs):
        # Also normalise when objects are created from code or the shell.
        self._normalise()
        super().save(*args, **kwargs)
