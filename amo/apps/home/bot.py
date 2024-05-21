import json
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import openai
import requests
from amocrm.v2 import Contact, Company as Comp, Lead, tokens
from .models import Company, OpenAi
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY


@csrf_exempt
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
                    elif update['text'] == '/settings':
                        setting(update, pk)
                    # Проверяем, есть ли в сообщении видео
                    elif update['text'] == f'{company.create_deal}':
                        create_deal(update, pk)
                    elif update['text'] == f'{company.create_contact}':
                        create_contact(update, pk)
                    elif update['text'].startswith('<'):
                        contacty(update, pk)
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
    # Аутентификация компании

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


def openai_generate(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[

                {
                    "role": "system",
                    "content": "Ты - ИИ-турагент, задача которого состоит в первичной квалификации обращений. Твоя задача узнать в какую страну и город хочет полететь клиент, какой у него бюджет, из какого города он будет вылетать, на сколько дней он планирует поездку, какие даты вылета клиент рассматривает удобными для него, сколько человек летит вместе с ним и есть ли у него дети которые полетят с ним, а также дополнительные пожелания. После чего на основе полученных данных найти подходящие варианты туров на сайте https://tourvisor.ru/ и предоставить их клиенту."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],

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
