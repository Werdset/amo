import telegram
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .amo_wrapper import AmoCRMWrapper
from ... import settings

base_url = "https://your_domain.amocrm.ru"
client_id = "client_id"
client_secret = "client_secret"
redirect_uri = "redirect_uri"
bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
amo_wrapper = AmoCRMWrapper(base_url, client_id, client_secret, redirect_uri)

username = "username"
password = "password"


def authenticate(request):
    authenticated = amo_wrapper.authenticate(username, password)
    if authenticated:
        print("Успещно!")
    else:
        print("Отклонено!")


def respond_to_customer(message):
    # Your logic to generate response to customer's message
    # For simplicity, let's just return a static response
    return "Hello! How can I assist you today?"


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        update = telegram.Update.de_json(request.body, bot)
        chat_id = update.message.chat_id
        message_text = update.message.text
        response_text = respond_to_customer(message_text)
        bot.send_message(chat_id=chat_id, text=response_text)
    return HttpResponse('')
