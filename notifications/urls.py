from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import addDeviceToken, SendPush, CreateServiceWorker

urlpatterns = [
    path('add-token-push/', login_required(addDeviceToken), name='add-token-push'),
    path('enviar-push/', login_required(SendPush), name='enviartoken'),
    path('crear-worker/', login_required(CreateServiceWorker), name='crear-worker'),

]