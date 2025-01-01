from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Merchant, Category, MenuItem

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
        queryset = Merchant.objects.filter(is_active=True)
        
        # Handle search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Handle category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
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