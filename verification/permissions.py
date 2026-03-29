from rest_framework.permissions import BasePermission

class IsVerified(BasePermission):
    """
    The Bouncer: Allows access ONLY to users whose verification_status is 'verified'.
    """
    message = {
        "error": "verification_required",
        "detail": "You must verify your identity before booking or listing items.",
        "redirect": "/verify"
    }

    def has_permission(self, request, view):
        # 1. Are they logged in?
        if not request.user or not request.user.is_authenticated:
            return False
        # 2. Are they verified?
        return request.user.userprofile.verification_status == 'verified'