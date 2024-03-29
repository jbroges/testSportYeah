from rest_framework import serializers
from user_profile.models import Profile
from django.contrib.auth.models import User

#serializer for user_profile ands user
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)
    class Meta:
        model = User
        fields = ('id','username', 'email', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.update_or_create(user=user, defaults=profile_data)
        return user
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile        
        profile.thumbnail = profile_data.get('thumbnail', profile.thumbnail)
        instance.save()
        profile.save()
        return instance

class CommonFriendsSerializer(serializers.Serializer):
    user_common_info = UserSerializer(many=True)
    user_common_count = serializers.IntegerField()    