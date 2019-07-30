from django.contrib import admin
from mybook.models import UserProfile, BookData, ListBook

admin.site.register(UserProfile)
admin.site.register(BookData)
admin.site.register(ListBook)
