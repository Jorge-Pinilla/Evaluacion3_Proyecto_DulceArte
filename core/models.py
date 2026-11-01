from django.contrib.auth.models import AbstractUser
from django.db import models

# 1. USUARIOS Y ROLES
class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('DUENO', 'Dueño / Administración'),
        ('VENDEDOR', 'Vendedor'),
        ('COCINERO', 'Cocinero / Taller'),
        ('REPARTIDOR', 'Repartidor / Despachos'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='VENDEDOR')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# 2. INVENTARIO (Insumos)
class Insumo(models.Model):
    nombre = models.CharField(max_length=100)
    unidad_medida = models.CharField(max_length=20, help_text="Ej: Kg, Litros, Unidades")
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_critico = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.nombre} ({self.stock_actual} {self.unidad_medida})"

# 3. PRODUCTOS Y RECETAS (BOM - Bill of Materials)
class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio_base = models.IntegerField()

    def __str__(self):
        return self.nombre

class RecetaBOM(models.Model):
    """Define qué insumos y qué cantidad gasta cada producto"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ingredientes')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad_necesaria = models.DecimalField(max_digits=10, decimal_places=2)

# 4. PEDIDOS Y TABLERO KANBAN
ESTADOS_KANBAN = (
    ('RECIBIDO', 'Recibido'),
    ('PREPARACION', 'En Preparación'),
    ('HORNEADO', 'Horneado / Decorado'),
    ('CALIDAD', 'Control de Calidad'),
    ('LISTO', 'Listo para Despacho'),
    ('DESPACHADO', 'Entregado al Cliente'),
)

class Pedido(models.Model):
    ESTADOS_KANBAN = ESTADOS_KANBAN  # Mantiene compatibilidad con vistas o plantillas existentes
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    nombre_cliente = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre Cliente/a")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    detalles_diseno = models.TextField(help_text="Especificaciones personalizadas, mensajes, colores.")
    fecha_entrega = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS_KANBAN, default='RECIBIDO')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        nombre = self.nombre_cliente if self.nombre_cliente else self.cliente.username
        return f"Pedido #{self.id} - {self.producto.nombre} ({nombre})"

# 5. LOGÍSTICA DE DESPACHO
class Despacho(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    repartidor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'REPARTIDOR'})
    direccion_entrega = models.CharField(max_length=255)
    confirmacion_firma = models.BooleanField(default=False, help_text="Marcar si el cliente firmó la recepción")
    foto_comprobante = models.ImageField(upload_to='comprobantes/', blank=True, null=True)

    def __str__(self):
        return f"Despacho Pedido #{self.pedido.id}"