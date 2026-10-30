from rest_framework import serializers
from core.models import User, Insumo, Producto, Pedido, Despacho

class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar nombres en vez de solo IDs
    cliente_nombre = serializers.CharField(source='cliente.username', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'cliente', 'cliente_nombre', 'producto', 'producto_nombre', 'detalles_diseno', 'fecha_entrega', 'estado', 'creado_en']
        # El cliente se asigna por token, y el estado inicial siempre es RECIBIDO
        read_only_fields = ['cliente', 'estado', 'creado_en']

class DespachoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Despacho
        fields = '__all__'