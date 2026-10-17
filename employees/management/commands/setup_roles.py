"""Creates two ready-made user groups ("roles") with the right permissions."""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

MODELS = ("employee", "department")
ROLES = {
    "HR Manager": ("view", "add", "change", "delete"),
    "Viewer": ("view",),
}


class Command(BaseCommand):
    help = (
        "Create the 'HR Manager' (full access) and 'Viewer' (read-only) groups. "
        "Run it after `migrate`. It is safe to run more than once."
    )

    def handle(self, *args, **options):
        for role, actions in ROLES.items():
            codenames = [f"{action}_{model}" for action in actions for model in MODELS]
            permissions = Permission.objects.filter(
                content_type__app_label="employees", codename__in=codenames
            )
            group, created = Group.objects.get_or_create(name=role)
            group.permissions.set(permissions)
            state = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(f"{state} group '{role}' with {permissions.count()} permissions.")
            )
        self.stdout.write(
            "Assign users to these groups in the Django Admin (Users > choose a user > Groups)."
        )
