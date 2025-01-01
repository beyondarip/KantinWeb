from django.urls import path
from . import views

app_name = 'merchants'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('merchants/', views.MerchantListView.as_view(), name='merchant_list'),
    path('merchants/<int:pk>/', views.MerchantDetailView.as_view(), name='merchant_detail'),

    path('dashboard/', views.MerchantDashboardView.as_view(), name='dashboard'),
    path('dashboard/menu/add/', views.MenuItemCreateView.as_view(), name='menu_create'),
      path('dashboard/menu/<int:pk>/edit/', views.MenuItemUpdateView.as_view(), name='menu_edit'),
    path('dashboard/menu/<int:pk>/delete/', views.MenuItemDeleteView.as_view(), name='menu_delete'),
]