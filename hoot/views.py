from django.shortcuts import render, HttpResponse
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserPhoneNumber
from rest_framework.decorators import action
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import pyotp
from rest_framework.views import APIView
import base64



from .serializers import UserSerializer
# from .utils import send_otp


@api_view(["GET"])
def getRoutes(request):
    routes = [
        {
            "register": {"POST": "api/register"},
        },
        {
            "hoot": {"GET POST ": "api/posts"},
        },
    ]
    return Response(routes)


# This class returns the string needed to generate the key
class generateKey:
    @staticmethod
    def returnValue(phone_number):
        return str(phone_number) + str(datetime.date(datetime.now())) + "Some Random Secret Key"


class getPhoneNumberRegistered(APIView):
    # Get to Create a call for OTP
    @staticmethod
    def get(request, phone_number):
        try:
            phone_number = UserPhoneNumber.objects.get(phone_number=phone_number)  # if Mobile already exists the take this else create New One
        except ObjectDoesNotExist:
            UserPhoneNumber.objects.create(
                phone_number=phone_number,
            )
            phone_number = UserPhoneNumber.objects.get(phone_number=phone_number)  # user Newly created Model
        phone_number.counter += 1  # Update Counter At every Call
        phone_number.save()  # Save the data
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone_number).encode())  # Key is generated
        OTP = pyotp.HOTP(key)  # HOTP Model for OTP is created
        print(OTP.at(phone_number.counter))
        # Using Multi-Threading send the OTP Using Messaging Services like Twilio or Fast2sms
        return Response({"OTP": OTP.at(phone_number.counter)}, status=200)  # Just for demonstration

    # This Method verifies the OTP
    @staticmethod
    def post(request, phone_number):
        try:
            phone_number = UserPhoneNumber.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
            return Response("User does not exist", status=404)  # False Call

        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone_number).encode())  # Generating Key
        OTP = pyotp.HOTP(key)  # HOTP Model
        if OTP.verify(request.data["otp"], phone_number.counter):  # Verifying the OTP
            phone_number.isVerified = True
            phone_number.save()
            return Response("You are authorised", status=200)
        return Response("OTP is wrong", status=400)


# Time after which OTP will expire
EXPIRY_TIME = 50 # seconds

class getPhoneNumberRegistered_TimeBased(APIView):
    # Get to Create a call for OTP
    @staticmethod
    def get(request, phone_number):
        try:
            phone_number = UserPhoneNumber.objects.get(phone_number=phone_number)  # if Mobile already exists the take this else create New One
        except ObjectDoesNotExist:
            UserPhoneNumber.objects.create(
                phone_number=phone_number,
            )
            phone_number = UserPhoneNumber.objects.get(phone_number=phone_number)  # user Newly created Model
        phone_number.save()  # Save the data
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone_number).encode())  # Key is generated
        OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model for OTP is created
        print(OTP.now())
        # Using Multi-Threading send the OTP Using Messaging Services like Twilio or Fast2sms
        return Response({"OTP": OTP.now()}, status=200)  # Just for demonstration

    # This Method verifies the OTP
    @staticmethod
    def post(request, phone_number):
        try:
            phone_number = UserPhoneNumber.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
            return Response("User does not exist", status=404)  # False Call

        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone_number).encode())  # Generating Key
        OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model 
        if OTP.verify(request.data["otp"]):  # Verifying the OTP
            phone_number.isVerified = True
            phone_number.save()
            return Response("You are authorised", status=200)
        return Response("OTP is wrong/expired", status=400)


# @api_view(["POST"])
# def registerView(request):
#     if request.method == "POST":
#         serializer = UserPhoneNumberSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def userView(request):
    if request.method == "POST":
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# class UserView(generics.CreateAPIView):
#     queryset = UserPhoneNumber.objects.all()
#     serializer_class = UserSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)

#         # Send OTP via SMS
#         phone_number = serializer.data.get('phone_number')
#         totp = pyotp.TOTP("base32secret3232")
#         verification_code = totp.now()
#         otp = send_otp(verification_code, phone_number)
#         UserPhoneNumber.objects.filter(phone_number=phone_number).update(otp=otp)

#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@api_view(["POST"])
def verifyOTP(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        user = UserPhoneNumber.objects.filter(otp=otp).first()
        if user:
            user.is_verified = True
            user.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(generics.RetrieveUpdateAPIView):
    queryset = UserPhoneNumber.objects.all()
    serializer_class = UserSerializer

    @action(methods=["patch"], detail=False)
    def verify_otp(self, request):
        phone_number = request.data.get("phone_number")
        otp = request.data.get("otp")

        try:
            user = UserPhoneNumber.objects.get(
                phone_number=phone_number, otp=otp, is_verified=False
            )
            user.is_verified = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        except UserPhoneNumber.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
