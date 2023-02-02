from django.urls import path
from . import views
from .views import getPhoneNumberRegistered, getPhoneNumberRegistered_TimeBased


urlpatterns = [
    path("", views.getRoutes),
    path("<phone_number>", getPhoneNumberRegistered.as_view(), name="OTP Gen"),
    path(
        "time-based/<phone_number>",
        getPhoneNumberRegistered_TimeBased.as_view(),
        name="OTP Gen Time Based",
    ),
]
