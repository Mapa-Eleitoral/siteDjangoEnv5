#!/usr/bin/env python3
"""
Script para encontrar quais contatos desatualizados estão sendo removidos como duplicatas
"""

import pandas as pd
import os

def clean_phone(phone_str):
    """Limpa e formata telefone"""
    if pd.isna(phone_str) or not phone_str:
        return ""
    
    phone = str(phone_str).strip()
    if ':::' in phone:
        phone = phone.split(':::')[0].strip()
    
    return phone

def encontrar_duplicatas():
    """Encontra duplicatas entre arquivos"""
    
    # Ler arquivos originais
    dep_fed_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_dep_fed.csv"
    vereadores_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_vereadores.csv"
    desatualizados_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_desatualizados.csv"
    
    # Processar deputados federais
    dep_federal_nomes = set()
    with open(dep_fed_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[2:]:  # Pular cabeçalho
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    nome = parts[1].strip()
                    if nome and nome != '':
                        dep_federal_nomes.add(nome.lower())
    
    # Processar vereadores
    vereadores_nomes = set()
    df_vereadores = pd.read_csv(vereadores_path, encoding='utf-8')
    for _, row in df_vereadores.iterrows():
        nome = str(row.get('Nome', '')).strip()
        if nome and nome != '':
            vereadores_nomes.add(nome.lower())
    
    # Processar desatualizados
    df_desatualizados = pd.read_csv(desatualizados_path, encoding='utf-8')
    desatualizados_processados = []
    
    print("=== PROCESSANDO CONTATOS DESATUALIZADOS ===")
    
    for i, row in df_desatualizados.iterrows():
        # Combinar first name, middle name, last name
        nome_parts = []
        if pd.notna(row.get('First Name', '')) and str(row['First Name']).strip():
            nome_parts.append(str(row['First Name']).strip())
        if pd.notna(row.get('Middle Name', '')) and str(row['Middle Name']).strip():
            nome_parts.append(str(row['Middle Name']).strip())
        if pd.notna(row.get('Last Name', '')) and str(row['Last Name']).strip():
            nome_parts.append(str(row['Last Name']).strip())
        
        nome = ' '.join(nome_parts).strip()
        
        # Se não há nome nos campos padrão, usar o campo personalizado
        if not nome and pd.notna(row.get('Organization Name', '')):
            nome = str(row['Organization Name']).strip()
        
        # Pegar primeiro telefone disponível
        telefone = ''
        for j in range(1, 5):
            phone_col = f'Phone {j} - Value'
            if phone_col in row and pd.notna(row[phone_col]):
                telefone = clean_phone(row[phone_col])
                break
        
        if nome and nome != '':
            linha_original = i + 2  # +2 porque DataFrame começa em 0 e arquivo tem cabeçalho
            nome_lower = nome.lower()
            
            # Verificar se é duplicata
            eh_duplicata_dep = nome_lower in dep_federal_nomes
            eh_duplicata_ver = nome_lower in vereadores_nomes
            
            info = {
                'linha': linha_original,
                'nome': nome,
                'nome_lower': nome_lower,
                'telefone': telefone,
                'duplicata_dep': eh_duplicata_dep,
                'duplicata_ver': eh_duplicata_ver,
                'sera_removido': eh_duplicata_dep or eh_duplicata_ver
            }
            
            desatualizados_processados.append(info)
            
            if info['sera_removido']:
                print(f"DUPLICATA ENCONTRADA - Linha {linha_original}: '{nome}' "
                      f"(Dep: {eh_duplicata_dep}, Ver: {eh_duplicata_ver})")
    
    print(f"\n=== RESUMO ===")
    print(f"Total de contatos desatualizados processados: {len(desatualizados_processados)}")
    
    duplicatas = [c for c in desatualizados_processados if c['sera_removido']]
    nao_duplicatas = [c for c in desatualizados_processados if not c['sera_removido']]
    
    print(f"Serão removidos como duplicatas: {len(duplicatas)}")
    print(f"Permanecerão no arquivo final: {len(nao_duplicatas)}")
    
    if duplicatas:
        print(f"\n=== CONTATOS QUE SERÃO REMOVIDOS ===")
        for dup in duplicatas:
            print(f"- {dup['nome']} (linha {dup['linha']})")
    
    # Verificar se algum nome aparece múltiplas vezes nos desatualizados
    nomes_desatualizados = [c['nome_lower'] for c in desatualizados_processados]
    duplicatas_internas = {}
    for nome in nomes_desatualizados:
        count = nomes_desatualizados.count(nome)
        if count > 1:
            duplicatas_internas[nome] = count
    
    if duplicatas_internas:
        print(f"\n=== DUPLICATAS INTERNAS NOS DESATUALIZADOS ===")
        for nome, count in duplicatas_internas.items():
            print(f"- {nome}: aparece {count} vezes")

if __name__ == "__main__":
    encontrar_duplicatas()