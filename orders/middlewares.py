from django.shortcuts import get_object_or_404
from merchants.models import MenuItem

class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, 'session'):
            request.session = {}
        
        if 'cart' not in request.session:
            request.session['cart'] = {}
        
        return self.get_response(request)