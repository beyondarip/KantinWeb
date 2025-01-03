from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Merchant, Category, MenuItem
from .forms import MenuItemForm


class HomeView(ListView):
    template_name = 'home.html'
    model = Merchant
    context_object_name = 'featured_merchants'

    def get_queryset(self):
        return Merchant.objects.filter(is_active=True)[:6]  # Ambil 6 merchant untuk featured
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
# merchants/views.py

from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Merchant
from .forms import MerchantRegistrationForm

# class MerchantRegistrationView(LoginRequiredMixin, CreateView):
#     model = Merchant
#     template_name = 'merchants/dashboard/merchant_registration.html'
#     form_class = MerchantRegistrationForm
#     success_url = reverse_lazy('merchants:dashboard')
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['categories'] = Category.objects.all()
#         return context
    
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         messages.success(self.request, 'Toko berhasil dibuat!')
#         return super().form_valid(form)
    
#     def dispatch(self, request, *args, **kwargs):
#         # Redirect if user already has a merchant
#         if hasattr(request.user, 'merchant'):
#             messages.info(request, 'Anda sudah memiliki toko.')
#             return redirect('merchants:dashboard')
#         return super().dispatch(request, *args, **kwargs)

# merchants/views.py
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .models import Merchant
from .forms import MerchantForm

