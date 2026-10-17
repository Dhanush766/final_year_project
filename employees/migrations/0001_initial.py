import django.db.models.deletion
from django.db import migrations, models

import employees.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("employee_id", models.CharField(max_length=20, unique=True, validators=[employees.validators.validate_employee_id])),
                ("full_name", models.CharField(max_length=150, validators=[employees.validators.validate_full_name])),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("phone_number", models.CharField(max_length=16, validators=[employees.validators.validate_phone_number])),
                ("designation", models.CharField(max_length=100)),
                ("salary", models.DecimalField(decimal_places=2, max_digits=10, validators=[employees.validators.validate_positive_salary])),
                ("joining_date", models.DateField(validators=[employees.validators.validate_not_in_future])),
                ("status", models.CharField(choices=[("ACTIVE", "Active"), ("ON_LEAVE", "On Leave"), ("RESIGNED", "Resigned"), ("TERMINATED", "Terminated")], default="ACTIVE", max_length=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="employees", to="employees.department")),
            ],
            options={
                "ordering": ["employee_id"],
            },
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["status"], name="emp_status_idx"),
        ),
    ]
