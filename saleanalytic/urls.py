"""
URL configuration for saleanalytic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from products.views import ProductDetailApiView, ProductListCreateApiView
from accounts.views import ClientListCreateApiView, ClientDetailApiView
from orders.views import OrderListCreateView, OrderStatusUpdateApiView, ReportApiView

schema_view = get_schema_view(
   openapi.Info(
      title="Sales Analytics API",
      default_version='v1',
      description="API documentation",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('api/products/<int:pk>/', ProductDetailApiView.as_view(), name='product-view'),
    path('api/products/', ProductListCreateApiView.as_view(), name='product-list-create-view'),

    path('api/clients/<int:pk>/', ClientDetailApiView.as_view(), name='client-view'),
    path('api/clients/', ClientListCreateApiView.as_view(), name='client-list-create-view'),

    path('api/orders/<int:pk>/', OrderStatusUpdateApiView.as_view(), name='order-status-update-view'),
    path('api/orders/', OrderListCreateView.as_view(), name='order-list-create-view'),
    path('api/reports/sales/', ReportApiView.as_view(), name='report-sales'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
