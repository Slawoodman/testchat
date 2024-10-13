from django.contrib import admin
from .models import Thread, Message


class ThreadAdmin(admin.ModelAdmin):
    list_display = ["id", "created", "updated"]
    filter_horizontal = ("participants",)


class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "sender", "thread", "created", "is_read"]
    list_filter = ["is_read"]


admin.site.register(Thread, ThreadAdmin)
admin.site.register(Message, MessageAdmin)
