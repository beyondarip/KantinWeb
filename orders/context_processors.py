# orders/context_processors.py
def cart_count(request):
    if request.user.is_authenticated:
        from .models import Cart
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            return {'cart_count': cart.items.count()}
    return {'cart_count': 0}