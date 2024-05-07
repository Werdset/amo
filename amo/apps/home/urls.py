from django.urls import path
from . import views, bot

urlpatterns = [
    path('webhook/<int:pk>/', bot.telegram_webhook, name='company_detail')
]