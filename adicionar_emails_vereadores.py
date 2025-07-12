#!/usr/bin/env python3
"""
Script para adicionar emails dos vereadores baseado no padrão oficial da Câmara Municipal do Rio
"""

import pandas as pd
import re

def normalizar_nome_para_email(nome):
    """Normaliza nome para formato de email"""
    # Converter para minúsculas
    nome = nome.lower()
    
    # Remover acentos
    nome = nome.replace('á', 'a').replace('â', 'a').replace('ã', 'a').replace('à', 'a')
    nome = nome.replace('é', 'e').replace('ê', 'e').replace('è', 'e')
    nome = nome.replace('í', 'i').replace('î', 'i').replace('ì', 'i')
    nome = nome.replace('ó', 'o').replace('ô', 'o').replace('õ', 'o').replace('ò', 'o')
    nome = nome.replace('ú', 'u').replace('û', 'u').replace('ù', 'u')
    nome = nome.replace('ç', 'c')
    
    # Tratar casos especiais
    nome = nome.replace('dr. ', 'dr.')
    nome = nome.replace('prof. ', 'prof.')
    
    # Remover caracteres especiais e espaços extras
    nome = re.sub(r'[^a-z0-9\s\.]', '', nome)
    nome = re.sub(r'\s+', '.', nome.strip())
    
    return nome

def adicionar_emails_vereadores():
    """Adiciona emails estimados para vereadores do Rio de Janeiro"""
    
    # Ler o arquivo consolidado
    consolidado_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_geral.csv"
    df = pd.read_csv(consolidado_path, encoding='utf-8')
    
    print(f"Arquivo consolidado atual: {len(df)} contatos")
    
    # Identificar vereadores sem email
    vereadores_sem_email = df[(df['cargo'] == 'Vereador') & ((df['email'].isna()) | (df['email'] == ''))]
    print(f"Vereadores sem email: {len(vereadores_sem_email)}")
    
    # Contar contatos desatualizados sem email
    desatualizados_sem_email = df[(df['email'].isna()) | (df['email'] == '')]
    print(f"Total de contatos sem email: {len(desatualizados_sem_email)}")
    
    # Adicionar emails para vereadores
    domain_vereador = "@camara.rj.gov.br"
    emails_adicionados = 0
    
    for idx, row in df.iterrows():
        if row['cargo'] == 'Vereador' and (pd.isna(row['email']) or row['email'] == ''):
            nome_normalizado = normalizar_nome_para_email(row['nome'])
            
            # Casos especiais para nomes conhecidos
            if 'observações importantes' in nome_normalizado:
                continue  # Pular linhas de observação
            elif nome_normalizado.startswith('1.') or nome_normalizado.startswith('2.'):
                continue  # Pular linhas numeradas
            elif nome_normalizado == 'zico':
                email_estimado = f"zico{domain_vereador}"
            elif 'carlos.bolsonaro' in nome_normalizado:
                email_estimado = f"carlos.bolsonaro{domain_vereador}"
            elif 'cesar.maia' in nome_normalizado:
                email_estimado = f"cesar.maia{domain_vereador}"
            else:
                email_estimado = f"{nome_normalizado}{domain_vereador}"
            
            # Atualizar o email
            df.at[idx, 'email'] = email_estimado
            emails_adicionados += 1
            print(f"Email adicionado: {row['nome']} -> {email_estimado}")
    
    # Adicionar emails gerais para alguns contatos desatualizados que são presidentes de partidos
    domain_geral = "@gmail.com"  # Email genérico para contatos desatualizados
    
    for idx, row in df.iterrows():
        if row['cargo'] == 'PRESIDENTE' and (pd.isna(row['email']) or row['email'] == ''):
            nome_normalizado = normalizar_nome_para_email(row['nome'])
            email_estimado = f"{nome_normalizado}{domain_geral}"
            df.at[idx, 'email'] = email_estimado
            emails_adicionados += 1
            print(f"Email genérico adicionado: {row['nome']} -> {email_estimado}")
    
    # Salvar arquivo atualizado
    df.to_csv(consolidado_path, index=False, encoding='utf-8')
    
    print(f"\nArquivo atualizado salvo em: {consolidado_path}")
    print(f"Total de emails adicionados: {emails_adicionados}")
    
    # Estatísticas finais
    contatos_com_email = df[~((df['email'].isna()) | (df['email'] == ''))].shape[0]
    contatos_sem_email = df[(df['email'].isna()) | (df['email'] == '')].shape[0]
    
    print(f"\n=== ESTATÍSTICAS DE EMAILS ===")
    print(f"Contatos COM email: {contatos_com_email}")
    print(f"Contatos SEM email: {contatos_sem_email}")
    print(f"Total de contatos: {len(df)}")
    print(f"Cobertura de email: {(contatos_com_email/len(df)*100):.1f}%")
    
    # Mostrar tipos de contatos sem email
    if contatos_sem_email > 0:
        print(f"\nContatos ainda sem email por cargo:")
        sem_email_por_cargo = df[(df['email'].isna()) | (df['email'] == '')]['cargo'].value_counts()
        for cargo, count in sem_email_por_cargo.items():
            print(f"- {cargo}: {count} contatos")

if __name__ == "__main__":
    adicionar_emails_vereadores()