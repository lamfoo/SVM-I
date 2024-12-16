from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import UserProfile

class NIPAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Tenta autenticar com o username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                # Tenta autenticar com o nip
                profile = UserProfile.objects.get(nip=username)
                user = profile.user
            except UserProfile.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None
