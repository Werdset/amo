from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import telegram
import openai  
import json


bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
openai.api_key = settings.OPENAI_API_KEY  

def generate_response(input_text):
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo", 
            prompt=input_text,
            max_tokens=150  
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Произошла ошибка при обработке вашего запроса: {str(e)}"

@csrf_exempt
def telegram_webhook(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Только POST запросы"})

    try:
        update = telegram.Update.de_json(json.loads(request.body.decode('utf-8')), bot)
        message = update.message or update.edited_message
        if message and message.text:
            chat_id = message.chat.id
            response_text = generate_response(message.text)
            bot.send_message(chat_id=chat_id, text=response_text)
            return JsonResponse({"status": "ok"})
        else:
            return JsonResponse({"status": "error", "message": "Получено неподдерживаемое сообщение"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Ошибка: {str(e)}"})
