from django.core.management.base import BaseCommand
from doacoes.models import ConfiguracaoEFI


class Command(BaseCommand):
    help = 'Configura as credenciais do EFI Bank'

    def add_arguments(self, parser):
        parser.add_argument(
            '--environment',
            type=str,
            choices=['sandbox', 'production'],
            default='sandbox',
            help='Ambiente: sandbox (homologação) ou production (produção)'
        )

    def handle(self, *args, **options):
        environment = options['environment']
        
        # Limpar configurações existentes
        ConfiguracaoEFI.objects.all().update(ativa=False)
        
        if environment == 'sandbox':
            config = ConfiguracaoEFI.objects.create(
                client_id='Client_Id_53aaf22c522c3e164c6a7f9719b4f7f8c3ea1aef',
                client_secret='Client_Secret_4b2618ae13adceb9041faef0e300334e3c28d94a',
                certificate_path='./certificados/homologacao-792139-mapa-eleitoral-homologacao.p12',
                sandbox=True,
                webhook_url='https://sitedjangoenv4-production.up.railway.app/doacoes/webhook/efi/',
                ativa=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Configuração de HOMOLOGAÇÃO criada com sucesso!')
            )
        
        elif environment == 'production':
            config = ConfiguracaoEFI.objects.create(
                client_id='Client_Id_7949b42e84a24dbc9990f758c38b3395296212d4',
                client_secret='Client_Secret_4aeb1f33e2ce33723b2212afec2566d2dd250553',
                certificate_path='./certificados/producao-792139-mapa-eleitoral-certificado.p12',
                sandbox=False,
                webhook_url='https://mapaeleitoral.com.br/doacoes/webhook/efi/',
                ativa=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Configuração de PRODUÇÃO criada com sucesso!')
            )
        
        self.stdout.write(
            self.style.WARNING('⚠️  IMPORTANTE: Atualize o caminho do certificado no Django Admin!')
        )
        self.stdout.write(
            self.style.WARNING('⚠️  Configure o webhook URL no painel EFI Bank!')
        )