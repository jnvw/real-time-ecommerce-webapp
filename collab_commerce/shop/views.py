from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseBadRequest
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from decimal import Decimal



from django.utils import timezone
from django.views.decorators.http import require_POST
import requests
import uuid
import json

from .models import Product, ShoppingGroup, CartItem, Order, OrderItem, ChatMessage, Cart, Category,OrderStatusHistory,Review,Coupon
from .forms import GroupCreationForm, GroupJoinForm,ReviewForm,CouponApplyForm

def get_active_group(request):
    active_group_id = request.session.get('active_group_id')
    if active_group_id:
        try:
            return request.user.shopping_groups.get(id=active_group_id)
        except ShoppingGroup.DoesNotExist:
            del request.session['active_group_id']
            return None
    return None

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'shop/signup.html', {'form': form})

@login_required
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products_qs = Product.objects.filter(stock__gt=0)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products_qs = products_qs.filter(category=category)
        
    sort_option = request.GET.get('sort', 'name')
    if sort_option == 'price_asc':
        products_qs = products_qs.order_by('price')
    elif sort_option == 'price_desc':
        products_qs = products_qs.order_by('-price')
    else:
        products_qs = products_qs.order_by('name')

    paginator = Paginator(products_qs, 9)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'active_group': get_active_group(request),
        'sort_option': sort_option
    }
    return render(request, 'shop/product_list.html', context)





@login_required
def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    reviews = product.reviews.all()
    new_review = None

    # Check if the user has already reviewed this product
    user_review = reviews.filter(user=request.user).first()

    if request.method == 'POST' and not user_review:
        review_form = ReviewForm(data=request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            new_review.save()
            messages.success(request, 'Your review has been submitted successfully!')
            return redirect(product.get_absolute_url())
    else:
        review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'user_review': user_review,
        'active_group': get_active_group(request) # Keep context for base template
    }
    return render(request, 'shop/product_detail.html', context)

    
@login_required
def search_results(request):
    query = request.GET.get('q')
    if query:
        products_qs = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    else:
        products_qs = Product.objects.all()
    
    context = {
        'products': products_qs,
        'active_group': get_active_group(request),
        'query': query
    }
    return render(request, 'shop/product_list.html', context)


@login_required
def group_dashboard(request):
    user_groups = request.user.shopping_groups.all()
    active_group_id = request.session.get('active_group_id')
    
    if request.method == 'POST':
        if 'create_group' in request.POST:
            create_form = GroupCreationForm(request.POST)
            if create_form.is_valid():
                group = create_form.save()
                group.members.add(request.user)
                request.session['active_group_id'] = group.id
                messages.success(request, f"Group '{group.name}' created and set as active!")
                return redirect('group_detail', secret_code=group.secret_code)
        elif 'join_group' in request.POST:
            join_form = GroupJoinForm(request.POST)
            if join_form.is_valid():
                secret_code = join_form.cleaned_data['secret_code']
                try:
                    group_to_join = ShoppingGroup.objects.get(secret_code=secret_code)
                    if request.user not in group_to_join.members.all():
                        group_to_join.members.add(request.user)
                    request.session['active_group_id'] = group_to_join.id
                    messages.success(request, f"Successfully joined '{group_to_join.name}' and set as active!")
                    return redirect('group_detail', secret_code=group_to_join.secret_code)
                except ShoppingGroup.DoesNotExist:
                    messages.error(request, "Group with that secret code does not exist.")
                    return redirect('group_dashboard')
    else:
        create_form = GroupCreationForm()
        join_form = GroupJoinForm()

    return render(request, 'shop/group_dashboard.html', {
        'user_groups': user_groups,
        'create_form': create_form,
        'join_form': join_form,
        'active_group_id': active_group_id
    })

@login_required
def set_active_group(request, secret_code):
    try:
        group = request.user.shopping_groups.get(secret_code=secret_code)
        request.session['active_group_id'] = group.id
        messages.success(request, f"'{group.name}' is now your active shopping group.")
    except ShoppingGroup.DoesNotExist:
        messages.error(request, "You are not a member of that group.")
    
    return redirect(request.META.get('HTTP_REFERER', 'group_dashboard'))

@login_required
def group_detail(request, secret_code):
    group = get_object_or_404(ShoppingGroup, secret_code=secret_code)
    if request.user not in group.members.all():
        messages.error(request, "You are not a member of this group.")
        return redirect('group_dashboard')

    chat_messages = ChatMessage.objects.filter(group=group).order_by('timestamp')[:50]
    
    return render(request, 'shop/group_detail.html', {
        'group': group,
        'chat_messages': chat_messages,
        'current_user_username': request.user.username 
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    group = get_active_group(request)

    if not group:
        messages.error(request, "You must have an active group to add items to a cart.")
        return redirect('product_list')

    cart = group.shared_cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1, 'added_by': request.user}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    channel_layer = get_channel_layer()
    notification_message = f"{request.user.username} added '{product.name}' to the cart."
    async_to_sync(channel_layer.group_send)(
        f'group_{group.secret_code}',
        {
            'type': 'cart_update',
            'notification_message': notification_message
        }
    )
    
    messages.success(request, f"Added '{product.name}' to the '{group.name}' cart.")
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    group = ShoppingGroup.objects.get(shared_cart=cart_item.cart)

    if request.user not in group.members.all():
        messages.error(request, "You do not have permission to modify this cart.")
        return redirect('group_dashboard')
    
    notification_message = f"{request.user.username} removed an item from the cart."
    cart_item.delete()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'group_{group.secret_code}',
        {
            'type': 'cart_update',
            'notification_message': notification_message
        }
    )
    return redirect('group_detail', secret_code=group.secret_code)

