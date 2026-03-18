from django.contrib import admin
from .models import *

admin.site.register(Genre)
admin.site.register(Anime)
admin.site.register(SeasonAnime)
admin.site.register(Episode)
admin.site.register(Character)
admin.site.register(Bookmark)
admin.site.register(BackgroundPicture)
<<<<<<< HEAD
admin.site.register(WatchHistory)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustemUser

@admin.register(CustemUser)
class CustomUserAdmin(UserAdmin):
    model = CustemUser
    list_display = ['username', 'email', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Доп. поля', {'fields': ('avatar', 'description')}),
    )
=======
admin.site.register(WatchHistory)
>>>>>>> ec2a4da0743c3521977992317cb1844b7d3a3a10
