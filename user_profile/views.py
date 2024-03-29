from django.contrib.auth.models import User
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import LimitOffsetPagination

from django.shortcuts import render
import pytz


# Create your views here.
#login rest framework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework.decorators import action

from rest_framework import serializers
from streamers.models import Streamer
from trivias.models import TriviaGame
from trivias.serializer import TriviaGameSerializer

from wallet.serializer import WalletSerializer
from countries.serializers import CountrySerializer, AddressSerializer
from streamers.serializers import StreamerSerializer
from countries.models import Address
from .serializer import CompleteRegisterSerializer
import json
from django.db.models import Q

#login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from user_profile.models import Profile
from user_profile.serializer import UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_email
from django.contrib.sessions.models import Session
from datetime import datetime, timezone
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from notifications.models import Notification

from user_profile.serializer import CommonFriendsSerializer, UserSerializer
class CommonFriendsViewSet(ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = CommonFriendsSerializer
    pagination_class = LimitOffsetPagination
    default_limit = 25

    def get_queryset(self):
        # Get the current user
        current_user = User.objects.select_related('profile').get(pk=self.request.user.id)
        # Get the users that the current user is following
        following = current_user.profile.following.all()

        # Get the users that are following the current user
        followers = current_user.profile.followers.all()

        # Filter the users that are friends (follow and are followed)
        friends = followers.filter(pk__in=following)

        # Get the basic information of the friends
        friends_info = UserSerializer(friends, many=True).data

        # Get the total count of common friends
        common_friends_count = friends.count()

        # Get the 3 most recent friends
        recent_friends = friends.order_by('-date_joined')[:3]

        # Serialize the information of the recent friends
        recent_friends_info = UserSerializer(recent_friends, many=True).data

        # Subtract the displayed friends from the total count
        common_friends_count -= len(recent_friends)

        # Create the response
        response = {
            "user_common_info": recent_friends_info,
            "user_common_count": common_friends_count,
            "user_friends": friends_info,
        }

        return response
    

#login
class Login(ObtainAuthToken):
    def post(self,request,*args,**kwargs):
        try:
            validate_email(request.data['username'])
            valid_email = True
        except:
            valid_email = False
        if valid_email:
            try:
                user = User.objects.get(email=request.data['username'])
                request.data['username'] = user.username
            except ObjectDoesNotExist:
                return Response({'error':'Correo no registrado'}, status=status.HTTP_400_BAD_REQUEST)
            

        login_serializer = self.serializer_class(data = request.data, context = {'request':request})
        if login_serializer.is_valid():
            user = login_serializer.validated_data['user']
            token,created = Token.objects.get_or_create(user = user)

            if user.is_active:
                userData =  UserSerializer(user).data
                userData['wallet'] = WalletSerializer(user.wallet).data
                userData['country'] = CountrySerializer(user.profile.country).data
                if user.profile.is_streamer:
                    userData['streamer'] = StreamerSerializer(user.profile.streamer).data

                if created:
                    return Response({
                        'token': token.key,
                        'user': userData,
                        'message': 'Inicio Exitóso',
                    }, status = status.HTTP_200_OK)
                else:
                    token.delete()
                    token = Token.objects.create(user = user)


                    return Response({
                        'token': token.key,
                        'user':userData,
                        'message': 'Inicio Exitóso',
                    }, status = status.HTTP_200_OK)

            else:
                return Response({'error':'Su usuario ha sido suspendido'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error':'Usuario o contraseña incorrecta'}, status=status.HTTP_400_BAD_REQUEST)

    
class Logout(APIView):
    def post(self,request,*args,**kwargs):
        token = request.GET.get('token', '1')
        token = Token.objects.filter(key = token).first()

        if token:
            user = token.user

            all_sessions = Session.objects.filter(expire_date__gte = datetime.now())
            if all_sessions.exists():
                for session in all_sessions:
                    session_data = session.get_decoded()
                    if user.id == int(session_data.get('_auth_user_id')):
                        session.delete()
            
            token.delete()

            session_message = 'Sesión cerrada'
            token_message = 'Token eliminado'
            return Response(
                {'session_message':session_message, 'token_message':token_message},
                status = status.HTTP_200_OK)
        else:
            return Response(
                {'error':'No se ha encontrado usuario con estas credenciales'},
                status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success':'Register Success'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True,methods=['post'])
    def addFollow(self,request,pk=None):
        user_to_follow = User.objects.select_related('profile').get(pk=pk)
        if not user_to_follow:
            return Response({'error':'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.select_related('profile').get(pk=request.user.id)
        user.profile.add_new_following(user_to_follow.profile)
        user_to_follow.profile.add_new_follower(user.profile)
        
        Notification.objects.create(
            user = user_to_follow,
            notification = "El usuarios "+user.username+" te ha seguido",        
            type_motification = "follow",
        )
        return Response({'success':'Usuario seguido'}, status=status.HTTP_200_OK)
    
    @action(detail=True,methods=['post'])
    def addFollower(self,request,pk=None):
        
        user_to_follow = User.objects.select_related('profile').get(pk=pk)
        if not user_to_follow:
            return Response({'error':'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.select_related('profile').get(pk=request.user.id)
        user.profile.add_new_follower(user_to_follow.profile)
        user_to_follow.profile.add_new_following(user.profile)
        
        Notification.objects.create(
            user = user_to_follow,
            notification = "El usuarios "+user.username+" te ha seguido",        
            type_motification = "follow",
        )
        return Response({'success':'Usuario seguido'}, status=status.HTTP_200_OK)