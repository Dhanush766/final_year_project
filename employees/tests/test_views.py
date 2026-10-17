from django.test import Client
from django.urls import reverse

from employees.models import Department, Employee

from .base import BaseTestCase, make_department, make_employee, valid_employee_data


def message_texts(response):
    return [str(message) for message in response.context["messages"]]


class AuthenticationTests(BaseTestCase):
    def test_pages_redirect_anonymous_users_to_login(self):
        urls = [
            reverse("employees:dashboard"),
            reverse("employees:employee_list"),
            reverse("employees:employee_add"),
            reverse("employees:department_list"),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response, f"{reverse('login')}?next={url}", fetch_redirect_response=False
                )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("login"), {"username": "admin", "password": self.password}
        )
        self.assertRedirects(
            response, reverse("employees:dashboard"), fetch_redirect_response=False
        )
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            reverse("login"), {"username": "admin", "password": "wrong-password"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_requires_post_and_ends_the_session(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)

        protected = self.client.get(reverse("employees:employee_list"))
        self.assertEqual(protected.status_code, 302)


class DashboardTests(BaseTestCase):
    def test_dashboard_statistics(self):
        other = make_department("Finance")
        make_employee(self.department, employee_id="EMP001", email="a@example.com")
        make_employee(self.department, employee_id="EMP002", email="b@example.com")
        make_employee(
            other, employee_id="EMP003", email="c@example.com", status=Employee.Status.RESIGNED
        )
        self.client.force_login(self.admin)
        response = self.client.get(reverse("employees:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_employees"], 3)
        self.assertEqual(response.context["active_employees"], 2)
        self.assertEqual(response.context["inactive_employees"], 1)
        self.assertEqual(response.context["department_count"], 2)
        stats = {row["name"]: row for row in response.context["department_stats"]}
        self.assertEqual(stats["Engineering"]["total"], 2)
        self.assertEqual(stats["Finance"]["total"], 1)
        self.assertEqual(stats["Finance"]["active"], 0)

    def test_dashboard_works_with_no_data(self):
        Department.objects.all().delete()
        self.client.force_login(self.admin)
        response = self.client.get(reverse("employees:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_employees"], 0)


class EmployeeListTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.finance = make_department("Finance")
        cls.asha = make_employee(
            cls.department, employee_id="EMP001", full_name="Asha Verma", email="asha@example.com"
        )
        cls.rohan = make_employee(
            cls.finance,
            employee_id="EMP002",
            full_name="Rohan Mehta",
            email="rohan@example.com",
            status=Employee.Status.ON_LEAVE,
        )

    def get_ids(self, **params):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("employees:employee_list"), params)
        self.assertEqual(response.status_code, 200)
        return [employee.employee_id for employee in response.context["employees"]]

    def test_lists_all_employees(self):
        self.assertEqual(self.get_ids(), ["EMP001", "EMP002"])

    def test_search_by_name(self):
        self.assertEqual(self.get_ids(q="asha"), ["EMP001"])

    def test_search_by_employee_id(self):
        self.assertEqual(self.get_ids(q="emp002"), ["EMP002"])

    def test_search_with_no_match(self):
        self.assertEqual(self.get_ids(q="nobody-like-this"), [])

    def test_filter_by_department(self):
        self.assertEqual(self.get_ids(department=self.finance.pk), ["EMP002"])

    def test_filter_by_status(self):
        self.assertEqual(self.get_ids(status="ON_LEAVE"), ["EMP002"])

    def test_combined_filters(self):
        self.assertEqual(self.get_ids(q="rohan", department=self.finance.pk, status="ON_LEAVE"), ["EMP002"])
        self.assertEqual(self.get_ids(q="asha", department=self.finance.pk), [])

    def test_invalid_filter_values_do_not_crash(self):
        self.assertEqual(self.get_ids(department="abc", status="BAD"), ["EMP001", "EMP002"])

    def test_pagination(self):
        for number in range(3, 26):
            make_employee(
                self.department,
                employee_id=f"EMP{number:03d}",
                email=f"user{number}@example.com",
            )
        self.client.force_login(self.admin)
        url = reverse("employees:employee_list")
        self.assertEqual(len(self.client.get(url).context["employees"]), 10)
        self.assertEqual(len(self.client.get(url, {"page": 3}).context["employees"]), 5)
        self.assertEqual(self.client.get(url, {"page": 99}).status_code, 404)


