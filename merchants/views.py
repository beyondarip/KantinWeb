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

class MerchantDashboardView(LoginRequiredMixin, ListView):
    template_name = 'merchants/dashboard/dashboard.html'
    model = MenuItem
    context_object_name = 'menu_items'
    
    def get_queryset(self):
        return MenuItem.objects.filter(merchant__user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_items'] = self.get_queryset().count()
        context['categories'] = Category.objects.all()
        return context

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