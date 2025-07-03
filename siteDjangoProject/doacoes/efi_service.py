import requests
import json
import base64
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from decouple import config
from .models import ConfiguracaoEFI, LogTransacao

logger = logging.getLogger(__name__)


class EFIBankService:
    """Serviço para integração com EFI Bank API"""
    
    def __init__(self):
        self.config = self._get_config()
        self.base_url = 'https://sandbox.gerencianet.com.br' if self.config.sandbox else 'https://api.gerencianet.com.br'
        self.access_token = None
    
    def _get_config(self):
        """Obtém configuração ativa do EFI Bank"""
        try:
            # Primeiro tenta obter do banco de dados
            db_config = ConfiguracaoEFI.objects.filter(ativa=True).first()
            if db_config:
                return db_config
            
            # Fallback: usar variáveis de ambiente
            return self._get_config_from_env()
        except Exception:
            # Último recurso: variáveis de ambiente
            return self._get_config_from_env()
    
    def _get_config_from_env(self):
        """Obtém configuração das variáveis de ambiente"""
        class EnvConfig:
            def __init__(self):
                # Determinar ambiente (sandbox por padrão)
                self.sandbox = config('EFI_SANDBOX', default=True, cast=bool)
                
                if self.sandbox:
                    self.client_id = config('EFI_CLIENT_ID_SANDBOX', default='')
                    self.client_secret = config('EFI_CLIENT_SECRET_SANDBOX', default='')
                    self.certificate_path = config('EFI_CERTIFICATE_SANDBOX', default='')
                else:
                    self.client_id = config('EFI_CLIENT_ID_PRODUCTION', default='')
                    self.client_secret = config('EFI_CLIENT_SECRET_PRODUCTION', default='')
                    self.certificate_path = config('EFI_CERTIFICATE_PRODUCTION', default='')
        
        env_config = EnvConfig()
        
        # Validar se as credenciais foram fornecidas
        if not env_config.client_id or not env_config.client_secret:
            raise Exception('Credenciais EFI Bank não configuradas')
        
        return env_config
    
    def _certificate_exists(self):
        """Verifica se o certificado existe"""
        try:
            import os
            
            # Verificar se tem certificado em Base64 (para Railway)
            if self.config.sandbox:
                cert_b64 = config('EFI_CERTIFICATE_SANDBOX_B64', default='')
                if cert_b64:
                    return True
            else:
                cert_b64 = config('EFI_CERTIFICATE_PRODUCTION_B64', default='')
                if cert_b64:
                    return True
            
            # Verificar arquivo físico
            if hasattr(self.config, 'certificate_path') and self.config.certificate_path:
                return os.path.exists(self.config.certificate_path)
            return False
        except Exception:
            return False
    
    def _get_certificate_path(self):
        """Obtém o caminho do certificado, criando arquivo temporário se necessário"""
        try:
            import tempfile
            import base64
            import os
            
            # Tentar usar certificado Base64 primeiro (Railway)
            if self.config.sandbox:
                cert_b64 = config('EFI_CERTIFICATE_SANDBOX_B64', default='')
            else:
                cert_b64 = config('EFI_CERTIFICATE_PRODUCTION_B64', default='')
            
            if cert_b64:
                # Decodificar Base64 e criar arquivo temporário
                cert_data = base64.b64decode(cert_b64)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.p12')
                temp_file.write(cert_data)
                temp_file.close()
                return temp_file.name
            
            # Fallback para arquivo físico
            if hasattr(self.config, 'certificate_path') and self.config.certificate_path:
                if os.path.exists(self.config.certificate_path):
                    return self.config.certificate_path
            
            return None
        except Exception as e:
            logger.error(f'Erro ao obter certificado: {str(e)}')
            return None
    
    def _get_access_token(self):
        """Obtém token de acesso"""
        if self.access_token:
            return self.access_token
        
        try:
            # Codificar credenciais
            credentials = f"{self.config.client_id}:{self.config.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(
                f'{self.base_url}/v1/authorize',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                return self.access_token
            else:
                raise Exception(f'Erro ao obter token: {response.text}')
                
        except Exception as e:
            logger.error(f'Erro ao obter token EFI: {str(e)}')
            raise
    
    def _make_request(self, method, endpoint, data=None):
        """Faz requisição para API EFI Bank"""
        try:
            token = self._get_access_token()
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.base_url}{endpoint}'
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            else:
                raise Exception(f'Método HTTP não suportado: {method}')
            
            return {
                'sucesso': response.status_code in [200, 201],
                'status_code': response.status_code,
                'dados': response.json() if response.content else {},
                'resposta_raw': response.text
            }
            
        except Exception as e:
            logger.error(f'Erro na requisição EFI: {str(e)}')
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def criar_cobranca_pix(self, doacao):
        """Cria cobrança PIX"""
        try:
            # Para ambiente de desenvolvimento, simular cobrança se não tiver certificado válido
            if (self.config.sandbox and 
                (not hasattr(self.config, 'certificate_path') or 
                 not self.config.certificate_path or 
                 self.config.certificate_path in ['/path/to/sandbox_certificate.p12', './certificados/sandbox_certificate.p12'] or
                 not self._certificate_exists())):
                return self._simular_cobranca_pix(doacao)
            
            # Dados da cobrança
            cobranca_data = {
                'calendario': {
                    'expiracao': 3600  # 1 hora
                },
                'devedor': {
                    'nome': doacao.nome_doador,
                    'email': doacao.email_doador
                },
                'valor': {
                    'original': str(doacao.valor)
                },
                'chave': config('PIX_KEY', default='mapaeleitoral@outlook.com'),  # Chave PIX
                'solicitacaoPagador': f'Doação para Mapa Eleitoral - {doacao.mensagem}' if doacao.mensagem else 'Doação para Mapa Eleitoral'
            }
            
            # Adicionar CPF se fornecido
            if doacao.cpf_doador:
                cobranca_data['devedor']['cpf'] = doacao.cpf_doador.replace('.', '').replace('-', '')
            
            # Criar cobrança
            resultado = self._make_request('POST', '/v2/cob', cobranca_data)
            
            if resultado['sucesso']:
                dados = resultado['dados']
                
                # Atualizar doação com dados EFI
                doacao.efi_transaction_id = dados.get('txid')
                doacao.efi_charge_id = dados.get('loc', {}).get('id')
                
                # Gerar QR Code
                qr_resultado = self._gerar_qr_code(dados.get('loc', {}).get('id'))
                if qr_resultado['sucesso']:
                    doacao.efi_qr_code = qr_resultado['dados'].get('qrcode')
                    doacao.efi_qr_code_image = qr_resultado['dados'].get('imagemQrcode')
                    doacao.efi_copy_paste = qr_resultado['dados'].get('qrcode')
                
                doacao.save()
                
                return {
                    'sucesso': True,
                    'dados': dados,
                    'resposta_efi': resultado
                }
            else:
                return {
                    'sucesso': False,
                    'erro': resultado.get('erro', 'Erro desconhecido')
                }
                
        except Exception as e:
            logger.error(f'Erro ao criar cobrança PIX: {str(e)}')
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def _simular_cobranca_pix(self, doacao):
        """Simula cobrança PIX para desenvolvimento"""
        import uuid
        
        # Gerar dados simulados
        fake_txid = str(uuid.uuid4()).replace('-', '')[:32]
        pix_key = config('PIX_KEY', default='mapaeleitoral@outlook.com')
        fake_qr_code = f"00020126330014br.gov.bcb.pix{len(pix_key):02d}{pix_key}5204000053039865404{doacao.valor:.2f}5802BR6009SAO PAULO62070503***6304"
        
        # Atualizar doação
        doacao.efi_transaction_id = fake_txid
        doacao.efi_charge_id = f"loc_{fake_txid}"
        doacao.efi_qr_code = fake_qr_code
        doacao.efi_copy_paste = fake_qr_code
        doacao.efi_qr_code_image = f"data:image/svg+xml;base64,{base64.b64encode(b'<svg>QR Code Simulado</svg>').decode()}"
        doacao.save()
        
        return {
            'sucesso': True,
            'dados': {
                'txid': fake_txid,
                'loc': {'id': f"loc_{fake_txid}"},
                'status': 'ATIVA'
            },
            'resposta_efi': {'simulado': True}
        }
    
    def _gerar_qr_code(self, loc_id):
        """Gera QR Code para cobrança PIX"""
        return self._make_request('GET', f'/v2/loc/{loc_id}/qrcode')
    
    def criar_cobranca_cartao(self, doacao):
        """Cria cobrança com cartão de crédito"""
        try:
            # Implementar lógica de cartão de crédito
            # Por enquanto, retornar erro
            return {
                'sucesso': False,
                'erro': 'Pagamento com cartão não implementado ainda'
            }
            
        except Exception as e:
            logger.error(f'Erro ao criar cobrança cartão: {str(e)}')
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def criar_cobranca_boleto(self, doacao):
        """Cria cobrança com boleto"""
        try:
            # Implementar lógica de boleto
            # Por enquanto, retornar erro
            return {
                'sucesso': False,
                'erro': 'Pagamento com boleto não implementado ainda'
            }
            
        except Exception as e:
            logger.error(f'Erro ao criar cobrança boleto: {str(e)}')
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def consultar_cobranca(self, doacao):
        """Consulta status da cobrança"""
        try:
            if not doacao.efi_transaction_id:
                return {
                    'sucesso': False,
                    'erro': 'ID da transação não encontrado'
                }
            
            resultado = self._make_request('GET', f'/v2/cob/{doacao.efi_transaction_id}')
            
            if resultado['sucesso']:
                return {
                    'sucesso': True,
                    'dados': resultado['dados'],
                    'resposta_efi': resultado
                }
            else:
                return {
                    'sucesso': False,
                    'erro': resultado.get('erro', 'Erro ao consultar cobrança')
                }
                
        except Exception as e:
            logger.error(f'Erro ao consultar cobrança: {str(e)}')
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def processar_webhook(self, data):
        """Processa webhook do EFI Bank"""
        try:
            # Extrair dados do webhook
            pix_data = data.get('pix', [])
            
            for pix in pix_data:
                txid = pix.get('txid')
                if not txid:
                    continue
                
                # Buscar doação
                try:
                    doacao = Doacao.objects.get(efi_transaction_id=txid)
                except Doacao.DoesNotExist:
                    logger.warning(f'Doação não encontrada para txid: {txid}')
                    continue
                
                # Atualizar status
                if pix.get('status') == 'CONCLUIDA':
                    doacao.status = 'aprovada'
                    if not doacao.data_pagamento:
                        doacao.data_pagamento = timezone.now()
                elif pix.get('status') == 'REJEITADA':
                    doacao.status = 'rejeitada'
                
                doacao.save()
                
                # Registrar log
                LogTransacao.objects.create(
                    doacao=doacao,
                    evento='webhook_recebido',
                    dados=pix,
                    sucesso=True
                )
            
            return {
                'sucesso': True,
                'dados': data
            }
            
        except Exception as e:
            logger.error(f'Erro ao processar webhook: {str(e)}')
            return {
                'sucesso': False,
                'erro': str(e)
            }