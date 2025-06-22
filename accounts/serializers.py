from rest_framework import serializers
from .models import Client

class ClientCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Client
        fields = ['email', 'full_name', 'company_name', 'phone', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        client = Client(**validated_data)
        client.set_password(password)
        client.save()
        return client

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ClientReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'company_name', 'phone', 'created_at']
        read_only_fields = ['created_at']
