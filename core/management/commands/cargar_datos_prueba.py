# core/management/commands/cargar_datos_prueba.py
from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
from core.models import User, Insumo, Producto, RecetaBOM, Pedido

class Command(BaseCommand):
    help = 'Carga datos de prueba iniciales para el proyecto Dulce Arte'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generando datos de prueba...")

        # 1. Crear usuarios de prueba si no existen
        cliente, _ = User.objects.get_or_create(
            username='cliente_test', 
            defaults={'email': 'cliente@dulcearte.cl', 'role': 'CLIENTE', 'first_name': 'Ana', 'last_name': 'Pérez'}
        )
        if not cliente.check_password('password123'):
            cliente.set_password('password123')
            cliente.save()

        # 2. Crear Insumos para la bodega (BOM)
        harina, _ = Insumo.objects.get_or_create(nombre='Harina de Trigo', defaults={'unidad_medida': 'Kg', 'stock_actual': 50.0, 'stock_critico': 10.0})
        azucar, _ = Insumo.objects.get_or_create(nombre='Azúcar Flor', defaults={'unidad_medida': 'Kg', 'stock_actual': 30.0, 'stock_critico': 5.0})
        chocolate, _ = Insumo.objects.get_or_create(nombre='Chocolate Belga', defaults={'unidad_medida': 'Kg', 'stock_actual': 15.0, 'stock_critico': 3.0})
        manjar, _ = Insumo.objects.get_or_create(nombre='Manjar Artesanal', defaults={'unidad_medida': 'Litros', 'stock_actual': 25.0, 'stock_critico': 5.0})

        # 3. Crear Productos (Pasteles)
        torta_choco, _ = Producto.objects.get_or_create(
            nombre='Torta de Chocolate Trufa',
            defaults={'descripcion': 'Bizcocho de chocolate húmedo con relleno de trufa.', 'precio_base': 22990}
        )
        torta_mil_hojas, _ = Producto.objects.get_or_create(
            nombre='Mil Hojas Tradicional',
            defaults={'descripcion': 'Hojaldre crujiente relleno de manjar y lúcuma.', 'precio_base': 18990}
        )

        # 4. Asignar Recetas (BOM)
        RecetaBOM.objects.get_or_create(producto=torta_choco, insumo=harina, defaults={'cantidad_necesaria': 0.5})
        RecetaBOM.objects.get_or_create(producto=torta_choco, insumo=chocolate, defaults={'cantidad_necesaria': 0.8})
        RecetaBOM.objects.get_or_create(producto=torta_mil_hojas, insumo=harina, defaults={'cantidad_necesaria': 0.4})
        RecetaBOM.objects.get_or_create(producto=torta_mil_hojas, insumo=manjar, defaults={'cantidad_necesaria': 1.0})

        # 5. Crear Pedidos de Prueba en diferentes estados del Kanban
        ahora = timezone.now()
        Pedido.objects.get_or_create(
            id=101,
            defaults={
                'cliente': cliente,
                'producto': torta_choco,
                'detalles_diseno': 'Dedicatoria: "Feliz Cumpleaños Mamá" en fondant blanco.',
                'fecha_entrega': ahora + datetime.timedelta(days=1),
                'estado': 'RECIBIDO'
            }
        )
        Pedido.objects.get_or_create(
            id=102,
            defaults={
                'cliente': cliente,
                'producto': torta_mil_hojas,
                'detalles_diseno': 'Forma rectangular para 20 personas con detalles dorados.',
                'fecha_entrega': ahora + datetime.timedelta(hours=12),
                'estado': 'PREPARACION'
            }
        )
        Pedido.objects.get_or_create(
            id=103,
            defaults={
                'cliente': cliente,
                'producto': torta_choco,
                'detalles_diseno': 'Sin nueces, cobertura extra de chocolate.',
                'fecha_entrega': ahora + datetime.timedelta(hours=4),
                'estado': 'HORNEADO'
            }
        )

        self.stdout.write(self.style.SUCCESS("¡Datos de prueba cargados exitosamente!"))