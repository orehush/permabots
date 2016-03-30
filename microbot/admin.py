from django.contrib import admin
from microbot.models import Message, Chat, Update, User, Bot, Handler, EnvironmentVar, Request, Response, Hook, \
    UrlParam, HeaderParam, Recipient, State, ChatState

admin.site.register(Message)
admin.site.register(Chat)
admin.site.register(User)
admin.site.register(Update)
admin.site.register(Bot)
admin.site.register(Handler)
admin.site.register(Request)
admin.site.register(EnvironmentVar)
admin.site.register(Response)
admin.site.register(Hook)
admin.site.register(UrlParam)
admin.site.register(HeaderParam)
admin.site.register(Recipient)
admin.site.register(State)
admin.site.register(ChatState)