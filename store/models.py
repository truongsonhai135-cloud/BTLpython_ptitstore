from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Danh mục")
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá tiền (VNĐ)")
    description = models.TextField(blank=True, verbose_name="Mô tả sản phẩm")
    image_url = models.CharField(max_length=500, blank=True, verbose_name="Đường dẫn ảnh")
    stock_quantity = models.PositiveIntegerField(default=100, verbose_name="Số lượng tồn kho")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Quản lý Sản phẩm"

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Chờ xử lý'),
        ('Confirmed', 'Đã xác nhận'),
        ('Shipping', 'Đang giao hàng'),
        ('Completed', 'Đã hoàn thành'),
        ('Cancelled', 'Đã hủy'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='orders', verbose_name="Tài khoản đặt hàng")
    full_name = models.CharField(max_length=100, verbose_name="Họ tên người nhận")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ giao hàng")
    total_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Tổng tiền")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Trạng thái đơn hàng")

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Đơn hàng")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Sản phẩm")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá tại thời điểm mua")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class UserProfile(models.Model):
    ROLE_CHOICES = (('customer', 'Khách hàng'),)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Tài khoản")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer', verbose_name="Vai trò")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
