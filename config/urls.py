# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.views import PedidoViewSet, InsumoViewSet, ProductoViewSet, DespachoViewSet
from core.views import (
    dashboard_view, 
    kanban_view, 
    inventario_view, 
    despachos_view, 
    crear_pedido_view, 
    eliminar_pedido_view,
    agregar_insumo_view,     
    reabastecer_insumo_view, 
    eliminar_insumo_view,
    completar_despacho_view,
    crear_despacho_manual_view,
    error_404_view,
    login_view,       # <-- Vista de inicio de sesión
    registro_view,    # <-- Vista de registro
    logout_view       # <-- Vista de cierre de sesión
)

handler404 = 'core.views.error_404_view'

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'insumos', InsumoViewSet, basename='insumo')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'despachos', DespachoViewSet, basename='despacho')

schema_view = get_schema_view(
   openapi.Info(
      title="Dulce Arte API",
      default_version='v1',
      description="API para gestión de Pastelería, Kanban y BOM",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # Autenticación y Registro
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('logout/', logout_view, name='logout'),
    
    # Rutas Web
    path('', dashboard_view, name='dashboard'),
    path('kanban/', kanban_view, name='kanban'),
    path('inventario/', inventario_view, name='inventario'),
    path('despachos/', despachos_view, name='despachos'),
    path('pedidos/nuevo/', crear_pedido_view, name='crear_pedido'),
    path('pedidos/<int:pedido_id>/eliminar/', eliminar_pedido_view, name='eliminar_pedido'),
    
    # Rutas de Inventario
    path('inventario/agregar/', agregar_insumo_view, name='agregar_insumo'),
    path('inventario/<int:insumo_id>/reabastecer/', reabastecer_insumo_view, name='reabastecer_insumo'),
    path('inventario/<int:insumo_id>/eliminar/', eliminar_insumo_view, name='eliminar_insumo'),
    
    # Rutas de Despacho
    path('despachos/<int:despacho_id>/completar/', completar_despacho_view, name='completar_despacho'),
    path('despachos/crear_manual/', crear_despacho_manual_view, name='crear_despacho_manual'),
]

urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]