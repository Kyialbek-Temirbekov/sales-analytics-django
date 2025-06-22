from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.db.models import Sum
from django.conf import settings
from django.utils.dateparse import parse_date

from .models import Order, Client, OrderItem
from .serializers import OrderSerializer, OrderStatusSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from io import BytesIO
import logging
import os

log = logging.getLogger(__name__)

class OrderStatusUpdateApiView(APIView):
    @swagger_auto_schema(request_body=OrderStatusSerializer, operation_description="Update order status")
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderStatusSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            
            new_status = serializer.validated_data.get('status')
            if new_status == Order.Status.CONFIRMED:
                for order_item in order.items.all():
                    product = order_item.product
                    quantity = order_item.quantity
                    product.stock_quantity -= quantity
                    product.save()
            
            serializer.save()
            log.info('Order status updated')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderListCreateView(APIView):
    @swagger_auto_schema(request_body=OrderSerializer, operation_description="Make order")
    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            log.info('Order created')
            return Response({"message": "Order created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Get orders of user",
    )
    def get(self, request):
        user = request.user
        orders = Order.objects.filter(client=user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class ReportApiView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'start',
                openapi.IN_QUERY,
                description="Start date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format='date'
            ),
            openapi.Parameter(
                'end',
                openapi.IN_QUERY,
                description="End date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format='date'
            )
        ],
        operation_description="Get sales analytics report"
    )
    def get(self, request):
        start_str = request.GET.get('start')
        end_str = request.GET.get('end')

        start_date = parse_date(start_str) if start_str else None
        end_date = parse_date(end_str) if end_str else None

        orders_qs = Order.objects.all()
        if start_date:
            orders_qs = orders_qs.filter(created_at__date__gte=start_date)
        if end_date:
            orders_qs = orders_qs.filter(created_at__date__lte=end_date)

        total_revenue = orders_qs.aggregate(total=Sum('total_sum'))['total'] or 0
        order_count = orders_qs.count()

        top_clients = (
            orders_qs
            .values('client__id', 'client__full_name')
            .annotate(revenue=Sum('total_sum'))
            .order_by('-revenue')[:5]
        )

        most_popular_product = (
            OrderItem.objects
            .filter(order__in=orders_qs)
            .values('product__id', 'product__name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')
            .first()
        )

        filtered_orders = orders_qs.select_related('client').values(
            'created_at',
            'client__full_name',
            'total_sum',
            'status'
        )

        context = {
            'title': 'Sales Report',
            'total_revenue': total_revenue,
            'order_count': order_count,
            'top_clients': top_clients,
            'most_popular_product': most_popular_product,
            'orders': filtered_orders,
            'date_range': {
                'start': str(start_date) if start_date else None,
                'end': str(end_date) if end_date else None,
            }
        }

        pdf_file = render_pdf('report.html', context)
        log.info('Sales Analytics report created')
        return FileResponse(pdf_file, content_type='application/pdf')
    
def render_pdf(template_name, context):
    templates_dir = os.path.join(settings.BASE_DIR, 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_name)
    html_out = template.render(context)
    pdf_file = BytesIO()
    HTML(string=html_out).write_pdf(pdf_file)
    pdf_file.seek(0)
    return pdf_file
