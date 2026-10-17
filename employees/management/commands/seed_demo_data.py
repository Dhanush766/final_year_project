"""Loads fictional demo data so the application looks realistic in a demonstration."""
from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from employees.models import Department, Employee

DEPARTMENTS = {
    "Engineering": "Builds and maintains the company's software products.",
    "Human Resources": "Recruitment, onboarding and employee welfare.",
    "Finance": "Accounting, payroll and budgeting.",
    "Marketing": "Brand, campaigns and communication.",
    "Operations": "Day-to-day logistics and process management.",
}

# (employee_id, full_name, department, designation, salary, joining_date, status)
EMPLOYEES = [
    ("EMP001", "Aarav Sharma", "Engineering", "Software Engineer", "65000", date(2023, 3, 15), "ACTIVE"),
    ("EMP002", "Diya Reddy", "Engineering", "Senior Developer", "95000", date(2021, 7, 1), "ACTIVE"),
    ("EMP003", "Rohan Mehta", "Engineering", "QA Engineer", "52000", date(2024, 1, 10), "ON_LEAVE"),
    ("EMP004", "Ananya Iyer", "Human Resources", "HR Manager", "72000", date(2020, 11, 23), "ACTIVE"),
    ("EMP005", "Karthik Nair", "Human Resources", "Recruiter", "41000", date(2024, 6, 3), "ACTIVE"),
    ("EMP006", "Sneha Kulkarni", "Finance", "Accountant", "48000", date(2022, 9, 12), "ACTIVE"),
    ("EMP007", "Vikram Singh", "Finance", "Finance Manager", "88000", date(2019, 4, 8), "ACTIVE"),
    ("EMP008", "Meera Joshi", "Marketing", "Marketing Executive", "45000", date(2023, 8, 21), "RESIGNED"),
    ("EMP009", "Arjun Patel", "Marketing", "Content Strategist", "50000", date(2022, 2, 14), "ACTIVE"),
    ("EMP010", "Priya Menon", "Operations", "Operations Lead", "68000", date(2021, 12, 5), "ACTIVE"),
    ("EMP011", "Sanjay Gupta", "Operations", "Logistics Coordinator", "38000", date(2024, 3, 18), "TERMINATED"),
    ("EMP012", "Neha Desai", "Engineering", "DevOps Engineer", "78000", date(2023, 10, 2), "ACTIVE"),
]


class Command(BaseCommand):
    help = "Create fictional departments and employees for demonstration. Safe to run repeatedly."

    def handle(self, *args, **options):
        departments = {}
        for name, description in DEPARTMENTS.items():
            departments[name], _ = Department.objects.get_or_create(
                name=name, defaults={"description": description}
            )

        created = 0
        for number, (emp_id, name, dept, designation, salary, joined, status) in enumerate(
            EMPLOYEES, start=1
        ):
            first, last = name.lower().split()
            _, was_created = Employee.objects.get_or_create(
                employee_id=emp_id,
                defaults={
                    "full_name": name,
                    "email": f"{first}.{last}@example.com",
                    "phone_number": f"+919000000{number:03d}",
                    "department": departments[dept],
                    "designation": designation,
                    "salary": Decimal(salary),
                    "joining_date": joined,
                    "status": status,
                },
            )
            created += int(was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data ready: {len(DEPARTMENTS)} departments, {created} new employees "
                f"({len(EMPLOYEES) - created} already existed)."
            )
        )
