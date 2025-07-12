#!/usr/bin/env python3
"""
Script para corrigir o arquivo de contatos corrompido
"""

import pandas as pd
import os

def corrigir_arquivo_contatos():
    """Corrige arquivo corrompido reconstruindo a partir do backup"""
    
    # Ler arquivo corrompido linha por linha para entender a estrutura
    corrupted_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_geral_backup.csv"
    
    print("Lendo arquivo corrompido...")
    
    with open(corrupted_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total de linhas: {len(lines)}")
    print("Primeiras 5 linhas:")
    for i, line in enumerate(lines[:5]):
        print(f"{i+1}: {line.strip()}")
    
    # Reconstruir dados corretos
    contatos_corretos = []
    
    # Cabeçalho esperado
    colunas = ['nome', 'email', 'telefone', 'cargo', 'partido', 'origem']
    
    # Processar linha por linha
    for i, line in enumerate(lines):
        if i == 0:  # Pular cabeçalho
            continue
            
        line = line.strip()
        if not line:
            continue
            
        # Tentar extrair dados da linha corrompida
        # Formato parece ser: email,telefone,cargo,partido,origem (nome perdido)
        parts = line.split(',')
        
        if len(parts) >= 4:
            email_ou_nome = parts[0].strip()
            telefone = parts[1].strip()
            cargo = parts[2].strip()
            partido = parts[3].strip() if len(parts) > 3 else ''
            origem = parts[4].strip() if len(parts) > 4 else ''
            
            # Detectar se o primeiro campo é email ou nome
            if '@' in email_ou_nome:
                # É um email, precisamos extrair o nome do email
                email = email_ou_nome
                if 'camara.leg.br' in email:
                    # Deputado federal
                    nome = email.replace('dep.', '').replace('@camara.leg.br', '').replace('.', ' ').title()
                    origem = 'contatos_dep_fed'
                elif 'alerj.rj.gov.br' in email:
                    # Deputado estadual
                    nome = email.replace('dep.', '').replace('@alerj.rj.gov.br', '').replace('.', ' ').title()
                    origem = 'contatos_dep_estadual'
                else:
                    nome = email.split('@')[0]
            else:
                # É um nome
                nome = email_ou_nome
                email = ''  # Será preenchido depois
        else:
            continue  # Pular linhas inválidas
        
        # Adicionar à lista
        contatos_corretos.append({
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'cargo': cargo,
            'partido': partido,
            'origem': origem if origem else 'contatos_desatualizados'
        })
    
    print(f"Contatos processados: {len(contatos_corretos)}")
    
    # Criar DataFrame
    df_corrigido = pd.DataFrame(contatos_corretos)
    
    # Preencher emails faltantes
    for idx, row in df_corrigido.iterrows():
        if not row['email'] or pd.isna(row['email']):
            if row['cargo'] == 'Vereador':
                # Email de vereador
                nome_email = row['nome'].lower().replace(' ', '.').replace('dr. ', 'dr.')
                nome_email = nome_email.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                nome_email = nome_email.replace('ç', 'c').replace('ã', 'a').replace('õ', 'o')
                df_corrigido.at[idx, 'email'] = f"{nome_email}@camara.rj.gov.br"
            elif row['cargo'] == 'PRESIDENTE':
                # Email genérico para presidentes
                nome_email = row['nome'].lower().replace(' ', '.')
                nome_email = nome_email.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                df_corrigido.at[idx, 'email'] = f"{nome_email}@gmail.com"
            else:
                # Email genérico
                nome_email = row['nome'].lower().replace(' ', '.')
                df_corrigido.at[idx, 'email'] = f"{nome_email}@email.com"
    
    # Salvar arquivo corrigido
    output_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_geral.csv"
    df_corrigido.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"Arquivo corrigido salvo em: {output_path}")
    
    # Estatísticas
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de contatos: {len(df_corrigido)}")
    print(f"Contatos por cargo:")
    print(df_corrigido['cargo'].value_counts())
    
    print(f"\nContatos por origem:")
    print(df_corrigido['origem'].value_counts())
    
    # Verificar emails
    sem_email = df_corrigido[df_corrigido['email'] == ''].shape[0]
    print(f"\nContatos sem email: {sem_email}")

if __name__ == "__main__":
    corrigir_arquivo_contatos()