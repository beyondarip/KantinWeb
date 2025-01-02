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
    try:
        cart = request.user.cart
        if not cart.items.exists():
            messages.error(request, 'Keranjang Anda kosong')
            return redirect('orders:cart')

        if request.method == 'POST':
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            notes = request.POST.get('notes', '')
            
            if not name or not phone:
                messages.error(request, 'Mohon lengkapi semua data')
                return redirect('orders:checkout')
            
            # Calculate total with service fee
            total_amount = cart.get_total_amount() + 2000  # Service fee only

            try:
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
                    raise Exception('Gagal membuat payment token')

            except Exception as e:
                # Jika ada error, hapus order jika sudah dibuat
                if 'order' in locals():
                    order.delete()
                messages.error(request, 'Terjadi kesalahan saat memproses pesanan. Silakan coba lagi.')
                return redirect('orders:checkout')

        return render(request, 'orders/checkout.html', {'cart': cart})
        
    except Exception as e:
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi nanti.')
        return redirect('orders:cart')

@login_required
def payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        return render(request, 'orders/payment.html', {
            'order': order,
            'midtrans_client_key': settings.MIDTRANS_CLIENT_KEY
        })
    except Order.DoesNotExist:
        messages.error(request, 'Order tidak ditemukan')
        return redirect('orders:cart')
    except Exception as e:
        messages.error(request, 'Terjadi kesalahan sistem')
        return redirect('orders:cart')

@login_required
def payment_success(request):
    try:
        latest_order = Order.objects.filter(
            user=request.user,
            status='pending'
        ).latest('created_at')
        
        # Update order status
        latest_order.status = 'paid'
        latest_order.payment_status = 'paid'


        # Update merchant total_orders
        merchant = latest_order.merchant
        merchant.total_orders += 1
        latest_order.save()
        
        return render(request, 'orders/payment_success.html', {
            'order': latest_order
        })
    except Order.DoesNotExist:
        messages.warning(request, 'Tidak ada order yang ditemukan')
        return redirect('merchants:home')
    except Exception as e:
        messages.error(request, 'Terjadi kesalahan sistem')
        return redirect('merchants:home')


@login_required
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        return render(request, 'orders/order_detail.html', {'order': order})
    except Order.DoesNotExist:
        messages.error(request, 'Pesanan tidak ditemukan')
        return redirect('merchants:home')

from django.core.paginator import Paginator


@login_required
def order_history(request):
    # Get all orders for the user, newest first
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)  # 10 orders per page
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    return render(request, 'orders/order_history.html', {'orders': orders})
