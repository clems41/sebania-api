from rest_framework import permissions


class HasResponsablePermission(permissions.BasePermission):
    message = "Seuls les responsables d'exploitations ont accès à cette url."

    def has_permission(self, request, view):
        group_name = 'RESPONSABLE'
        if request.user.groups.filter(name__exact=group_name).exists() or request.user.is_superuser:
            return True

        return False