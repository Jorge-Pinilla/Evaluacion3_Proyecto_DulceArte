from django.contrib import admin
from .models import User, Insumo, Producto, RecetaBOM, Pedido, Despacho

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    list_filter = ('role',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'producto', 'estado', 'fecha_entrega')
    list_filter = ('estado',)
    search_fields = ('cliente__username', 'detalles_diseno')

admin.site.register(Insumo)
admin.site.register(Producto)
admin.site.register(RecetaBOM)
admin.site.register(Despacho)