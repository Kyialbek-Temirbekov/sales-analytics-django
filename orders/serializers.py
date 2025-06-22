from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem, Product, Client
import logging

log = logging.getLogger(__name__)


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    total_sum = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'items', 'status', 'created_at', 'total_sum']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        client = Client.objects.get(id=1) #self.context['request'].user
        subtotal = Decimal('0.00')
        validated_items = []

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            if not product.is_active:
                raise serializers.ValidationError(f"Product '{product.name}' is not active.")

            if product.stock_quantity < quantity:
                raise serializers.ValidationError(f"Not enough stock for product '{product.name}'.")

            item_total = product.price * quantity
            subtotal += item_total
            validated_items.append((product, quantity))

         # Скидка по клиенту
        client_discount = getattr(client, 'discount_percent', 0)
        discount = subtotal * Decimal(client_discount) / 100

        # Глобальная скидка, если сумма больше 150000
        if subtotal >= 150000:
            discount += subtotal * Decimal('0.10')

        # НДС 12%
        tax = (subtotal - discount) * Decimal('0.12')

        # Доставка: бесплатно, если > 2000
        delivery = Decimal('0.00') if subtotal >= 2000 else Decimal('300.00')

        # Итог
        total_sum = subtotal - discount + tax + delivery
        log.info(f"Subtotal '{subtotal}', Total '{total_sum}'")

        order = Order.objects.create(client=client, total_sum=total_sum, **validated_data)

        for product, quantity in validated_items:
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        return order

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
