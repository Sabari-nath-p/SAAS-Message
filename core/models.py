from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        abstract = True

class User(AbstractUser, SoftDeleteModel):
    is_client_admin = models.BooleanField(default=False)
    is_super_admin = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.email