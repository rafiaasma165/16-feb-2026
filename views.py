from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import UserProfile
from claims.models import Organization
from .serializers import (UserProfileSerializer, UserDetailSerializer, UserUpdateSerializer, 
                          PasswordChangeSerializer, UserRegistrationSerializer, 
                          LoginSerializer, UserSerializer)

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserDetailSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrganizationUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, org_id):
        """Get all users in an organization"""
        if not request.user.is_superuser:
            # Check if user belongs to this organization
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                if user_profile.organization.id != int(org_id):
                    return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
            except UserProfile.DoesNotExist:
                return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            organization = Organization.objects.get(id=org_id)
            users = UserProfile.objects.filter(organization=organization)
            serializer = UserProfileSerializer(users, many=True)
            return Response(serializer.data)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

class UserRegistrationView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        user_data = UserSerializer(user).data
        
        return Response({
            'token': token.key,
            'user': user_data
        })