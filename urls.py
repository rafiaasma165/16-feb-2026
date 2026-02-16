from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, UserViewSet, OrganizationUsersView, UserRegistrationView, LoginView

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='userprofile')
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('organization/<int:org_id>/users/', OrganizationUsersView.as_view(), name='organization-users'),
]
