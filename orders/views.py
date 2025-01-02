from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Order, OrderItem
from merchants.models import MenuItem
from .payment import MidtransPaymentGateway
import json
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponse
from django.views import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'orders/cart.html', {'cart': cart})

@login_required
@require_POST
def add_to_cart(request, item_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    menu_item = get_object_or_404(MenuItem, id=item_id)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        menu_item=menu_item,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'cart_count': cart.items.count()
    })

@login_required
@require_POST
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    data = json.loads(request.body)
    action = data.get('action')
    
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'removed': True,
                'cart_count': cart_item.cart.items.count(),
                'total': float(cart_item.cart.get_total_amount())
            })
            
    cart_item.save()
    
    return JsonResponse({
        'success': True,
        'quantity': cart_item.quantity,
        'subtotal': float(cart_item.get_subtotal()),
        'total': float(cart_item.cart.get_total_amount()),
        'cart_count': cart_item.cart.items.count()
    })

@login_required
@require_POST
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = cart_item.cart
    cart_item.delete()
    
    return JsonResponse({
        'success': True,
        'total': float(cart.get_total_amount()),
        'cart_count': cart.items.count()
    })
@login_required
def checkout(request):
    cart = request.user.cart
    if not cart.items.exists():
        return redirect('orders:cart')

    if request.method == 'POST':
        delivery_type = request.POST.get('delivery_type')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        notes = request.POST.get('delivery_notes') if delivery_type == 'delivery' else request.POST.get('pickup_notes', '')
        
        # Calculate total with fees
        total_amount = cart.get_total_amount() + 2000  # Service fee
        if delivery_type == 'delivery':
            total_amount += 10000  # Delivery fee

        # Create order
        order = Order.objects.create(
            user=request.user,
            merchant=cart.items.first().menu_item.merchant,
            total_amount=total_amount,
            status='pending',
            note=f"Nama: {name}\nTelepon: {phone}\nCatatan: {notes}"
        )

        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                price=cart_item.menu_item.price,
                subtotal=cart_item.get_subtotal()
            )

        # Generate Midtrans payment
        payment_gateway = MidtransPaymentGateway()
        payment = payment_gateway.generate_payment_token(order)

        if payment:
            order.midtrans_id = payment['token']
            order.payment_url = payment['redirect_url']
            order.save()

            # Clear cart
            cart.items.all().delete()

            return redirect('orders:payment', order_id=order.id)
        else:
            # Handle payment generation error
            order.delete()
            messages.error(request, 'Terjadi kesalahan saat memproses pembayaran. Silakan coba lagi.')
            return redirect('orders:checkout')

    return render(request, 'orders/checkout.html', {
        'cart': cart
    })

@login_required
def payment(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'orders/payment.html', {
        'order': order,
        'midtrans_client_key': settings.MIDTRANS_CLIENT_KEY
    })

@login_required
def payment_success(request):
    # Ambil order terakhir dari user untuk ditampilkan di success page
    try:
        latest_order = Order.objects.filter(user=request.user).latest('created_at')
        return render(request, 'orders/payment_success.html', {
            'order': latest_order
        })
    except Order.DoesNotExist:
        return render(request, 'orders/payment_success.html')