from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Product and Main pages
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('search/', views.search_results, name='search_results'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    

    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='shop/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Group Management
    path('groups/', views.group_dashboard, name='group_dashboard'),
    path('groups/<str:secret_code>/', views.group_detail, name='group_detail'),
    path('groups/set-active/<str:secret_code>/', views.set_active_group, name='set_active_group'),

    # Cart Management
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_cart_item, name='update_cart_item'),

    # Order & Payment Management
    path('order/create/', views.create_order_and_payment, name='create_order'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('orders/', views.order_history, name='order_history'),
    path('order/track/<int:order_id>/', views.order_tracking_view, name='order_tracking'),
    path('order/invoice/<int:order_id>/', views.view_invoice, name='view_invoice'),
    path('coupons/apply/', views.coupon_apply, name='coupon_apply'),
]
