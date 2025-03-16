from django.contrib import admin
from .models import Post, Category, Location

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Location)
admin.site.empty_value_display = 'Не задано'
