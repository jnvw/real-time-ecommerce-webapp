from django.contrib import admin
from .models import Category, Product, ShoppingGroup, Cart, CartItem, Order, OrderItem, ChatMessage, OrderStatusHistory,Review,Coupon

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'created']
    list_filter = ['category', 'created']
    list_editable = ['price', 'stock']
    prepopulated_fields = {'slug': ('name',)}

class ShoppingGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'secret_code')
    filter_horizontal = ('members',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'user', 'status', 'paid', 'created_at')
    list_filter = ('status', 'paid', 'created_at')
    search_fields = ('group__name', 'user__username', 'id')
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        # Automatically log status changes
        if 'status' in form.changed_data:
            OrderStatusHistory.objects.create(order=obj, status=obj.status)
        super().save_model(request, obj, form, change)

admin.site.register(ShoppingGroup, ShoppingGroupAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(ChatMessage)
admin.site.register(OrderStatusHistory)
admin.site.site_header = "Collab Commerce Admin"
admin.site.site_title = "Collab Commerce Admin Portal"
admin.site.register(Review)
admin.site.register(Coupon)

