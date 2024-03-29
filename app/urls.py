#urls
from django.urls import path
from user_profile.views import Login, Logout, register_view




urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('register/', register_view, name='register'),

]