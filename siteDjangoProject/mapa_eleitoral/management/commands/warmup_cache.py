"""
Comando Django para aquecimento do cache
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from mapa_eleitoral.cache_utils import cache_manager, preload_critical_data
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Aquece o cache com dados frequentemente acessados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['all', 'electoral', 'blog', 'maps'],
            default='all',
            help='Tipo de cache para aquecer'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpar cache antes do aquecimento'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando aquecimento do cache...'))
        
        # Limpar cache se solicitado
        if options['clear']:
            self.stdout.write('Limpando cache existente...')
            cache_manager.invalidate_pattern('*', 'electoral')
            cache_manager.invalidate_pattern('*', 'blog')
            cache_manager.invalidate_pattern('*', 'maps')
            cache_manager.invalidate_pattern('*', 'api')
            
        cache_type = options['type']
        
        try:
            if cache_type in ['all', 'electoral']:
                self.stdout.write('Aquecendo cache de dados eleitorais...')
                cache_manager.warm_up_cache()
            
            if cache_type in ['all', 'blog']:
                self.stdout.write('Aquecendo cache do blog...')
                preload_critical_data()
            
            # Mostrar estatísticas do cache
            stats = cache_manager.get_cache_stats()
            self.stdout.write(self.style.SUCCESS('Estatísticas do cache:'))
            for cache_name, cache_stats in stats.items():
                self.stdout.write(f"  {cache_name}: {cache_stats['backend']}")
            
            self.stdout.write(
                self.style.SUCCESS('Aquecimento do cache concluído com sucesso!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante aquecimento: {str(e)}')
            )
            logger.error(f'Erro no aquecimento do cache: {e}', exc_info=True)
            raise