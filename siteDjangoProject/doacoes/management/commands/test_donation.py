from django.core.management.base import BaseCommand
from doacoes.models import Doacao
from doacoes.efi_service import EFIBankService
from decimal import Decimal


class Command(BaseCommand):
    help = 'Testa o sistema de doações'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Testando sistema de doações...')
        
        try:
            # Criar doação de teste
            doacao = Doacao.objects.create(
                nome_doador='João Teste',
                email_doador='teste@teste.com',
                telefone_doador='(11) 99999-9999',
                valor=Decimal('25.00'),
                tipo_pagamento='pix',
                mensagem='Teste de doação'
            )
            
            self.stdout.write(f'✅ Doação criada: {doacao.id}')
            
            # Testar EFI Service
            efi_service = EFIBankService()
            resultado = efi_service.criar_cobranca_pix(doacao)
            
            if resultado['sucesso']:
                self.stdout.write('✅ Cobrança PIX criada com sucesso!')
                self.stdout.write(f'   Transaction ID: {doacao.efi_transaction_id}')
                self.stdout.write(f'   QR Code gerado: {"Sim" if doacao.efi_qr_code else "Não"}')
                
                # Atualizar status
                doacao.status = 'processando'
                doacao.save()
                
                self.stdout.write('✅ Status atualizado para "processando"')
                
                # Testar URL de pagamento
                self.stdout.write(f'🔗 URL de pagamento: http://127.0.0.1:8000/doacoes/pagamento/{doacao.id}/')
                
            else:
                self.stdout.write(f'❌ Erro na cobrança: {resultado["erro"]}')
                
        except Exception as e:
            self.stdout.write(f'❌ Erro no teste: {str(e)}')
        
        self.stdout.write('🏁 Teste concluído!')