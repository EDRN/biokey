# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: users.'''

from .constants import MAX_UID_LENGTH, MAX_EMAIL_LENGTH, MAX_PHONE_LENGTH
from django.db import models


class PendingUser(models.Model):
    uid = models.CharField(max_length=MAX_UID_LENGTH)
    fn = models.CharField(max_length=128)
    ln = models.CharField(max_length=128)
    phone = models.CharField(max_length=MAX_PHONE_LENGTH)
    email = models.EmailField(max_length=MAX_EMAIL_LENGTH)
    created_at = models.DateTimeField(auto_now_add=True)
    page = models.ForeignKey(
        'jpledrnbiokeyusermgmt.DirectoryInformationTree', blank=True, null=True, on_delete=models.CASCADE,
        related_name='pending_users'
    )
    def __str__(self):
        return self.uid
    class Meta:
        indexes = [models.Index(fields=['created_at'])]
        ordering = ['created_at']
