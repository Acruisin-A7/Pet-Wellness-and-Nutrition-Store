from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Product, Category, Order, OrderItem, Veterinarian, VetAvailability, Appointment, ResourceCategory, Resource

User = get_user_model()  # Get Django's default User model

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock']
    search_fields = ['name']
    list_filter = ['category']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'total_amount', 'status', 'payment_status')
    list_filter = ('status', 'payment_status')
    search_fields = ('user__id', 'id')  # Updated to avoid direct username reference

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')

admin.site.register(Veterinarian)
admin.site.register(VetAvailability)
admin.site.register(Appointment)
admin.site.register(ResourceCategory)
admin.site.register(Resource)