from django.shortcuts import render, HttpResponse
from pyfcm import FCMNotification
from .models import DeviceToken
import os
import shutil
from django.conf import settings

def SendPush(request):
    if request.method == 'POST':
        # Obtén la lista de tokens de registro de los dispositivos desde el formulario.
        device_tokens = []
        for device_token in DeviceToken.objects.all():
            device_tokens.append(device_token.token)
        

        # Crea un mensaje para la notificación push.
        message = {
            'title': '¡Nueva notificación push!',
            'message': 'Este es un mensaje de prueba para la notificación push.',
            'icon': 'https://www.familiamillonaria.com/logo.png',
            'url': 'https://www.familiamillonaria.com/',
        }

        # Envía la notificación push a través de Firebase Cloud Messaging.
        push_service = FCMNotification(api_key=settings.FIREBASE_CLOUD_MESSAGING_CONFIG['API_KEY'])
        result = push_service.notify_multiple_devices(registration_ids=device_tokens, data_message=message)
    return HttpResponse('listo')

def addDeviceToken(request):
    if request.method == 'POST':
        # Obtén el token de registro del dispositivo desde el formulario.
        device_token = request.POST.get('device_token')

        # Guarda el token de registro del dispositivo en la base de datos.
        if device_token:
            if not DeviceToken.objects.filter(token=device_token).exists():
                DeviceToken.objects.create(token=device_token,user=request.user)
            else:
                return HttpResponse('Ya estás suscrito a las notificaciones de tus partidas.')
        # ...
        else:
            return HttpResponse('No se pudo suscribir a las notificaciones de tus partidas.')
        return HttpResponse('Ahora recibirás notificaciones de tus partidas.')
import time
def CreateServiceWorker(request):
    # Obtiene la ruta del archivo de Service Worker para el usuario actual.
    file_path = os.path.join('/opt','familiamillonaria', 'static_files', 'js', 'servicesusers', f'service-worker-{request.user.id}.js')
    # Verifica si el archivo de Service Worker ya existe.
    if os.path.exists(file_path):
        # El archivo ya existe, no es necesario crearlo de nuevo.
        return HttpResponse('listo')
    else:
        # El archivo no existe, copia el archivo original y cambia su nombre.
        original_file_path = os.path.join('/opt','familiamillonaria', 'static_files', 'js', 'servicesusers', 'service-worker.js')
        shutil.copyfile(original_file_path, file_path)
        time.sleep(1)
        return HttpResponse('listo')