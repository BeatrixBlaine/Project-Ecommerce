import json

from django.http import JsonResponse

from .models import Subscriber

def api_add_subcriber(request):
    data = json.loads(request.body)
    email = data['email']

    s = Subscriber.objects.create(email=email)

    return JsonResponse({'success': True})