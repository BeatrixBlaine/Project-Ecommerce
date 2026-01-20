from django.conf import settings
from apps.store.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def __iter__(self):
        product_ids = list(self.cart.keys())
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(p.id): p for p in products}

        for item in self.cart.values():
            # attach product safely
            item['product'] = product_map.get(item.get('id'))

            # sanitize quantity
            try:
                quantity = int(item.get('quantity') or 0)
            except (TypeError, ValueError):
                quantity = 0

            item['quantity'] = quantity
            item['price'] = float(item.get('price') or 0)
            item['total_price'] = item['price'] * quantity

            yield item

    def __len__(self):
        return sum(
            int(item.get('quantity') or 0)
            for item in self.cart.values()
        )

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': float(product.price),
                'id': product_id
            }

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def get_total_length(self):
        return sum(int(item['quantity']) for item in self.cart.values())
    
    def get_total_cost(self):
        return sum(float(item['total_price']) for item in self.cart.values())
