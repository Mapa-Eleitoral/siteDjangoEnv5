from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import json
import logging

from .models import Doacao, ConfiguracaoEFI, LogTransacao
from .efi_service import EFIBankService

logger = logging.getLogger(__name__)


class DoacaoView(TemplateView):
    template_name = 'doacoes/doacao.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['valores_sugeridos'] = [10, 25, 50, 100, 250, 500]
        return context


def processar_doacao(request):
    """Processa uma nova doação"""
    if request.method == 'POST':
        try:
            # Dados do formulário
            nome_doador = request.POST.get('nome_doador')
            email_doador = request.POST.get('email_doador')
            telefone_doador = request.POST.get('telefone_doador', '')
            cpf_doador = request.POST.get('cpf_doador', '')
            valor = Decimal(request.POST.get('valor'))
            tipo_pagamento = request.POST.get('tipo_pagamento')
            mensagem = request.POST.get('mensagem', '')
            anonimo = request.POST.get('anonimo') == 'on'
            
            # Validações básicas
            if not nome_doador or not email_doador or not valor:
                messages.error(request, 'Dados obrigatórios não preenchidos.')
                return redirect('doacoes:doacao')
            
            if valor < Decimal('5.00'):
                messages.error(request, 'Valor mínimo para doação é R$ 5,00.')
                return redirect('doacoes:doacao')
            
            # Criar doação
            doacao = Doacao.objects.create(
                nome_doador=nome_doador,
                email_doador=email_doador,
                telefone_doador=telefone_doador,
                cpf_doador=cpf_doador,
                valor=valor,
                tipo_pagamento=tipo_pagamento,
                mensagem=mensagem,
                anonimo=anonimo
            )
            
            # Processar pagamento via EFI Bank
            efi_service = EFIBankService()
            
            if tipo_pagamento == 'pix':
                resultado = efi_service.criar_cobranca_pix(doacao)
            elif tipo_pagamento == 'cartao':
                resultado = efi_service.criar_cobranca_cartao(doacao)
            elif tipo_pagamento == 'boleto':
                resultado = efi_service.criar_cobranca_boleto(doacao)
            else:
                messages.error(request, 'Tipo de pagamento inválido.')
                return redirect('doacoes:doacao')
            
            if resultado['sucesso']:
                doacao.status = 'processando'
                doacao.save()
                
                # Registrar log
                LogTransacao.objects.create(
                    doacao=doacao,
                    evento='cobranca_criada',
                    dados=resultado['dados'],
                    resposta_efi=resultado.get('resposta_efi'),
                    sucesso=True
                )
                
                return redirect('doacoes:pagamento', doacao_id=doacao.id)
            else:
                # Erro ao processar pagamento - debug detalhado
                erro_detalhado = resultado.get('erro', 'Erro desconhecido')
                resposta_completa = resultado.get('resposta_efi', {})
                
                logger.error(f'Erro EFI Bank: {erro_detalhado}')
                logger.error(f'Resposta completa EFI: {resposta_completa}')
                
                doacao.status = 'rejeitada'
                doacao.save()
                
                LogTransacao.objects.create(
                    doacao=doacao,
                    evento='erro_cobranca',
                    dados={
                        'erro': erro_detalhado,
                        'resposta_completa': resposta_completa,
                        'resultado_completo': resultado
                    },
                    sucesso=False,
                    erro=erro_detalhado
                )
                
                # Mostrar erro mais detalhado em desenvolvimento
                if settings.DEBUG:
                    messages.error(request, f'Erro detalhado: {erro_detalhado} | Resposta: {resposta_completa}')
                else:
                    messages.error(request, f'Erro ao processar pagamento: {erro_detalhado}')
                return redirect('doacoes:doacao')
                
        except Exception as e:
            logger.error(f'Erro ao processar doação: {str(e)}')
            messages.error(request, 'Erro interno. Tente novamente.')
            return redirect('doacoes:doacao')
    
    return redirect('doacoes:doacao')


def pagamento_view(request, doacao_id):
    """Exibe página de pagamento"""
    doacao = get_object_or_404(Doacao, id=doacao_id)
    
    context = {
        'doacao': doacao,
    }
    
    return render(request, 'doacoes/pagamento.html', context)


def status_doacao(request, doacao_id):
    """Retorna status da doação em JSON"""
    doacao = get_object_or_404(Doacao, id=doacao_id)
    
    data = {
        'status': doacao.status,
        'status_display': doacao.get_status_display(),
        'valor': str(doacao.valor),
        'data_criacao': doacao.data_criacao.isoformat(),
        'data_pagamento': doacao.data_pagamento.isoformat() if doacao.data_pagamento else None,
    }
    
    return JsonResponse(data)


