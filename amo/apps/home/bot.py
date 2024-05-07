from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import telegram
import openai

from .amo_wrapper import AmoCRMWrapper
from .models import Company, OpenAi


@csrf_exempt
def telegram_webhook(request, pk):
    if request.method == "POST":
        try:
            company = Company.objects.get(pk=pk)
            bot_token = company.telegram_bot_token
            bot = telegram.Bot(token=bot_token)

            openai_obj = OpenAi.objects.first()
            openai_api_key = openai_obj.openai_api
            openai.api_key = openai_api_key

            update = telegram.Update.de_json(request.body.decode('utf-8'), bot)
            chat_id = update.message.chat.id
            message_text = update.message.text
            if f"{company.create_deal}" in message_text.lower():
                create_deal(company)
                response = "Сделка успешно создана в amoCRM"
            elif f"{company.create_contact}" in message_text.lower():
                bot.send_message(chat_id=chat_id,
                                 text="Введите имя, email и телефон контакта в формате: <Имя> <Email> <Телефон>")
            elif message_text.startswith('<'):
                parts = message_text.split()
                if len(parts) == 4:
                    name = parts[1]
                    email = parts[2]
                    phone = parts[3]

                    # Создаем данные для нового контакта
                    contact_data = {"name": name, "email": email, "phone": phone}

                    # Создаем экземпляр AmoCRMWrapper и создаем контакт
                    amo_wrapper = AmoCRMWrapper(company.id)
                    amo_wrapper.create_contact(contact_data)

                    response = "Контакт успешно создан в amoCRM"
            else:
                response = generate_response(company, message_text, openai_api_key)

            bot.send_message(chat_id=chat_id, text=response)

            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Только Post Запросы"})


def generate_response(input_text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=input_text,
        max_tokens=50
    )
    return response.choices[0].text.strip()


def create_deal(company):
    amo_wrapper = AmoCRMWrapper(company.id)
    deal_data = {"title": "Новая сделка", "description": "Описание сделки", "amount": 1000, "status": "В работе"}
    amo_wrapper.create_deal(deal_data)