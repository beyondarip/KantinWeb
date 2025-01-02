from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Order, OrderItem
import json

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
    cart = get_object_or_404(Cart, user=request.user)
    
    if request.method == 'POST':
        # Handle form submission
        delivery_type = request.POST.get('delivery_type')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        
        if delivery_type == 'delivery':
            address = request.POST.get('address')
            delivery_notes = request.POST.get('delivery_notes')
        else:
            pickup_notes = request.POST.get('pickup_notes')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            delivery_type=delivery_type,
            name=name,
            phone=phone,
            address=address if delivery_type == 'delivery' else '',
            notes=delivery_notes if delivery_type == 'delivery' else pickup_notes,
            total_amount=cart.get_total_amount()
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
        
        # Clear cart
        cart.items.all().delete()
        
        # Redirect to payment
        return redirect('orders:payment', order_id=order.id)
    
    return render(request, 'orders/checkout.html', {
        'cart': cart
    })