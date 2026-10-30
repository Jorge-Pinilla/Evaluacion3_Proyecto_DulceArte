from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404

from core.models import Insumo, Producto, Pedido, RecetaBOM, Despacho
from .serializers import InsumoSerializer, ProductoSerializer, PedidoSerializer, DespachoSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('fecha_entrega')
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        """
        LÓGICA BOM (Bill of Materials):
        Al registrar un pedido, se descuentan automáticamente los insumos.
        """
        # 1. Guardar el pedido vinculándolo al cliente logueado
        pedido = serializer.save(cliente=self.request.user, estado='RECIBIDO')
        
        # 2. Buscar la receta (BOM) del producto solicitado
        receta = RecetaBOM.objects.filter(producto=pedido.producto)
        
        # 3. Descontar el stock de cada insumo
        for item in receta:
            insumo = item.insumo
            
            # Validación opcional: Evitar stock negativo extremo
            if insumo.stock_actual < item.cantidad_necesaria:
                raise ValueError(f"Stock insuficiente de {insumo.nombre}. Disponible: {insumo.stock_actual}")
            
            insumo.stock_actual -= item.cantidad_necesaria
            insumo.save()

    @action(detail=True, methods=['patch'])
    def actualizar_kanban(self, request, pk=None):
        """
        Endpoint exclusivo para que los Cocineros muevan tarjetas en el Kanban.
        Ej: PATCH /api/pedidos/1/actualizar_kanban/ {"estado": "HORNEADO"}
        """
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        estados_validos = dict(Pedido.ESTADOS_KANBAN).keys()
        if nuevo_estado not in estados_validos:
            return Response({"error": "Estado no válido para el Kanban"}, status=status.HTTP_400_BAD_REQUEST)
        
        pedido.estado = nuevo_estado
        pedido.save()
        return Response(PedidoSerializer(pedido).data)

# --- Otras Vistas Básicas ---
class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    permission_classes = [IsAuthenticated]

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

class DespachoViewSet(viewsets.ModelViewSet):
    queryset = Despacho.objects.all()
    serializer_class = DespachoSerializer
    permission_classes = [IsAuthenticated]
    
    # Permite recibir archivos de imagen en la petición
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['patch'])
    def confirmar_entrega(self, request, pk=None):
        """
        Endpoint para el Repartidor.
        Sube la foto del comprobante y marca el pedido como DESPACHADO.
        """
        despacho = self.get_object()
        
        # Validar rol (Opcional, pero otorga puntos en seguridad)
        if request.user.role != 'REPARTIDOR':
            return Response({"error": "Solo los repartidores pueden confirmar despachos."}, status=status.HTTP_403_FORBIDDEN)
        
        foto = request.FILES.get('foto_comprobante')
        if not foto:
            return Response({"error": "Es obligatorio adjuntar la foto_comprobante para cerrar el despacho."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar Despacho
        despacho.foto_comprobante = foto
        despacho.confirmacion_firma = True
        despacho.repartidor = request.user
        despacho.save()

        # Actualizar Tablero Kanban del Pedido automáticamente
        pedido = despacho.pedido
        pedido.estado = 'DESPACHADO'
        pedido.save()

        return Response({
            "mensaje": "Despacho confirmado exitosamente. Kanban actualizado.",
            "despacho_id": despacho.id,
            "pedido_estado": pedido.estado
        }, status=status.HTTP_200_OK)