from online_shop.views import get_cart
from decimal import Decimal

def cart(request):
    cart = get_cart(request)
    y = sum([x['weight'] * x['quantity'] for x in cart.values()])
    cart_total_price = sum(Decimal(item['price'])*item['quantity'] for item in cart.values())
    return {'cart_total_price': cart_total_price}