from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    notification = models.TextField()
    url = models.CharField(max_length=255,default='x')
    type_motification = models.CharField(max_length=10,default='app')
    readed = models.BooleanField(default=False)
    created_at = models.DateTimeField(editable=False,default='2020-06-29')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        return super(Notification, self).save(*args, **kwargs)    
    class Meta:
        ordering = ['-id']
@receiver(post_save,sender=Notification)
def notifications_push(sender,instance,created,**kwargs):
    if created:
        channel_layer = get_channel_layer()
        day = naturaltime(instance.created_at)
        data = {
			'id': instance.id,
			'type': instance.type_motification,
			'timeago': str(day),
	    	'message' : instance.notification,  # Pass any data based on your requirement
	       	"url": instance.url, #str(reverse_lazy('cargar-video', kwargs={'pk':1}))
		}		# Trigger message sent to group
        async_to_sync(channel_layer.group_send)(
			'noti-' + str(instance.user.pk),  # Group Name, Should always be string
			{
				"type": "notify",   # Custom Function written in the consumers.py
				"text": data,
			},
		)  	



class DeviceToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=800)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token