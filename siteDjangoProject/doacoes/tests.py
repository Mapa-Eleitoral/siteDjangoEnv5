from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Doacao, ConfiguracaoEFI


class DoacaoModelTest(TestCase):
    def test_create_doacao(self):
        """Teste de criação de doação"""
        doacao = Doacao.objects.create(
            nome_doador='Teste User',
            email_doador='teste@teste.com',
            valor=Decimal('50.00'),
            tipo_pagamento='pix'
        )
        
        self.assertEqual(doacao.nome_doador, 'Teste User')
        self.assertEqual(doacao.valor, Decimal('50.00'))
        self.assertEqual(doacao.status, 'pendente')
        self.assertEqual(doacao.valor_formatado, 'R$ 50,00')


class DoacaoViewTest(TestCase):
    def test_doacao_page(self):
        """Teste da página de doação"""
        response = self.client.get('/doacoes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Faça sua Doação')
    
    def test_processar_doacao_invalid_data(self):
        """Teste de processamento com dados inválidos"""
        response = self.client.post('/doacoes/processar/', {
            'nome_doador': '',
            'email_doador': 'invalid',
            'valor': 'abc'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect


class ConfiguracaoEFITest(TestCase):
    def test_create_config(self):
        """Teste de criação de configuração EFI"""
        config = ConfiguracaoEFI.objects.create(
            client_id='test_client',
            client_secret='test_secret',
            certificate_path='/path/to/cert',
            sandbox=True
        )
        
        self.assertTrue(config.sandbox)
        self.assertTrue(config.ativa)