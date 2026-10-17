"""Django Admin integration."""
from django.contrib import admin
from django.db.models import Count

from .models import Department, Employee

admin.site.site_header = "Employee Management System - Administration"
admin.site.site_title = "EMS Admin"
admin.site.index_title = "Manage departments and employees"


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "employee_count", "created_at")
    search_fields = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_employee_count=Count("employees"))

    @admin.display(description="Employees", ordering="_employee_count")
    def employee_count(self, obj):
        return obj._employee_count


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "full_name",
        "email",
        "department",
        "designation",
        "status",
        "joining_date",
    )
    list_filter = ("department", "status", "joining_date")
    search_fields = ("employee_id", "full_name", "email")
    list_select_related = ("department",)
    ordering = ("employee_id",)
    date_hierarchy = "joining_date"
    readonly_fields = ("created_at", "updated_at")
