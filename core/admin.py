from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Insumo, Producto, RecetaBOM, Pedido, Despacho

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Rol en Dulce Arte', {'fields': ('role',)}),
    )

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad_medida', 'stock_actual', 'stock_critico', 'estado_stock')
    list_filter = ('unidad_medida',)
    search_fields = ('nombre',)

    def estado_stock(self, obj):
        return "CRÍTICO" if obj.stock_actual <= obj.stock_critico else "OK"
    estado_stock.short_description = 'Estado'

class RecetaBOMInline(admin.TabularInline):
    model = RecetaBOM
    extra = 1

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base')
    search_fields = ('nombre',)
    inlines = [RecetaBOMInline]

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'producto', 'estado', 'fecha_entrega', 'creado_en')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('nombre_cliente', 'producto__nombre', 'detalles_diseno')
    date_hierarchy = 'fecha_entrega'

@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'repartidor', 'direccion_entrega', 'confirmacion_firma')
    list_filter = ('confirmacion_firma', 'repartidor')
    search_fields = ('direccion_entrega', 'pedido__id', 'pedido__nombre_cliente')