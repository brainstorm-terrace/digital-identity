from django.db import models
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

class UserDetail(models.Model):

    #Fields
    user_id = models.CharField(unique=True, max_length=50)
    user_name = models.CharField(unique=True, max_length=50)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    linked_in_profile = models.URLField(max_length=200)
    facebook_profile = models.URLField(max_length=200)
    region = models.CharField(max_length=255)
    city  = models.CharField(max_length=100)
    country = models.CharField(max_length=64)
    pincode = models.IntegerField

    phone_no = PhoneNumberField(null=True)
    dob = models.DateField(null=True)

    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()

    gender = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        """ On save, update timestamps of created_on and updated_at fields"""
        if not self.id:
            self.created_on = timezone.now()
        self.updated_at = timezone.now()
        return super(UserDetail, self).save(*args, **kwargs)

    def __str__(self):
        return self.user_name
