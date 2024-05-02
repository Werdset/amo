from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import telegram
import openai
from amo import settings


bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
openai.api_key = settings.OPENAI_API_KEY


def generate_response(input_text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=input_text,
        max_tokens=50
    )
    return response.choices[0].text.strip()


@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        update = telegram.Update.de_json(request.body.decode('utf-8'), bot)
        chat_id = update.message.chat.id
        message_text = update.message.text

        response = generate_response(message_text)
        bot.send_message(chat_id=chat_id, text=response)

        return JsonResponse({"status": "ok"})
    else:
        return JsonResponse({"status": "error", "message": "Только Post Запросы"})