@login_required
def update_cart_item(request, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id)
    group = ShoppingGroup.objects.get(shared_cart=cart_item.cart)
    notification_message = f"{request.user.username} updated an item in the cart."

    if request.user not in group.members.all():
        messages.error(request, "You do not have permission to modify this cart.")
        return redirect('group_dashboard')

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'group_{group.secret_code}',
        {
            'type': 'cart_update',
            'notification_message': notification_message
        }
    )
    return redirect('group_detail', secret_code=group.secret_code)


@login_required
def create_order_and_payment(request):
    group = get_active_group(request)
    if not group or not group.shared_cart.items.exists():
        messages.error(request, "Your active cart is empty.")
        return redirect('group_dashboard')

    cart = group.shared_cart
    cart_total_price = sum(item.get_total() for item in cart.items.all())
    
    # Check for an active coupon
    coupon_id = request.session.get('coupon_id')
    coupon = None
    discount_percentage = 0
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
            discount_percentage = coupon.discount
        except Coupon.DoesNotExist:
            pass # Invalid coupon, proceed without discount

    # Calculate final price
    discount_amount = (cart_total_price * Decimal(discount_percentage)) / 100
    final_price = cart_total_price - discount_amount
    
    # Create the order with all details
    order = Order.objects.create(
        group=group, user=request.user, total_price=cart_total_price,
        coupon=coupon, discount=discount_percentage
    )
    for item in cart.items.all():
        OrderItem.objects.create(order=order, product=item.product, price=item.product.price, quantity=item.quantity)
    
    # Prepare payment session with the FINAL price
    url = f"{settings.CASHFREE_API_BASE}/orders"
    cashfree_order_id = f"order_{order.id}_{uuid.uuid4().hex[:6]}"
    payload = {
        "customer_details": {"customer_id": str(request.user.id), "customer_email": request.user.email or "default@email.com", "customer_phone": "9999999999"},
        "order_meta": {"return_url": request.build_absolute_uri(reverse('payment_success')) + f"?order_id={cashfree_order_id}"},
        "order_id": cashfree_order_id,
        "order_amount": float(final_price),
        "order_currency": "INR"
    }
    headers = {"accept": "application/json", "x-api-version": "2022-09-01", "x-client-id": settings.CASHFREE_APP_ID, "x-client-secret": settings.CASHFREE_SECRET_KEY, "content-type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        payment_data = response.json()
        if response.status_code == 200 and payment_data.get('payment_session_id'):
            order.cashfree_order_id = payment_data.get('cf_order_id')
            order.save()
            return render(request, 'shop/checkout.html', {'payment_session_id': payment_data['payment_session_id']})
        
        error_message = payment_data.get('message', 'An unknown error occurred.')
        messages.error(request, f"Could not initialize payment: {error_message}")
        order.delete()
        return redirect('group_detail', secret_code=group.secret_code)
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Could not connect to payment gateway: {e}")
        order.delete()
        return redirect('group_detail', secret_code=group.secret_code)

@require_POST
def coupon_apply(request):
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True)
            request.session['coupon_id'] = coupon.id
            messages.success(request, f'Coupon "{coupon.code}" applied successfully!')
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
            messages.error(request, 'This coupon does not exist or is not active.')
    return redirect('group_detail', secret_code=request.POST.get('secret_code'))

@login_required
def payment_success(request):
    cashfree_order_id = request.GET.get('order_id')
    if not cashfree_order_id:
        messages.error(request, "Payment details not found.")
        return redirect('order_history')

    url = f"{settings.CASHFREE_API_BASE}/orders/{cashfree_order_id}"
    headers = {"accept": "application/json", "x-api-version": "2022-09-01", "x-client-id": settings.CASHFREE_APP_ID, "x-client-secret": settings.CASHFREE_SECRET_KEY}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        payment_data = response.json()
        
        internal_order_id = cashfree_order_id.split('_')[1]
        order = Order.objects.get(id=internal_order_id)

        if payment_data.get('order_status') == 'PAID':
            order.paid = True
            order.status = 'Processing'
            order.save()
            
            # Clear coupon from session after successful use
            if 'coupon_id' in request.session:
                del request.session['coupon_id']
            
            messages.success(request, f"Payment for Order #{order.id} was successful!")
            
            group = get_active_group(request)
            if group and group.shared_cart:
                group.shared_cart.items.all().delete()
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'group_{group.secret_code}',
                    {'type': 'cart_update', 'notification_message': f'Order #{order.id} was placed and the cart cleared.'}
                )
        else:
            order.status = 'Failed'
            order.save()
            messages.error(request, f"Payment for Order #{order.id} failed. Status: {payment_data.get('order_status')}")
    except (requests.exceptions.RequestException, Order.DoesNotExist, IndexError) as e:
        messages.error(request, f"Could not verify payment status: {e}")

    return redirect('order_history')



@login_required
def order_history(request):
    user_groups = request.user.shopping_groups.all()
    orders = Order.objects.filter(group__in=user_groups).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})
@login_required
def order_tracking_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Security check: ensure the user is part of the group that made the order
    if request.user not in order.group.members.all():
        messages.error(request, "You do not have permission to view this order.")
        return redirect('order_history')
        
    return render(request, 'shop/order_tracking.html', {'order': order})

@login_required
def view_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user not in order.group.members.all():
        messages.error(request, "You do not have permission to view this invoice.")
        return redirect('order_history')
        
    return render(request, 'shop/invoice.html', {'order': order})
