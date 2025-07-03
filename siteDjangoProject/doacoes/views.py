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
                # Erro ao processar pagamento
                doacao.status = 'rejeitada'
                doacao.save()
                
                LogTransacao.objects.create(
                    doacao=doacao,
                    evento='erro_cobranca',
                    dados={'erro': resultado['erro']},
                    sucesso=False,
                    erro=resultado['erro']
                )
                
                messages.error(request, f'Erro ao processar pagamento: {resultado["erro"]}')
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