def obrigado_view(request, doacao_id):
    """Página de agradecimento"""
    doacao = get_object_or_404(Doacao, id=doacao_id)
    
    context = {
        'doacao': doacao,
    }
    
    return render(request, 'doacoes/obrigado.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_efi(request):
    """Webhook para receber notificações do EFI Bank"""
    try:
        data = json.loads(request.body)
        
        # Log da notificação
        logger.info(f'Webhook EFI recebido: {data}')
        
        # Processar notificação
        efi_service = EFIBankService()
        resultado = efi_service.processar_webhook(data)
        
        if resultado['sucesso']:
            return HttpResponse('OK', status=200)
        else:
            logger.error(f'Erro ao processar webhook: {resultado["erro"]}')
            return HttpResponse('Erro', status=400)
            
    except Exception as e:
        logger.error(f'Erro no webhook EFI: {str(e)}')
        return HttpResponse('Erro', status=500)


def consultar_pagamento(request, doacao_id):
    """Consulta status do pagamento no EFI Bank"""
    doacao = get_object_or_404(Doacao, id=doacao_id)
    
    try:
        efi_service = EFIBankService()
        resultado = efi_service.consultar_cobranca(doacao)
        
        if resultado['sucesso']:
            # Atualizar status da doação
            status_efi = resultado['dados'].get('status')
            if status_efi == 'CONCLUIDA':
                doacao.status = 'aprovada'
                if not doacao.data_pagamento:
                    doacao.data_pagamento = timezone.now()
            elif status_efi == 'REJEITADA':
                doacao.status = 'rejeitada'
            
            doacao.save()
            
            # Registrar log
            LogTransacao.objects.create(
                doacao=doacao,
                evento='consulta_status',
                dados=resultado['dados'],
                resposta_efi=resultado.get('resposta_efi'),
                sucesso=True
            )
            
            return JsonResponse({
                'sucesso': True,
                'status': doacao.status,
                'status_display': doacao.get_status_display()
            })
        else:
            return JsonResponse({
                'sucesso': False,
                'erro': resultado['erro']
            })
            
    except Exception as e:
        logger.error(f'Erro ao consultar pagamento: {str(e)}')
        return JsonResponse({
            'sucesso': False,
            'erro': 'Erro interno'
        })


def debug_view(request):
    """View para debug - só funciona com DEBUG=True"""
    from django.conf import settings
    import os
    from decouple import config
    
    if not settings.DEBUG:
        return HttpResponse('Debug desabilitado', status=403)
    
    debug_info = {
        'Django Settings': {
            'DEBUG': settings.DEBUG,
            'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
            'CSRF_TRUSTED_ORIGINS': getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'Não configurado'),
            'INSTALLED_APPS': 'doacoes' in settings.INSTALLED_APPS,
        },
        'Environment Variables': {
            'EFI_SANDBOX': config('EFI_SANDBOX', default='Não configurado'),
            'EFI_PIX_KEY': config('EFI_PIX_KEY', default='Não configurado'),
            'EFI_CLIENT_ID_PRODUCTION': config('EFI_CLIENT_ID_PRODUCTION', default='Não configurado')[:20] + '...' if config('EFI_CLIENT_ID_PRODUCTION', default='') else 'Não configurado',
            'DEBUG': config('DEBUG', default='Não configurado'),
        },
        'Database': {},
        'EFI Service': {}
    }
    
    # Testar conexão com banco
    try:
        from .models import Doacao
        count = Doacao.objects.count()
        debug_info['Database']['Conexão'] = f'OK - {count} doações'
    except Exception as e:
        debug_info['Database']['Erro'] = str(e)
    
    # Testar EFI Service
    try:
        from .efi_service import EFIBankService
        efi = EFIBankService()
        debug_info['EFI Service']['Configuração'] = 'OK'
        debug_info['EFI Service']['Sandbox'] = efi.config.sandbox
        debug_info['EFI Service']['Client ID'] = efi.config.client_id[:20] + '...' if efi.config.client_id else 'Não configurado'
    except Exception as e:
        debug_info['EFI Service']['Erro'] = str(e)
    
    # Renderizar como HTML simples
    html = '<html><head><title>Debug Info</title></head><body>'
    html += '<h1>Debug Information</h1>'
    html += '<style>body{font-family:monospace;} table{border-collapse:collapse;} td,th{border:1px solid #ddd;padding:8px;}</style>'
    
    for section, data in debug_info.items():
        html += f'<h2>{section}</h2><table>'
        for key, value in data.items():
            html += f'<tr><td><strong>{key}</strong></td><td>{value}</td></tr>'
        html += '</table><br>'
    
    html += '</body></html>'
    
    return HttpResponse(html)