class EmployeeCrudTests(BaseTestCase):
    def setUp(self):
        self.client.force_login(self.admin)

    def test_detail_page(self):
        employee = make_employee(self.department)
        response = self.client.get(reverse("employees:employee_detail", args=[employee.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Asha Verma")

    def test_detail_of_missing_employee_is_404(self):
        response = self.client.get(reverse("employees:employee_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_add_employee_with_valid_data(self):
        response = self.client.post(
            reverse("employees:employee_add"),
            valid_employee_data(self.department),
            follow=True,
        )
        self.assertRedirects(response, reverse("employees:employee_list"))
        self.assertTrue(Employee.objects.filter(employee_id="EMP100").exists())
        self.assertTrue(any("added successfully" in text for text in message_texts(response)))

    def test_add_employee_with_invalid_data_shows_errors(self):
        response = self.client.post(
            reverse("employees:employee_add"),
            valid_employee_data(self.department, email="bad-email"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Employee.objects.count(), 0)
        self.assertIn("email", response.context["form"].errors)
        self.assertTrue(any("correct the errors" in text for text in message_texts(response)))

    def test_edit_employee(self):
        employee = make_employee(self.department, employee_id="EMP100", email="ravi@example.com")
        response = self.client.post(
            reverse("employees:employee_edit", args=[employee.pk]),
            valid_employee_data(self.department, designation="Lead Analyst"),
        )
        self.assertRedirects(
            response,
            reverse("employees:employee_detail", args=[employee.pk]),
            fetch_redirect_response=False,
        )
        employee.refresh_from_db()
        self.assertEqual(employee.designation, "Lead Analyst")

    def test_delete_shows_confirmation_page_first(self):
        employee = make_employee(self.department)
        url = reverse("employees:employee_delete", args=[employee.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "employees/employee_confirm_delete.html")
        self.assertTrue(Employee.objects.filter(pk=employee.pk).exists())

    def test_delete_employee_after_confirmation(self):
        employee = make_employee(self.department)
        response = self.client.post(
            reverse("employees:employee_delete", args=[employee.pk]), follow=True
        )
        self.assertRedirects(response, reverse("employees:employee_list"))
        self.assertFalse(Employee.objects.filter(pk=employee.pk).exists())
        self.assertTrue(any("was deleted" in text for text in message_texts(response)))


class DepartmentCrudTests(BaseTestCase):
    def setUp(self):
        self.client.force_login(self.admin)

    def test_department_list_shows_employee_counts(self):
        make_employee(self.department)
        response = self.client.get(reverse("employees:department_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["departments"][0].employee_count, 1)

    def test_add_department(self):
        response = self.client.post(
            reverse("employees:department_add"),
            {"name": "Finance", "description": "Money matters"},
            follow=True,
        )
        self.assertRedirects(response, reverse("employees:department_list"))
        self.assertTrue(Department.objects.filter(name="Finance").exists())

    def test_duplicate_department_is_rejected(self):
        response = self.client.post(
            reverse("employees:department_add"), {"name": "engineering", "description": ""}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Department.objects.count(), 1)

    def test_edit_department(self):
        response = self.client.post(
            reverse("employees:department_edit", args=[self.department.pk]),
            {"name": "Engineering", "description": "Updated text"},
        )
        self.assertRedirects(
            response, reverse("employees:department_list"), fetch_redirect_response=False
        )
        self.department.refresh_from_db()
        self.assertEqual(self.department.description, "Updated text")

    def test_delete_empty_department(self):
        empty = Department.objects.create(name="Empty")
        response = self.client.post(reverse("employees:department_delete", args=[empty.pk]))
        self.assertRedirects(
            response, reverse("employees:department_list"), fetch_redirect_response=False
        )
        self.assertFalse(Department.objects.filter(pk=empty.pk).exists())

    def test_department_with_employees_cannot_be_deleted(self):
        make_employee(self.department)
        response = self.client.post(
            reverse("employees:department_delete", args=[self.department.pk]), follow=True
        )
        self.assertTrue(Department.objects.filter(pk=self.department.pk).exists())
        self.assertTrue(any("cannot be deleted" in text for text in message_texts(response)))


class PermissionTests(BaseTestCase):
    def setUp(self):
        self.employee = make_employee(self.department)

    def test_viewer_can_read_but_not_modify(self):
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.get(reverse("employees:employee_list")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("employees:employee_detail", args=[self.employee.pk])).status_code,
            200,
        )
        self.assertEqual(self.client.get(reverse("employees:employee_add")).status_code, 403)
        self.assertEqual(
            self.client.get(reverse("employees:employee_edit", args=[self.employee.pk])).status_code,
            403,
        )

    def test_viewer_cannot_create_edit_or_delete(self):
        self.client.force_login(self.viewer)
        response = self.client.post(
            reverse("employees:employee_add"),
            valid_employee_data(self.department),
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Employee.objects.count(), 1)

        response = self.client.post(
            reverse("employees:employee_edit", args=[self.employee.pk]),
            valid_employee_data(self.department, designation="Hacked"),
        )
        self.assertEqual(response.status_code, 403)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.designation, "Developer")

        response = self.client.post(reverse("employees:employee_delete", args=[self.employee.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Employee.objects.filter(pk=self.employee.pk).exists())

    def test_viewer_cannot_manage_departments(self):
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.get(reverse("employees:department_list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("employees:department_add")).status_code, 403)
        response = self.client.post(
            reverse("employees:department_delete", args=[self.department.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_user_without_permissions_is_denied(self):
        self.client.force_login(self.nobody)
        self.assertEqual(self.client.get(reverse("employees:dashboard")).status_code, 403)
        self.assertEqual(self.client.get(reverse("employees:employee_list")).status_code, 403)
        self.assertEqual(self.client.get(reverse("employees:department_list")).status_code, 403)

    def test_anonymous_user_cannot_delete(self):
        url = reverse("employees:employee_delete", args=[self.employee.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])
        self.assertTrue(Employee.objects.filter(pk=self.employee.pk).exists())

    def test_post_without_csrf_token_is_rejected(self):
        strict_client = Client(enforce_csrf_checks=True)
        strict_client.force_login(self.admin)
        response = strict_client.post(
            reverse("employees:employee_add"), valid_employee_data(self.department)
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Employee.objects.count(), 1)


class AdminIntegrationTests(BaseTestCase):
    def test_admin_changelists_load_for_superuser(self):
        make_employee(self.department)
        self.client.force_login(self.admin)
        for name in ("admin:employees_employee_changelist", "admin:employees_department_changelist"):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_admin_is_closed_to_non_staff_users(self):
        self.client.force_login(self.viewer)
        response = self.client.get(reverse("admin:employees_employee_changelist"))
        self.assertEqual(response.status_code, 302)
