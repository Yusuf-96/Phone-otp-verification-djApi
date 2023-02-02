from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from .models import UserPhoneNumber
from .utils import send_otp
import pyotp



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoneNumber
        fields = ('id', 'phone_number', 'otp', 'is_verified')
        
    def vallidate_phone_number(self, value):
        phone_number = UserPhoneNumber.objects.filter(phone_number=value).first()
        if phone_number:
            raise serializers.ValidationError("Phone Number already exists")
        return value

    def create(self, validated_data):
        phone_number = validated_data.get("phone_number")
        totp = pyotp.TOTP("base32secret3232")
        verification_code = totp.now()
        otp = send_otp(verification_code, phone_number)
        user_phone_number = UserPhoneNumber.objects.create(**validated_data)
        return user_phone_number

