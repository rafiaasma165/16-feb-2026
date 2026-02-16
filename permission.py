from rest_framework import permissions
from user.models import UserProfile

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsOrgAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'org_admin'

class IsRegionManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'region_manager'

class IsPracticeUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'practice_user'

class HasOrganizationAccess(permissions.BasePermission):
    """
    Custom permission to only allow access to objects related to the user's organization.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        if not hasattr(request.user, 'userprofile') or not request.user.userprofile.organization:
            return False
            
        user_org = request.user.userprofile.organization
        
        if hasattr(obj, 'organization'):
            return obj.organization == user_org
        elif hasattr(obj, 'practice'):
            return obj.practice.organization == user_org
        elif hasattr(obj, 'patient'):
            return obj.patient.practice.organization == user_org
        elif hasattr(obj, 'claim'):
            return obj.claim.patient.practice.organization == user_org
            
        return False

class HasRegionAccess(permissions.BasePermission):
    """
    Custom permission for region-based access control.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        if not hasattr(request.user, 'userprofile'):
            return False
            
        user_profile = request.user.userprofile
        
        # Org admins can access all regions in their organization
        if user_profile.role == 'org_admin' and user_profile.organization:
            if hasattr(obj, 'organization'):
                return obj.organization == user_profile.organization
            elif hasattr(obj, 'practice') and obj.practice.organization:
                return obj.practice.organization == user_profile.organization
        
        # Region managers can only access their assigned region
        if user_profile.role == 'region_manager' and user_profile.region:
            if hasattr(obj, 'region'):
                return obj.region == user_profile.region
            elif hasattr(obj, 'practice') and obj.practice.region:
                return obj.practice.region == user_profile.region
                
        return False