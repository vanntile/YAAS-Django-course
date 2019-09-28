from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Language(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=8, default='en')


@receiver(post_save, sender=User)
def create_user_language(_, instance, created, **kwargs):
    if created:
        Language.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_language(_, instance, **kwargs):
    instance.language.save()

