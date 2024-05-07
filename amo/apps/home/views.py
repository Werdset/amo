import telegram
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .amo_wrapper import AmoCRMWrapper
from .models import Company

amo_wrapper = AmoCRMWrapper()


def authenticate(request, pk):
    # Получаем объект Company из базы данных по идентификатору pk
    try:
        company = Company.objects.get(pk=pk)
    except Company.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Company does not exist"})

    # Используем данные из объекта Company для аутентификации в amoCRM
    authenticated = amo_wrapper.authenticate(company.amo_client_id, company.amo_client_secret, company.amo_redirect_url)

    if authenticated:
        return JsonResponse({"status": "success", "message": "Successfully authenticated with amoCRM"})
    else:
        return JsonResponse({"status": "error", "message": "Failed to authenticate with amoCRM"})




