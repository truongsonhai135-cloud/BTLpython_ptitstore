from django.contrib import admin
from .models import Product, Category, Order, OrderItem

# 1. Cấu hình hiển thị Danh mục sản phẩm
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# 2. Cấu hình hiển thị Sản phẩm
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock_quantity', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

# 3. Hiển thị danh sách sản phẩm con bên trong Đơn hàng
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')

# 4. Cấu hình quản lý Đơn hàng
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'total_price', 'status', 'created_at', 'user')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone', 'user__username')
    list_editable = ('status',)  # Cho phép đổi trạng thái trực tiếp ở bảng danh sách
    inlines = [OrderItemInline]