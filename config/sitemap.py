from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from merchants.models import Merchant

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['merchants:home', 'merchants:merchant_list', 'accounts:login', 
                'accounts:register']

    def location(self, item):
        return reverse(item)

class MerchantSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Merchant.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('merchants:merchant_detail', args=[obj.pk])
