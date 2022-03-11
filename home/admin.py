from django.contrib import admin
from home.models import Services,Cred, Order, deleted_orders, dry_clean_services

# Register your models here.
admin.site.register(Services)
admin.site.register(Order)
admin.site.register(dry_clean_services)
admin.site.register(deleted_orders)
admin.site.register(Cred)