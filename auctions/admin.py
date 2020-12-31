from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . models import User, Listing, Bid, Comment, watchlist

# Register your models here.
admin.site.register(Listing)
admin.site.register(Comment)
admin.site.register(watchlist)
admin.site.register(User)
admin.site.register(Bid)

