from django.contrib import admin
from .models import *

admin.site.register(Genre)
admin.site.register(Anime)
admin.site.register(SeasonAnime)
admin.site.register(Episode)
admin.site.register(Character)
admin.site.register(Bookmark)
admin.site.register(BackgroundPicture)
admin.site.register(WatchHistory)
admin.site.register(Comments)


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

