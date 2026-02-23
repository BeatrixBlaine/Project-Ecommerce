import json
import stripe

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .cart import Cart

from apps.order.models import Order

@csrf_exempt
def webhook(request):
    payload = request.body
    event = None

    stripe.api_key = settings.STRIPE_API_KEY_HIDDEN

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        return HttpResponse(status=400)
    

    if event.type == 'checkout.session.completed':
        session = event.data.object

        try:
            order = Order.objects.get(stripe_checkout_id=session.id)
            order.payment_intent = session.payment_intent
            order.paid = True
            order.save()
            print('Payment completed:', session.payment_intent)
        except Order.DoesNotExist:
            print('Order not found for session', session.id)

        for item in order.items.all():
            product = item.product
            product.num_available = product.num_available - item.quantity
            product.save()

        html = render_to_string('order_sent.html', {'order': order})
        send_mail('Order Confirmation', 'Your order is successful!', 'noreply@icadgadgets.com', ['muhammadirsyadibrahim21@gmail.com', order.email], fail_silently=False, html_message=html)

    return HttpResponse(status=200)
    
#    if event.type == 'checkout':
#      payment_intent = event.data.object
#
 #       print('Payment Intent : ', payment_intent.id)
  #      order = Order.objects.get(payment_intent=payment_intent.id)
#
#
#        order.payment_intent = payment_intent.id
#        order.paid = True
#        order.save()
#
#    return HttpResponse(status=200)

