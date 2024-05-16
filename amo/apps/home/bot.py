import json
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import openai
import requests
from amocrm.v2 import Contact, Lead, tokens
from .models import Company
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY


@csrf_exempt  # обработчик webhooks
def telegram_webhook(request, pk):
    company = Company.objects.get(pk=pk)
    if request.method == "POST":

        if request.method == 'POST':
            data = json.loads(request.body)
            # Проверяем, есть ли в данных сообщение
            if 'message' in data:
                update = data['message']

                # Проверяем, есть ли в сообщении текстовое сообщение
                if 'text' in update:
                    # Если текст - '/start', вызываем функцию handle_start
                    if update['text'] == '/start':
                        handle_start(update, pk)
                        # Если текст - '/start', вызываем функцию
                    elif update['text'] == '/settings':
                        setting(update, pk)
                    # Проверяем, есть ли ключевое слово для создания сделки
                    elif update['text'] == f'{company.create_deal}':
                        create_deal(update, pk)
                    # Проверяем, есть ли ключевое слово для создания контакта
                    elif update['text'] == f'{company.create_contact}':
                        create_contact(update, pk)
                        # Проверяем, есть ли данные для создания контакта
                    elif update['text'].startswith('<'):
                        contacty(update, pk)
                        # если ключевых слов нет, отправляем в чат GPT
                    else:
                        generate_response(update, pk)

                # Возвращаем ответ серверу Telegram
                return HttpResponse('Got it!')
            else:
                # Если сообщение не содержит обновлений, возвращаем ошибку
                return HttpResponse('No updates found')
        else:
            # Если метод запроса не POST, возвращаем ошибку
            return HttpResponse('Only POST requests are allowed')


def handle_start(update, pk):
    company = Company.objects.get(pk=pk)
    name = company.name
    bot_token = company.telegram_bot_token
    chat_id = update['chat']['id']
    response = {
        'chat_id': chat_id,
        'text': f"Привет! Я Telegram бот, компании {name}. Я отвечу на любой твой вопрос. Для заказа напиши мне {company.create_deal}, для заказа обратного звонка {company.create_contact}"
    }
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json=response)


def create_deal(update, pk):
    chat_id = update['chat']['id']
    company = Company.objects.get(pk=pk)
    bot_token = company.telegram_bot_token

    authenticate(company)
    deal_data = {"title": "Новая сделка", "description": "Описание сделки", "amount": 1000, "status": "В работе"}
    lead = Lead.objects.create(**deal_data)
    lead.save()

    response = {
        'chat_id': chat_id,
        'text': f"Заказ успешно создан"
    }
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json=response)


def contacty(update, pk):
    company = Company.objects.get(pk=pk)
    bot_token = company.telegram_bot_token

    # Обработка данных о контакте
    parts = update['text'].split()
    chat_id = update['chat']['id']
    if len(parts) == 4:
        name = parts[1]
        email = parts[2]
        phone = parts[3]

        # Создаем данные для нового контакта
        contact_data = {"name": name, "email": email, "phone": phone}
        # Отправка контакта в amoCRM
        authenticate(company)
        contact = Contact.objects.create(**contact_data)
        contact.save()

        # Отправка ответа пользователю в Telegram
        response = {
            'chat_id': chat_id,
            'text': "Обратный звонок заказан"
        }
        requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json=response)


def create_contact(update, pk):
    company = Company.objects.get(pk=pk)
    bot_token = company.telegram_bot_token
    chat_id = update['chat']['id']
    response = {
        'chat_id': chat_id,
        'text': "Введите имя, email и телефон контакта в формате: <Имя> <Email> <Телефон>"
    }
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json=response)


# обработка перед отправкой в openai и отправка возвращенного ответа
def generate_response(update, pk):
    company = Company.objects.get(pk=pk)
    name = company.name
    bot_token = company.telegram_bot_token
    chat_id = update['chat']['id']
    text = update['text']
    response_text = openai_generate(text)

    # Sending the completion response back to the user via Telegram
    response_data = {
        'chat_id': chat_id,
        'text': response_text
    }
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json=response_data)


# отправка запроса в openai  и возврат ответа
def openai_generate(text):
    try:
        response = openai.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": text
                }
            ],
            model="gpt-3.5-turbo-1106",
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Произошла ошибка при обработке вашего запроса: {str(e)}"


def authenticate(company):
    tokens.default_token_manager(
        client_id=company.amo_client_id,
        client_secret=company.amo_client_secret,
        subdomain=company.amo_base_url,
        redirect_url=company.amo_redirect_url,
        storage=tokens.FileTokensStorage(f"{settings.BASE_DIR}/tokens/{company.id}")

    )


def setting(update, pk):
    company = Company.objects.get(pk=pk)
    bot_token = company.telegram_bot_token
    chat_id = update['chat']['id']

    tokens_dir = f"{settings.BASE_DIR}/tokens/{company.id}"
    os.makedirs(tokens_dir, exist_ok=True)

    # Инициализация менеджера токенов
    tokens.default_token_manager(
        client_id=company.amo_client_id,
        client_secret=company.amo_client_secret,
        subdomain=company.amo_base_url,
        redirect_url=company.amo_redirect_url,
        storage=tokens.FileTokensStorage(f"{settings.BASE_DIR}/tokens/{company.id}")

    )
    tokens.default_token_manager.init(code=f"{company.amo_code}", skip_error=False)

    response_data = {
        'chat_id': chat_id,
        'text': "Получение токенов выполнено"
    }
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json=response_data)
