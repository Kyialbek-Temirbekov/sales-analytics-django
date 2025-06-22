from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Client
from .serializers import ClientCreateSerializer, ClientReadSerializer
from drf_yasg.utils import swagger_auto_schema


class ClientListCreateApiView(APIView):
    @swagger_auto_schema(request_body=ClientCreateSerializer)
    def post(self, request):
        serializer = ClientCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientReadSerializer(clients, many=True)
        return Response(serializer.data)

class ClientDetailApiView(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Client, pk=pk)
        serializer = ClientReadSerializer(product)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ClientReadSerializer)
    def put(self, request, pk):
        product = get_object_or_404(Client, pk=pk)
        serializer = ClientReadSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Client, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
