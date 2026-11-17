from django.db import models


class Provider(models.Model):

    user_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name