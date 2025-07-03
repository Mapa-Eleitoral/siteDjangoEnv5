from django.contrib import admin
from django.utils.html import format_html
from .models import Doacao, ConfiguracaoEFI, LogTransacao


@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
    list_display = ['nome_doador', 'valor_formatado', 'tipo_pagamento', 'status_badge', 'data_criacao']
    list_filter = ['status', 'tipo_pagamento', 'anonimo', 'data_criacao']
    search_fields = ['nome_doador', 'email_doador', 'efi_transaction_id']
    readonly_fields = ['id', 'data_criacao', 'data_atualizacao', 'efi_transaction_id', 'efi_charge_id']
    
    fieldsets = (
        ('Dados do Doador', {
            'fields': ('nome_doador', 'email_doador', 'telefone_doador', 'cpf_doador', 'anonimo')
        }),
        ('Doação', {
            'fields': ('valor', 'tipo_pagamento', 'status', 'mensagem')
        }),
        ('Dados EFI Bank', {
            'fields': ('efi_transaction_id', 'efi_charge_id', 'efi_qr_code', 'efi_qr_code_image', 'efi_copy_paste'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao', 'data_pagamento')
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pendente': 'orange',
            'processando': 'blue',
            'aprovada': 'green',
            'rejeitada': 'red',
            'cancelada': 'gray',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def valor_formatado(self, obj):
        return obj.valor_formatado
    valor_formatado.short_description = 'Valor'
    
    actions = ['marcar_como_aprovada', 'marcar_como_rejeitada']
    
    def marcar_como_aprovada(self, request, queryset):
        queryset.update(status='aprovada')
    marcar_como_aprovada.short_description = 'Marcar doações como aprovadas'
    
    def marcar_como_rejeitada(self, request, queryset):
        queryset.update(status='rejeitada')
    marcar_como_rejeitada.short_description = 'Marcar doações como rejeitadas'


@admin.register(ConfiguracaoEFI)
class ConfiguracaoEFIAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'ativa', 'sandbox', 'data_criacao']
    list_filter = ['ativa', 'sandbox']
    
    fieldsets = (
        ('Credenciais', {
            'fields': ('client_id', 'client_secret', 'certificate_path')
        }),
        ('Configurações', {
            'fields': ('sandbox', 'webhook_url', 'ativa')
        }),
    )


@admin.register(LogTransacao)
class LogTransacaoAdmin(admin.ModelAdmin):
    list_display = ['doacao', 'evento', 'sucesso', 'data_criacao']
    list_filter = ['sucesso', 'evento', 'data_criacao']
    search_fields = ['doacao__nome_doador', 'evento']
    readonly_fields = ['data_criacao']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False