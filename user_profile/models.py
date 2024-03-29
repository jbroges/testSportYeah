from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

class Profile(models.Model):    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField('self', related_name='followers', symmetrical=False)
    following = models.ManyToManyField('self', related_name='following', symmetrical=False)
    thumbnail = models.ImageField(upload_to='profile_pics', default='default.jpg')
    create_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}'s profile"

    def add_new_following(self, profile):
        self.following.add(profile)
    
    def add_new_follower(self, profile):
        self.followers.add(profile)

    def unfollow(self, profile):
        self.following.remove(profile)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)