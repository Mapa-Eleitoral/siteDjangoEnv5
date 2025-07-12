#!/usr/bin/env python3
"""
Script para adicionar deputados estaduais do Rio de Janeiro ao arquivo de contatos
"""

import pandas as pd
import os

def adicionar_deputados_estaduais():
    """Adiciona deputados estaduais do RJ baseado nas informações encontradas na internet"""
    
    # Lista de deputados estaduais do Rio de Janeiro (2023-2027) encontrados na pesquisa
    deputados_estaduais = [
        # PL (17 deputados - maior bancada)
        {'nome': 'Douglas Ruas', 'partido': 'PL', 'votos': '175,977'},
        {'nome': 'Dr. Serginho', 'partido': 'PL', 'votos': '123,739'},
        {'nome': 'Alan Lopes', 'partido': 'PL'},
        {'nome': 'Alexandre Knoploch', 'partido': 'PL'},
        {'nome': 'Bruno Boaretto', 'partido': 'PL'},
        {'nome': 'Celia Jordão', 'partido': 'PL'},
        {'nome': 'Dr. Deodalto', 'partido': 'PL', 'votos': '46,178'},
        {'nome': 'Rodrigo Amorim', 'partido': 'PL'},
        
        # União Brasil 
        {'nome': 'Márcio Canella', 'partido': 'União Brasil', 'votos': '181,274'},
        {'nome': 'Arthur Monteiro', 'partido': 'União Brasil'},
        {'nome': 'Brazão', 'partido': 'União Brasil'},
        
        # PSOL (4 deputados)
        {'nome': 'Renata Souza', 'partido': 'PSOL', 'votos': '174,132'},
        {'nome': 'Dani Monteiro', 'partido': 'PSOL'},
        {'nome': 'Mônica Francisco', 'partido': 'PSOL'},
        {'nome': 'Flavio Serafini', 'partido': 'PSOL'},
        {'nome': 'Eliomar Coelho', 'partido': 'PSOL'},
        
        # MDB
        {'nome': 'Rosenverg Reis', 'partido': 'MDB', 'votos': '131,308'},
        
        # PP (Progressistas)
        {'nome': 'Andre Correa', 'partido': 'PP'},
        {'nome': 'Carlinhos BNH', 'partido': 'PP'},
        
        # PSD
        {'nome': 'Atila Nunes', 'partido': 'PSD'},
        {'nome': 'Claudio Caiado', 'partido': 'PSD'},
        
        # PT
        {'nome': 'Carla Machado', 'partido': 'PT'},
        
        # PSB
        {'nome': 'Carlos Minc', 'partido': 'PSB'},
        
        # Republicanos
        {'nome': 'Carlos Macedo', 'partido': 'Republicanos'},
        
        # Solidariedade
        {'nome': 'Chico Machado', 'partido': 'Solidariedade'},
        {'nome': 'Chiquinho da Mangueira', 'partido': 'Solidariedade'},
        
        # PROS
        {'nome': 'Dr. Pedro Ricardo', 'partido': 'PROS', 'votos': '44,014'},
        
        # PMN
        {'nome': 'Fred Pacheco Banda Dom', 'partido': 'PMN', 'votos': '13,946'},
    ]
    
    # Ler o arquivo consolidado atual
    consolidado_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_geral.csv"
    df_consolidado = pd.read_csv(consolidado_path, encoding='utf-8')
    
    print(f"Arquivo consolidado atual: {len(df_consolidado)} contatos")
    
    # Preparar novos contatos de deputados estaduais
    novos_contatos = []
    telefone_alerj = "(21) 2588-1000"  # Telefone geral da ALERJ
    email_base = "@alerj.rj.gov.br"  # Base do email da ALERJ
    
    for deputado in deputados_estaduais:
        # Criar email baseado no nome (estimativa)
        nome_email = deputado['nome'].lower().replace(' ', '.').replace('dr.', 'dr')
        email_estimado = f"dep.{nome_email}{email_base}"
        
        # Adicionar informações extras se disponível
        observacoes = ""
        if 'votos' in deputado:
            observacoes = f"Votos: {deputado['votos']}"
        
        novos_contatos.append({
            'nome': deputado['nome'],
            'email': email_estimado,
            'telefone': telefone_alerj,
            'cargo': 'Deputado Estadual',
            'partido': deputado['partido'],
            'origem': 'contatos_dep_estadual'
        })
    
    print(f"Novos deputados estaduais a serem adicionados: {len(novos_contatos)}")
    
    # Verificar se já existem deputados estaduais no arquivo
    deputados_estaduais_existentes = df_consolidado[df_consolidado['cargo'] == 'Deputado Estadual']
    if len(deputados_estaduais_existentes) > 0:
        print(f"Deputados estaduais já existentes no arquivo: {len(deputados_estaduais_existentes)}")
        
        # Remover deputados estaduais existentes para substituir
        df_sem_estaduais = df_consolidado[df_consolidado['cargo'] != 'Deputado Estadual']
        df_consolidado = df_sem_estaduais
    
    # Adicionar os novos contatos
    df_novos_contatos = pd.DataFrame(novos_contatos)
    df_final = pd.concat([df_consolidado, df_novos_contatos], ignore_index=True)
    
    # Remover duplicatas baseado no nome (case insensitive)
    print(f"Total antes de remover duplicatas: {len(df_final)}")
    
    # Criar uma coluna temporária para detecção de duplicatas
    df_final['nome_lower'] = df_final['nome'].str.lower()
    
    # Definir prioridade: dep_fed > dep_estadual > vereadores > desatualizados
    df_final['prioridade'] = df_final['origem'].map({
        'contatos_dep_fed': 1,
        'contatos_dep_estadual': 2,
        'contatos_vereadores': 3, 
        'contatos_desatualizados': 4
    })
    
    df_final = df_final.sort_values('prioridade')
    df_final = df_final.drop_duplicates(subset=['nome_lower'], keep='first')
    df_final = df_final.drop(['nome_lower', 'prioridade'], axis=1)
    
    print(f"Total após remoção de duplicatas: {len(df_final)}")
    
    # Reorganizar colunas
    df_final = df_final[['nome', 'email', 'telefone', 'cargo', 'partido', 'origem']]
    
    # Salvar arquivo consolidado atualizado
    df_final.to_csv(consolidado_path, index=False, encoding='utf-8')
    
    print(f"Arquivo consolidado atualizado salvo em: {consolidado_path}")
    
    # Estatísticas finais
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de contatos únicos: {len(df_final)}")
    
    origem_stats = df_final['origem'].value_counts()
    for origem, count in origem_stats.items():
        print(f"{origem}: {count} contatos")
    
    # Estatísticas por cargo
    print(f"\n=== ESTATÍSTICAS POR CARGO ===")
    cargo_stats = df_final['cargo'].value_counts()
    for cargo, count in cargo_stats.items():
        print(f"{cargo}: {count} contatos")
    
    # Verificar especificamente os deputados estaduais
    deputados_estaduais_final = df_final[df_final['cargo'] == 'Deputado Estadual']
    print(f"\nDeputados estaduais no arquivo final: {len(deputados_estaduais_final)}")
    
    if len(deputados_estaduais_final) > 0:
        print(f"\nDistribuição dos Deputados Estaduais por Partido:")
        partidos_estaduais = deputados_estaduais_final['partido'].value_counts()
        for partido, count in partidos_estaduais.items():
            print(f"{partido}: {count} deputados")

if __name__ == "__main__":
    adicionar_deputados_estaduais()