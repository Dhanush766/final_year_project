from io import StringIO

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase

from employees.models import Department, Employee


class SetupRolesCommandTests(TestCase):
    def test_creates_groups_with_expected_permissions(self):
        call_command("setup_roles", stdout=StringIO())

        manager = Group.objects.get(name="HR Manager")
        viewer = Group.objects.get(name="Viewer")
        self.assertEqual(manager.permissions.count(), 8)
        self.assertEqual(
            set(viewer.permissions.values_list("codename", flat=True)),
            {"view_employee", "view_department"},
        )

    def test_command_is_repeatable(self):
        call_command("setup_roles", stdout=StringIO())
        call_command("setup_roles", stdout=StringIO())
        self.assertEqual(Group.objects.filter(name="HR Manager").count(), 1)


class SeedDemoDataCommandTests(TestCase):
    def test_seeds_data_without_duplicates(self):
        call_command("seed_demo_data", stdout=StringIO())
        call_command("seed_demo_data", stdout=StringIO())
        self.assertEqual(Department.objects.count(), 5)
        self.assertEqual(Employee.objects.count(), 12)
