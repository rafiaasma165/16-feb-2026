from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import UserProfile
from claims.models import Organization

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'organization', 'organization_name', 'role', 'created_at']

class UserDetailSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'userprofile']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return value
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    organization_id = serializers.IntegerField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'organization_id')
    
    def create(self, validated_data):
        organization_id = validated_data.pop('organization_id', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        if organization_id:
            try:
                organization = Organization.objects.get(id=organization_id)
                UserProfile.objects.create(user=user, organization=organization)
            except Organization.DoesNotExist:
                pass
        
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            data['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        
        return data