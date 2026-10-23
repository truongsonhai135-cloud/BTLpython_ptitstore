from decimal import Decimal, InvalidOperation
import re

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Category, Order, OrderItem, Product, UserProfile


def product_list(request):
    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(name__icontains=query)
    category_id = request.GET.get('category', '')
    if category_id.isdigit():
        products = products.filter(category_id=int(category_id))
    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-id')
    return render(request, 'store/product_list.html', {
        'products': products, 'categories': categories, 'query': query,
        'selected_category': category_id, 'sort': sort,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, min(quantity, 99))
    cart = request.session.get('cart', {})
    key = str(product.pk)
    existing = cart.get(key, {})
    try:
        existing_quantity = int(existing.get('quantity', 0))
    except (TypeError, ValueError):
        existing_quantity = 0
    requested_total = existing_quantity + quantity
    if requested_total > product.stock_quantity:
        messages.error(request, f"Vượt quá số lượng hàng tồn kho. Sản phẩm '{product.name}' chỉ còn {product.stock_quantity}.")
        return redirect('cart_detail')
    cart[key] = {
        'name': product.name,
        'quantity': min(requested_total, 99),
        'image_url': product.image_url or '',
    }
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, 'Đã thêm sản phẩm vào giỏ hàng.')
    return redirect('cart_detail')


def _build_cart(request):
    """Luôn lấy giá hiện tại từ database, không tin giá lưu trong session."""
    session_cart = request.session.get('cart', {})
    cart = {}
    total = Decimal('0')
    valid_ids = []
    for product_id, data in session_cart.items():
        if not str(product_id).isdigit():
            continue
        try:
            quantity = int(data.get('quantity', 1))
        except (TypeError, ValueError):
            continue
        if quantity < 1 or quantity > 99:
            continue
        valid_ids.append(int(product_id))
    products = {str(p.pk): p for p in Product.objects.filter(pk__in=valid_ids)}
    for product_id, data in session_cart.items():
        product = products.get(str(product_id))
        if not product:
            continue
        try:
            quantity = int(data.get('quantity', 1))
        except (TypeError, ValueError):
            continue
        if not 1 <= quantity <= 99:
            continue
        subtotal = product.price * quantity
        cart[str(product.pk)] = {
            'name': product.name, 'price': product.price,
            'quantity': quantity, 'image_url': product.image_url or '',
            'subtotal': subtotal,
        }
        total += subtotal
    request.session['cart'] = {k: {'quantity': v['quantity']} for k, v in cart.items()}
    return cart, total


def cart_detail(request):
    cart, total_price = _build_cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart, 'total_price': total_price})


@require_POST
def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    cart.pop(str(pk), None)
    request.session['cart'] = cart
    return redirect('cart_detail')


@require_POST
def increase_quantity(request, pk):
    cart = request.session.get('cart', {})
    key = str(pk)
    if key in cart:
        product = Product.objects.filter(pk=pk).first()
        current_quantity = int(cart[key].get('quantity', 1))
        if product is None:
            cart.pop(key, None)
            messages.error(request, 'Sản phẩm không còn tồn tại.')
        elif current_quantity + 1 > product.stock_quantity:
            messages.error(request, f"Vượt quá số lượng hàng tồn kho. Sản phẩm '{product.name}' chỉ còn {product.stock_quantity}.")
        elif current_quantity < 99:
            cart[key]['quantity'] = current_quantity + 1
        request.session['cart'] = cart
    return redirect('cart_detail')


@require_POST
def decrease_quantity(request, pk):
    cart = request.session.get('cart', {})
    key = str(pk)
    if key in cart:
        quantity = int(cart[key].get('quantity', 1))
        if quantity > 1:
            cart[key]['quantity'] = quantity - 1
        else:
            cart.pop(key, None)
        request.session['cart'] = cart
    return redirect('cart_detail')


def checkout(request):
    cart, total_price = _build_cart(request)
    if not cart:
        messages.info(request, 'Giỏ hàng đang trống hoặc sản phẩm không còn tồn tại.')
        return redirect('product_list')
    if request.method == 'POST':
        customer_name = request.POST.get('name', '').strip()
        customer_phone = request.POST.get('phone', '').strip()
        customer_address = request.POST.get('address', '').strip()
        if not customer_name or not customer_phone or not customer_address:
            messages.error(request, 'Vui lòng nhập đầy đủ họ tên, số điện thoại và địa chỉ.')
            return render(request, 'store/checkout.html', {'cart': cart, 'total_price': total_price})
        if not re.fullmatch(r'0[0-9]{9}', customer_phone):
            messages.error(request, 'Số điện thoại phải bắt đầu bằng số 0 và gồm đúng 10 chữ số.')
            return render(request, 'store/checkout.html', {'cart': cart, 'total_price': total_price})
        with transaction.atomic():
            # Tính lại giá ngay lúc tạo đơn, tránh dùng giá do trình duyệt/session gửi lên.
            product_ids = [int(pid) for pid in cart]
            products = {str(p.pk): p for p in Product.objects.select_for_update().filter(pk__in=product_ids)}
            if len(products) != len(cart):
                messages.error(request, 'Một số sản phẩm không còn khả dụng. Vui lòng kiểm tra giỏ hàng.')
                return redirect('cart_detail')
            # Kiểm tra tồn kho trong transaction trước khi tạo đơn hàng.
            for pid, data in cart.items():
                product = products[pid]
                if data['quantity'] > product.stock_quantity:
                    messages.error(request, f"Vượt quá số lượng hàng tồn kho. Sản phẩm '{product.name}' chỉ còn {product.stock_quantity}.")
                    return redirect('cart_detail')
            total_price = sum((products[pid].price * data['quantity'] for pid, data in cart.items()), Decimal('0'))
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=customer_name, phone=customer_phone,
                address=customer_address, total_price=total_price,
            )
            for product_id, data in cart.items():
                product = products[product_id]
                OrderItem.objects.create(order=order, product=product,
                                         price=product.price, quantity=data['quantity'])
                product.stock_quantity -= data['quantity']
                product.save(update_fields=['stock_quantity'])
        request.session['cart'] = {}
        return render(request, 'store/order_success.html', {'order': order})
    return render(request, 'store/checkout.html', {'cart': cart, 'total_price': total_price})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('product_list')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        if not username or not password:
            messages.error(request, 'Vui lòng nhập tên đăng nhập và mật khẩu.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập này đã có người sử dụng!')
        else:
            user = User.objects.create_user(username=username, password=password)
            UserProfile.objects.create(user=user, role='customer', phone=phone, address=address)
            messages.success(request, 'Đăng ký thành công! Hãy đăng nhập để tiếp tục.')
            return redirect('login')
    return render(request, 'store/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('product_list')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, 'Đăng nhập thành công!')
            next_url = request.GET.get('next')
            return redirect(next_url if next_url and next_url.startswith('/') and not next_url.startswith('//') else 'product_list')
        messages.error(request, 'Tên đăng nhập hoặc mật khẩu không chính xác!')
    return render(request, 'store/login.html')


@login_required(login_url='login')
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
        profile.phone = request.POST.get('phone', '').strip()
        profile.address = request.POST.get('address', '').strip()
        profile.save(update_fields=['phone', 'address'])
        messages.success(request, 'Cập nhật thông tin cá nhân thành công!')
        return redirect('profile')
    return render(request, 'store/profile.html', {'profile': profile, 'orders': orders})


@login_required(login_url='login')
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not (request.user.is_staff or order.user_id == request.user.id):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    return render(request, 'store/order_detail.html', {'order': order})
