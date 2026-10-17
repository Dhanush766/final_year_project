"""
Views for the Employee Management System.

Security model
--------------
* Every page requires a logged-in user (anonymous users are sent to /login/).
* Every page also requires a Django permission. Superusers have all of them.
  - viewing  : employees.view_employee / employees.view_department
  - adding   : employees.add_employee  / employees.add_department
  - editing  : employees.change_employee / employees.change_department
  - deleting : employees.delete_employee / employees.delete_department
* A logged-in user without the needed permission receives a 403 page.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import (
    DepartmentForm,
    EmployeeFilterForm,
    EmployeeForm,
    StyledAuthenticationForm,
)
from .models import Department, Employee

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
class SecureViewMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Login + permission check. Subclasses set `permission_required`."""


class FormFeedbackMixin:
    """Shows a success or error message after a form is submitted."""

    success_message = ""
    error_message = "Please correct the errors highlighted below."

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message.format(obj=self.object))
        return response

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
class AppLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Welcome back, {form.get_user().get_username()}!")
        return response


class AppLogoutView(LogoutView):
    """Logout (POST only, as required by Django 5) with a confirmation message."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, "You have been logged out successfully.")
        return response


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class DashboardView(SecureViewMixin, TemplateView):
    template_name = "employees/dashboard.html"
    permission_required = "employees.view_employee"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total = Employee.objects.count()
        active = Employee.objects.filter(status=Employee.Status.ACTIVE).count()
        status_counts = dict(
            Employee.objects.order_by().values_list("status").annotate(total=Count("id"))
        )

        departments = Department.objects.annotate(
            total=Count("employees"),
            active=Count("employees", filter=Q(employees__status=Employee.Status.ACTIVE)),
        ).order_by("-total", "name")

        context.update(
            total_employees=total,
            active_employees=active,
            inactive_employees=total - active,
            department_count=Department.objects.count(),
            department_stats=[
                {
                    "name": dept.name,
                    "total": dept.total,
                    "active": dept.active,
                    "percent": round(dept.total * 100 / total) if total else 0,
                }
                for dept in departments
            ],
            status_breakdown=[
                {"label": label, "count": status_counts.get(value, 0), "value": value}
                for value, label in Employee.Status.choices
            ],
            recent_employees=Employee.objects.select_related("department").order_by(
                "-created_at", "-id"
            )[:5],
        )
        return context


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------
class EmployeeListView(SecureViewMixin, ListView):
    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"
    paginate_by = 10
    permission_required = "employees.view_employee"

    def get_queryset(self):
        queryset = Employee.objects.select_related("department")
        self.filter_form = EmployeeFilterForm(self.request.GET)
        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            query = data.get("q")
            if query:
                queryset = queryset.filter(
                    Q(full_name__icontains=query) | Q(employee_id__icontains=query)
                )
            if data.get("department"):
                queryset = queryset.filter(department=data["department"])
            if data.get("status"):
                queryset = queryset.filter(status=data["status"])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context["filter_form"] = self.filter_form
        context["querystring"] = params.urlencode()
        context["result_count"] = context["paginator"].count
        return context


class EmployeeDetailView(SecureViewMixin, DetailView):
    model = Employee
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"
    permission_required = "employees.view_employee"

    def get_queryset(self):
        return Employee.objects.select_related("department")


class EmployeeCreateView(SecureViewMixin, FormFeedbackMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    permission_required = "employees.add_employee"
    success_url = reverse_lazy("employees:employee_list")
    success_message = "Employee {obj} was added successfully."
    extra_context = {"form_title": "Add New Employee"}


class EmployeeUpdateView(SecureViewMixin, FormFeedbackMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    permission_required = "employees.change_employee"
    success_message = "Employee {obj} was updated successfully."
    extra_context = {"form_title": "Edit Employee"}

    def get_success_url(self):
        return reverse("employees:employee_detail", kwargs={"pk": self.object.pk})


class EmployeeDeleteView(SecureViewMixin, FormFeedbackMixin, DeleteView):
    model = Employee
    template_name = "employees/employee_confirm_delete.html"
    context_object_name = "employee"
    permission_required = "employees.delete_employee"
    success_url = reverse_lazy("employees:employee_list")
    success_message = "Employee {obj} was deleted."

    def get_queryset(self):
        return Employee.objects.select_related("department")


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------
class DepartmentListView(SecureViewMixin, ListView):
    model = Department
    template_name = "employees/department_list.html"
    context_object_name = "departments"
    permission_required = "employees.view_department"

    def get_queryset(self):
        return Department.objects.annotate(employee_count=Count("employees"))


class DepartmentCreateView(SecureViewMixin, FormFeedbackMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "employees/department_form.html"
    permission_required = "employees.add_department"
    success_url = reverse_lazy("employees:department_list")
    success_message = "Department {obj} was created successfully."
    extra_context = {"form_title": "Add New Department"}


class DepartmentUpdateView(SecureViewMixin, FormFeedbackMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = "employees/department_form.html"
    permission_required = "employees.change_department"
    success_url = reverse_lazy("employees:department_list")
    success_message = "Department {obj} was updated successfully."
    extra_context = {"form_title": "Edit Department"}


class DepartmentDeleteView(SecureViewMixin, FormFeedbackMixin, DeleteView):
    model = Department
    template_name = "employees/department_confirm_delete.html"
    context_object_name = "department"
    permission_required = "employees.delete_department"
    success_url = reverse_lazy("employees:department_list")
    success_message = "Department {obj} was deleted."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["employee_count"] = self.object.employees.count()
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            logger.info("Blocked deletion of department %s: it still has employees.", self.object)
            messages.error(
                self.request,
                f'Department "{self.object}" cannot be deleted because it still has '
                "employees. Move or delete those employees first.",
            )
            return redirect("employees:department_list")
