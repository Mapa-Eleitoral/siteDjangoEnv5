from django.db import models
from django.utils import timezone
import uuid


class Doacao(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('cancelada', 'Cancelada'),
    ]
    
    TIPO_PAGAMENTO_CHOICES = [
        ('pix', 'PIX'),
        ('cartao', 'Cartão de Crédito'),
        ('boleto', 'Boleto'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome_doador = models.CharField(max_length=100, verbose_name='Nome do Doador')
    email_doador = models.EmailField(verbose_name='Email do Doador')
    telefone_doador = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    cpf_doador = models.CharField(max_length=14, blank=True, verbose_name='CPF')
    
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor da Doação')
    tipo_pagamento = models.CharField(max_length=20, choices=TIPO_PAGAMENTO_CHOICES, verbose_name='Tipo de Pagamento')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name='Status')
    
    # Dados da transação EFI Bank
    efi_transaction_id = models.CharField(max_length=100, blank=True, verbose_name='ID Transação EFI')
    efi_charge_id = models.CharField(max_length=100, blank=True, verbose_name='ID Cobrança EFI')
    efi_qr_code = models.TextField(blank=True, verbose_name='QR Code PIX')
    efi_qr_code_image = models.URLField(blank=True, verbose_name='Imagem QR Code')
    efi_copy_paste = models.TextField(blank=True, verbose_name='Código PIX Copia e Cola')
    
    mensagem = models.TextField(blank=True, verbose_name='Mensagem do Doador')
    anonimo = models.BooleanField(default=False, verbose_name='Doação Anônima')
    
    data_criacao = models.DateTimeField(default=timezone.now, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    data_pagamento = models.DateTimeField(null=True, blank=True, verbose_name='Data do Pagamento')
    
    class Meta:
        verbose_name = 'Doação'
        verbose_name_plural = 'Doações'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f'{self.nome_doador} - R$ {self.valor} - {self.get_status_display()}'
    
    @property
    def valor_formatado(self):
        return f'R$ {self.valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


class ConfiguracaoEFI(models.Model):
    """Configurações da integração com EFI Bank"""
    
    client_id = models.CharField(max_length=200, verbose_name='Client ID')
    client_secret = models.CharField(max_length=200, verbose_name='Client Secret')
    certificate_path = models.CharField(max_length=500, verbose_name='Caminho do Certificado')
    sandbox = models.BooleanField(default=True, verbose_name='Modo Sandbox')
    
    webhook_url = models.URLField(blank=True, verbose_name='URL do Webhook')
    
    ativa = models.BooleanField(default=True, verbose_name='Configuração Ativa')
    data_criacao = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Configuração EFI Bank'
        verbose_name_plural = 'Configurações EFI Bank'
    
    def __str__(self):
        return f'EFI Bank - {"Sandbox" if self.sandbox else "Produção"}'


class LogTransacao(models.Model):
    """Log de transações com EFI Bank"""
    
    doacao = models.ForeignKey(Doacao, on_delete=models.CASCADE, related_name='logs')
    evento = models.CharField(max_length=100, verbose_name='Evento')
    dados = models.JSONField(verbose_name='Dados da Transação')
    resposta_efi = models.JSONField(blank=True, null=True, verbose_name='Resposta EFI')
    sucesso = models.BooleanField(default=True, verbose_name='Sucesso')
    erro = models.TextField(blank=True, verbose_name='Erro')
    
    data_criacao = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Log de Transação'
        verbose_name_plural = 'Logs de Transações'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f'{self.doacao.nome_doador} - {self.evento} - {self.data_criacao}'