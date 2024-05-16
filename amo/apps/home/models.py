from django.db import models
from django.urls import reverse


class Company(models.Model):
    name = models.CharField(max_length=100)
    amo_base_url = models.CharField(max_length=100)
    amo_client_id = models.CharField(max_length=100)
    amo_client_secret = models.CharField(max_length=100)
    amo_redirect_url = models.CharField(max_length=100)
    amo_access_token = models.CharField(max_length=100, default=None)
    amo_refresh_token = models.CharField(max_length=100, default=None)
    amo_code = models.CharField(max_length=1000)
    telegram_bot_token = models.CharField(max_length=100)
    create_deal = models.CharField(max_length=100)  # Ключевое слово для добавления сделки
    create_contact = models.CharField(max_length=100)  # Ключевое слово для создания контакта

    def get_absolute_url(self):
        return reverse('company_detail', args=[str(self.id)])

    def __str__(self):
        return self.name


class OpenAi(models.Model):
    openai_api = models.CharField(max_length=100)
