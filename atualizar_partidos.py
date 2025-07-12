#!/usr/bin/env python3
"""
Script para atualizar informações de partidos no arquivo de contatos
"""

import pandas as pd
import os

def atualizar_partidos():
    """Atualiza informações de partidos dos deputados federais"""
    
    # Ler o arquivo CSV
    file_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_geral.csv"
    df = pd.read_csv(file_path, encoding='utf-8')
    
    # Dicionário com as informações de partidos encontradas
    partidos_deputados = {
        'Altineu Côrtes': 'PL',
        'Áureo Ribeiro': 'Solidariedade', 
        'Eduardo Bandeira de Mello': 'PSB',
        'Bebeto': 'PP',  # Migrou do PTB para PP em 2023
        'Benedita da Silva': 'PT',
        'Caio Vianna': 'PSD',
        'Carlos Jordy': 'PL',
        'Chico Alencar': 'PSOL',
        'Chiquinho Brazão': 'Sem Partido',  # Estava sem partido quando preso
        'Chris Tonietto': 'PL',
        'Dani Cunha': 'União Brasil',
        'Daniela do Waguinho': 'União Brasil'
    }
    
    # Atualizar os partidos
    for nome, partido in partidos_deputados.items():
        # Buscar por nome exato ou similar
        mask = df['nome'].str.contains(nome, case=False, na=False)
        if mask.any():
            df.loc[mask, 'partido'] = partido
            print(f"Atualizado: {nome} -> {partido}")
        else:
            print(f"Não encontrado: {nome}")
    
    # Salvar o arquivo atualizado
    df.to_csv(file_path, index=False, encoding='utf-8')
    
    print(f"\nArquivo atualizado salvo em: {file_path}")
    
    # Estatísticas
    deputados_com_partido = df[(df['cargo'] == 'Deputado Federal') & (df['partido'] != '')].shape[0]
    total_deputados = df[df['cargo'] == 'Deputado Federal'].shape[0]
    
    print(f"\nEstatísticas dos Deputados Federais:")
    print(f"Com partido definido: {deputados_com_partido}/{total_deputados}")
    print(f"Ainda sem partido: {total_deputados - deputados_com_partido}")
    
    # Mostrar deputados que ainda estão sem partido
    deputados_sem_partido = df[(df['cargo'] == 'Deputado Federal') & (df['partido'] == '')]
    if not deputados_sem_partido.empty:
        print("\nDeputados ainda sem informação de partido:")
        for nome in deputados_sem_partido['nome'].tolist():
            print(f"- {nome}")

if __name__ == "__main__":
    atualizar_partidos()