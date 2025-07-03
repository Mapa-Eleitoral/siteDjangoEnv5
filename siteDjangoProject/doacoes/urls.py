from django.urls import path
from . import views

app_name = 'doacoes'

urlpatterns = [
    path('', views.DoacaoView.as_view(), name='doacao'),
    path('processar/', views.processar_doacao, name='processar'),
    path('pagamento/<uuid:doacao_id>/', views.pagamento_view, name='pagamento'),
    path('status/<uuid:doacao_id>/', views.status_doacao, name='status'),
    path('obrigado/<uuid:doacao_id>/', views.obrigado_view, name='obrigado'),
    path('webhook/efi/', views.webhook_efi, name='webhook_efi'),
    path('consultar/<uuid:doacao_id>/', views.consultar_pagamento, name='consultar'),
    path('debug/', views.debug_view, name='debug'),
]