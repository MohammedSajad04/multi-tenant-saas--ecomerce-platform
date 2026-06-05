from rest_framework.permissions import BasePermission


class IsApprovedCompany(BasePermission):

    def has_permission(
        self,
        request,
        view
    ):

        user = request.user

        if not user.is_authenticated:
            return False

        if user.role == "company_admin":

            if (
                user.tenant
                and user.tenant.status != "approved"
            ):
                return False

        return True