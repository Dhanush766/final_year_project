"""URL patterns of the employees app (all names are namespaced as `employees:`)."""
from django.urls import path

from . import views

app_name = "employees"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    # Employees
    path("employees/", views.EmployeeListView.as_view(), name="employee_list"),
    path("employees/add/", views.EmployeeCreateView.as_view(), name="employee_add"),
    path("employees/<int:pk>/", views.EmployeeDetailView.as_view(), name="employee_detail"),
    path("employees/<int:pk>/edit/", views.EmployeeUpdateView.as_view(), name="employee_edit"),
    path("employees/<int:pk>/delete/", views.EmployeeDeleteView.as_view(), name="employee_delete"),
    # Departments
    path("departments/", views.DepartmentListView.as_view(), name="department_list"),
    path("departments/add/", views.DepartmentCreateView.as_view(), name="department_add"),
    path("departments/<int:pk>/edit/", views.DepartmentUpdateView.as_view(), name="department_edit"),
    path("departments/<int:pk>/delete/", views.DepartmentDeleteView.as_view(), name="department_delete"),
]
