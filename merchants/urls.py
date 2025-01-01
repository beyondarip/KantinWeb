from django.urls import path
from . import views

app_name = 'merchants'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('merchants/', views.MerchantListView.as_view(), name='merchant_list'),
    path('merchants/<int:pk>/', views.MerchantDetailView.as_view(), name='merchant_detail'),
]