from rest_framework import serializers
from .models import Order, OrderItem, Product

class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ['items']
        read_only_fields = ['status', 'created_at', 'total_sum']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        client = self.context['request'].user
        total_sum = 0
        validated_items = []

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            if not product.is_active:
                raise serializers.ValidationError(f"Product '{product.name}' is not active.")

            if product.stock_quantity < quantity:
                raise serializers.ValidationError(f"Not enough stock for product '{product.name}'.")

            item_total = product.price * quantity
            total_sum += item_total
            validated_items.append((product, quantity))

        order = Order.objects.create(client=client, total_sum=total_sum, **validated_data)

        for product, quantity in validated_items:
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        return order

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
