import json
from decimal import Decimal
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from shop.models import Order, User, Product, Category, OrderItem
from django.http import JsonResponse

@staff_member_required
def admin_dashboard(request):
    # --- Dynamic Date Range Calculations ---
    range_param = request.GET.get('range', '30') # Default to last 30 days
    today = timezone.now()
    
    if range_param == '7':
        start_date = today - timedelta(days=7)
    elif range_param == '90':
        start_date = today - timedelta(days=90)
    else: # Default to 30
        start_date = today - timedelta(days=30)

    # --- KPI Card & Chart Data Calculations ---
    
    orders_in_range = Order.objects.filter(created_at__gte=start_date, paid=True)
    
    total_sales = orders_in_range.aggregate(total=Sum('total_price'))['total'] or 0
    net_sales = total_sales * Decimal('0.90')
    new_customers = User.objects.filter(date_joined__gte=start_date).count()
    total_orders = orders_in_range.count()

    # Sales Bar Chart (Daily sales over the selected period)
    sales_by_day = (
        orders_in_range
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(daily_total=Sum('total_price'))
        .order_by('day')
    )
    labels_by_day = [item['day'].strftime('%b %d') for item in sales_by_day]
    data_by_day = [float(item['daily_total']) for item in sales_by_day]

    # Donut Chart (Sales by Category for the selected period)
    category_sales = Product.objects.filter(
        orderitem__order__in=orders_in_range
    ).values('category__name').annotate(total=Sum('orderitem__price')).order_by('-total')
    
    category_labels = [item['category__name'] for item in category_sales if item['category__name']]
    category_data = [float(item['total'] or 0) for item in category_sales if item['category__name']]
    
    # Top 5 Selling Products Chart
    top_products = Product.objects.filter(
        orderitem__order__in=orders_in_range
    ).values('name').annotate(quantity_sold=Sum('orderitem__quantity')).order_by('-quantity_sold')[:5]

    top_products_labels = [item['name'] for item in top_products]
    top_products_data = [item['quantity_sold'] for item in top_products]

    # Radial Chart Data: Inventory vs. Sales
    all_categories = Category.objects.annotate(total_products=Count('products')).order_by('name')

    purchased_products_by_cat = OrderItem.objects.filter(
        order__in=orders_in_range
    ).values('product__category__name').annotate(
        purchased_count=Count('product_id', distinct=True)
    )
    
    purchased_lookup = {item['product__category__name']: item['purchased_count'] for item in purchased_products_by_cat}

    radial_labels = [cat.name for cat in all_categories]
    radial_total_data = [cat.total_products for cat in all_categories]
    radial_purchased_data = [purchased_lookup.get(cat.name, 0) for cat in all_categories]


    context = {
        'total_sales': f"{total_sales:,.2f}",
        'net_sales': f"{net_sales:,.2f}",
        'new_customers': new_customers,
        'total_orders': total_orders,
        'sales_by_day_labels': labels_by_day,
        'sales_by_day_data': data_by_day,
        'category_labels': category_labels,
        'category_data': category_data,
        'top_products_labels': top_products_labels,
        'top_products_data': top_products_data,
        'radial_labels': radial_labels,
        'radial_total_data': radial_total_data,
        'radial_purchased_data': radial_purchased_data,
        'active_range': range_param
    }

    # If this is an AJAX request from our filter buttons, return only the data
    if "XMLHttpRequest" == request.headers.get("x-requested-with"):
        return JsonResponse(context)
        
    # For a normal page load, render the full HTML template with the context
    return render(request, 'dashboard/dashboard.html', context)
