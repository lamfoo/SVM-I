from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    form = UserProfileForm
    can_delete = False
    verbose_name_plural = 'Perfil de Usuário'

class UserProfileAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_nip')

    def get_nip(self, obj):
        return obj.userprofile.nip
    get_nip.short_description = 'NIP'

# Registra a versão personalizada do UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
