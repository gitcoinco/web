from dashboard.models import ProfileVerification, Profile
from django.utils import timezone
from app.settings import PHONE_SALT
import hashlib

handle = 'owocki'
phone = '1234567809'

profile = Profile.objects.get(handle=handle)
hash_number = hashlib.pbkdf2_hmac('sha256', phone.encode(), PHONE_SALT.encode(), 100000).hex()
ProfileVerification.objects.create(profile=profile,
                                   caller_type="MANUAL",
                                   carrier_error_code="MANUAL",
                                   mobile_network_code="NA",
                                   mobile_country_code="1",
                                   carrier_name="NA",
                                   carrier_type="NA",
                                   country_code="NA",
                                   phone_number=hash_number,
                                   delivery_method="NA")


profile.last_validation_request = timezone.now()
profile.sms_verification = True
profile.save()
