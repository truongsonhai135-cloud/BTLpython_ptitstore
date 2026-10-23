from django.urls import path
from django.contrib.auth import views as auth_views  # <-- Thêm dòng này lên đầu file
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    # 2 đường dẫn mới cho giỏ hàng
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:pk>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:pk>/', views.decrease_quantity, name='decrease_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register_view, name='register'),

    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'), 
    path('logout/', auth_views.LogoutView.as_view(next_page='product_list'), name='logout'),
]