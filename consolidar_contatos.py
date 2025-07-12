#!/usr/bin/env python3
"""
Script para consolidar três arquivos CSV de contatos em um só
"""

import pandas as pd
import os
from pathlib import Path

def clean_email(email_str):
    """Limpa e extrai email da string formatada"""
    if pd.isna(email_str) or not email_str:
        return ""
    
    # Remove formatação markdown se existir
    if '[' in email_str and ']' in email_str and '(' in email_str and ')' in email_str:
        # Formato: [texto](mailto:email) -> extrai email
        start = email_str.find('mailto:') + 7
        end = email_str.find(')', start)
        if start > 6 and end > start:
            return email_str[start:end]
    
    return str(email_str).strip()

def clean_phone(phone_str):
    """Limpa e formata telefone"""
    if pd.isna(phone_str) or not phone_str:
        return ""
    
    # Remove caracteres extras e mantém apenas números e formatação básica
    phone = str(phone_str).strip()
    # Remove texto extra após :::
    if ':::' in phone:
        phone = phone.split(':::')[0].strip()
    
    return phone

def process_dep_federal():
    """Processa arquivo de deputados federais"""
    file_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_dep_fed.csv"
    
    # O arquivo parece estar em formato markdown/pipe-separated
    # Vamos ler como texto e processar manualmente
    contacts = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines[2:]:  # Pular cabeçalho
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    nome = parts[1].strip()
                    email = clean_email(parts[2])
                    telefone = parts[3].strip()
                    
                    if nome and nome != '':
                        contacts.append({
                            'nome': nome,
                            'email': email,
                            'telefone': telefone,
                            'cargo': 'Deputado Federal',
                            'partido': '',
                            'origem': 'contatos_dep_fed'
                        })
    
    except Exception as e:
        print(f"Erro ao processar deputados federais: {e}")
        return []
    
    return contacts

def process_desatualizados():
    """Processa arquivo de contatos desatualizados"""
    file_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_desatualizados.csv"
    
    contacts = []
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        
        for _, row in df.iterrows():
            # Combinar first name, middle name, last name
            nome_parts = []
            if pd.notna(row.get('First Name', '')):
                nome_parts.append(str(row['First Name']))
            if pd.notna(row.get('Middle Name', '')):
                nome_parts.append(str(row['Middle Name']))
            if pd.notna(row.get('Last Name', '')):
                nome_parts.append(str(row['Last Name']))
            
            nome = ' '.join(nome_parts).strip()
            
            # Se não há nome nos campos padrão, usar o campo personalizado
            if not nome and pd.notna(row.get('Organization Name', '')):
                nome = str(row['Organization Name'])
            
            # Pegar primeiro telefone disponível
            telefone = ''
            for i in range(1, 5):
                phone_col = f'Phone {i} - Value'
                if phone_col in row and pd.notna(row[phone_col]):
                    telefone = clean_phone(row[phone_col])
                    break
            
            if nome and nome != '':
                contacts.append({
                    'nome': nome,
                    'email': '',  # Não há campo de email claro neste arquivo
                    'telefone': telefone,
                    'cargo': str(row.get('Organization Title', '')),
                    'partido': '',
                    'origem': 'contatos_desatualizados'
                })
    
    except Exception as e:
        print(f"Erro ao processar contatos desatualizados: {e}")
        return []
    
    return contacts

def process_vereadores():
    """Processa arquivo de vereadores"""
    file_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_vereadores.csv"
    
    contacts = []
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        
        for _, row in df.iterrows():
            nome = str(row.get('Nome', '')).strip()
            partido = str(row.get('Partido', '')).strip()
            telefone = str(row.get('Telefone', '')).strip()
            email = str(row.get('Email', '')).strip()
            
            if nome and nome != '':
                contacts.append({
                    'nome': nome,
                    'email': email,
                    'telefone': telefone,
                    'cargo': 'Vereador',
                    'partido': partido,
                    'origem': 'contatos_vereadores'
                })
    
    except Exception as e:
        print(f"Erro ao processar vereadores: {e}")
        return []
    
    return contacts

def main():
    """Função principal"""
    print("Iniciando consolidação de contatos...")
    
    # Processar cada arquivo
    dep_federal = process_dep_federal()
    desatualizados = process_desatualizados()
    vereadores = process_vereadores()
    
    print(f"Deputados Federais: {len(dep_federal)} contatos")
    print(f"Contatos Desatualizados: {len(desatualizados)} contatos")
    print(f"Vereadores: {len(vereadores)} contatos")
    
    # Consolidar todos os contatos
    all_contacts = dep_federal + desatualizados + vereadores
    
    print(f"Total de contatos: {len(all_contacts)}")
    
    if not all_contacts:
        print("Nenhum contato encontrado. Verificando caminhos dos arquivos...")
        return
    
    # Criar DataFrame
    df_final = pd.DataFrame(all_contacts)
    
    # Remover duplicatas baseado no nome (case insensitive)
    df_final['nome_lower'] = df_final['nome'].str.lower()
    df_final = df_final.drop_duplicates(subset=['nome_lower'], keep='first')
    df_final = df_final.drop('nome_lower', axis=1)
    
    print(f"Contatos após remoção de duplicatas: {len(df_final)}")
    
    # Reorganizar colunas
    df_final = df_final[['nome', 'email', 'telefone', 'cargo', 'partido', 'origem']]
    
    # Salvar arquivo consolidado
    output_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_geral.csv"
    df_final.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"Arquivo consolidado salvo em: {output_path}")
    
    # Estatísticas finais
    print("\n=== ESTATÍSTICAS ===")
    print(f"Total de contatos únicos: {len(df_final)}")
    print(f"Contatos com email: {df_final['email'].notna().sum()}")
    print(f"Contatos com telefone: {df_final['telefone'].notna().sum()}")
    print("\nDistribuição por origem:")
    print(df_final['origem'].value_counts())
    print("\nDistribuição por cargo:")
    print(df_final['cargo'].value_counts())

if __name__ == "__main__":
    main()