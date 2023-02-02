from twilio.rest import Client
import pyotp


def generate_verification_code():
    code = pyotp.random_base32()[:6]
    request.session["verification_code"] = code
    return code


def send_otp(verification_code, phone_number):
    account_sid = "YOUR_ACCOUNT_SID"
    auth_token = "YOUR_AUTH_TOKEN"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to=phone_number,
        from_="YOUR_TWILIO_PHONE_NUMBER",
        body=f"Your verification code is: {verification_code}",
    )

def verify_code(verification_code):
    stored_code = request.session.get('verification_code')
    return stored_code == verification_code