class MerchantCreateView(LoginRequiredMixin, CreateView):
    model = Merchant
    form_class = MerchantForm
    template_name = 'merchants/dashboard/merchant_form.html'
    success_url = reverse_lazy('merchants:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Store'
        context['submit_text'] = 'Create Store'
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Store created successfully!')
        return response

class MerchantUpdateView(LoginRequiredMixin, UpdateView):
    model = Merchant
    form_class = MerchantForm
    template_name = 'merchants/dashboard/merchant_form.html'
    success_url = reverse_lazy('merchants:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Store'
        context['submit_text'] = 'Save Changes'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Store updated successfully!')
        return response

    def get_object(self, queryset=None):
        return self.request.user.merchant

class MerchantDeleteView(LoginRequiredMixin, DeleteView):
    model = Merchant
    template_name = 'merchants/dashboard/merchant_confirm_delete.html'
    success_url = reverse_lazy('merchants:dashboard')

    def get_object(self, queryset=None):
        return self.request.user.merchant

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Store deleted successfully!')
        return super().delete(request, *args, **kwargs)

class MerchantDashboardView(LoginRequiredMixin, ListView):
    template_name = 'merchants/dashboard/dashboard.html'
    model = MenuItem
    context_object_name = 'menu_items'
    
    def get_queryset(self):
        # Gunakan try-except untuk lebih robust
        try:
            merchant = self.request.user.merchant
            return MenuItem.objects.filter(merchant=merchant)
        except Merchant.DoesNotExist:
            return MenuItem.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(f"User: {self.request.user}")
        print(f"Is merchant: {self.request.user.is_merchant}")
        print(f"Has merchant attr: {hasattr(self.request.user, 'merchant')}")
        # Cek apakah user adalah merchant
        if not self.request.user.is_merchant:
            context['has_merchant'] = False
            return context
            
        # Jika user adalah merchant, cek merchant object
        try:
            merchant = Merchant.objects.get(user=self.request.user)
            context['has_merchant'] = True
            context['merchant'] = merchant
            context['total_items'] = self.get_queryset().count()
            context['categories'] = Category.objects.all()
        except Merchant.DoesNotExist:
            context['has_merchant'] = False
            
        return context

#     def get_queryset(self):
#         return MenuItem.objects.filter(merchant__user=self.request.user)
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['total_items'] = self.get_queryset().count()
#         context['categories'] = Category.objects.all()
#         return context

class MerchantListView(ListView):
    template_name = 'merchants/merchant_list.html'
    model = Merchant
    context_object_name = 'merchants'
    paginate_by = 9

    def get_queryset(self):
        queryset = Merchant.objects.filter(is_active=True).distinct()
        
        # Handle search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Handle category filter
        category = self.request.GET.get('category')
        if category and category.isdigit():
            queryset = queryset.filter(categories__id=category)
        
        # Handle sorting
        sort = self.request.GET.get('sort')
        if sort == 'rating':
            queryset = queryset.order_by('-rating')
        elif sort == 'popular':
            queryset = queryset.order_by('-total_orders')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-created_at')  # Default sorting
                
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        # Add active filters to context
        context['active_category'] = self.request.GET.get('category', '')
        context['active_sort'] = self.request.GET.get('sort', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        return context

class MerchantDetailView(DetailView):
    template_name = 'merchants/merchant_detail.html'
    model = Merchant
    context_object_name = 'merchant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group menu items by category
        menu_items = MenuItem.objects.filter(merchant=self.object, is_available=True)
        menu_by_category = {}
        for item in menu_items:
            if item.category not in menu_by_category:
                menu_by_category[item.category] = []
            menu_by_category[item.category].append(item)
        context['menu_by_category'] = menu_by_category
        return context
    
# merchants/views.py

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import MenuItem, Category

# class MerchantDashboardView(LoginRequiredMixin, ListView):
#     template_name = 'merchants/dashboard/dashboard.html'
#     model = MenuItem
#     context_object_name = 'menu_items'
    
#     def get_queryset(self):
#         return MenuItem.objects.filter(merchant__user=self.request.user)
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['total_items'] = self.get_queryset().count()
#         context['categories'] = Category.objects.all()
#         return context

class MenuItemCreateView(LoginRequiredMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'merchants/dashboard/menu_form.html'
    success_url = reverse_lazy('merchants:dashboard')

    def form_valid(self, form):
        # Tambahkan merchant sebelum menyimpan
        try:
            form.instance.merchant = self.request.user.merchant
            messages.success(self.request, 'Menu berhasil ditambahkan!')
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Gagal menambahkan menu: {str(e)}')
            return super().form_invalid(form)
    
# merchants/views.py

from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView


class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'merchants/dashboard/menu_confirm_delete.html'
    success_url = reverse_lazy('merchants:dashboard')

    def get_queryset(self):
        return MenuItem.objects.filter(merchant__user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Menu item deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
# merchants/views.py



class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'merchants/dashboard/menu_form.html'
    success_url = reverse_lazy('merchants:dashboard')


# merchants/views.py
# merchants/views.py
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from orders.models import Order
from datetime import datetime, timedelta
import calendar

class MerchantOrderListView(LoginRequiredMixin, ListView):
    template_name = 'merchants/dashboard/orders_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        merchant = self.request.user.merchant
        return Order.objects.filter(merchant=merchant).order_by('-created_at')

    def get_monthly_revenue(self, year, month):
        """Helper method to get revenue for specific month"""
        return Order.objects.filter(
            merchant=self.request.user.merchant,
            payment_status='paid',
            created_at__year=year,
            created_at__month=month
        ).aggregate(total=Sum('total_amount'))['total'] or 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        merchant = self.request.user.merchant
        
        # Get requested month/year or default to current
        current_date = datetime.now()
        requested_year = int(self.request.GET.get('year', current_date.year))
        requested_month = int(self.request.GET.get('month', current_date.month))
        requested_date = datetime(requested_year, requested_month, 1)

        # Get previous and next month/year
        prev_month = (requested_date - timedelta(days=1)).replace(day=1)
        next_month = (requested_date + timedelta(days=32)).replace(day=1)
        
        # Get revenue and order data for current month
        current_month_orders = Order.objects.filter(
            merchant=merchant,
            created_at__year=requested_year,
            created_at__month=requested_month
        )
        
        current_month_revenue = self.get_monthly_revenue(requested_year, requested_month)
        prev_month_revenue = self.get_monthly_revenue(prev_month.year, prev_month.month)
        
        # Get order statistics
        paid_orders = current_month_orders.filter(payment_status='paid').count()
        pending_orders = current_month_orders.filter(payment_status='pending').count()
        total_orders = current_month_orders.count()
        
        # Calculate daily average for current month
        days_in_month = calendar.monthrange(requested_year, requested_month)[1]
        if current_date.year == requested_year and current_date.month == requested_month:
            days_passed = current_date.day
        else:
            days_passed = days_in_month
        daily_average = current_month_revenue / days_passed if days_passed > 0 else 0

        # Calculate month-over-month growth
        revenue_growth = ((current_month_revenue - prev_month_revenue) / prev_month_revenue * 100) if prev_month_revenue > 0 else 0
        
        context.update({
            'current_month': requested_date,
            'prev_month': prev_month,
            'next_month': next_month if next_month <= current_date else None,
            'current_month_revenue': current_month_revenue,
            'prev_month_revenue': prev_month_revenue,
            'daily_average': daily_average,
            'revenue_growth': revenue_growth,
            'days_passed': days_passed,
            'days_in_month': days_in_month,
            'paid_orders': paid_orders,
            'pending_orders': pending_orders,
            'total_orders': total_orders
        })
        
        return context

class MerchantOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'merchants/dashboard/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(merchant=self.request.user.merchant)