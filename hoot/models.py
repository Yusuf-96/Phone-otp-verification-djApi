from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class UserPhoneNumber(models.Model):
    phone_number = PhoneNumberField()
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
