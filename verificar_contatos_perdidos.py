#!/usr/bin/env python3
"""
Script para verificar quais contatos foram perdidos na consolidação
"""

import pandas as pd
import os

def verificar_contatos_perdidos():
    """Verifica quais contatos foram perdidos na consolidação"""
    
    # Ler o arquivo original de desatualizados
    original_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_desatualizados.csv"
    df_original = pd.read_csv(original_path, encoding='utf-8')
    
    print(f"Arquivo original contatos_desatualizados.csv: {len(df_original)} registros")
    
    # Ler o arquivo consolidado
    consolidado_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_geral.csv"
    df_consolidado = pd.read_csv(consolidado_path, encoding='utf-8')
    
    # Filtrar apenas contatos desatualizados
    df_desatualizados_consolidado = df_consolidado[df_consolidado['origem'] == 'contatos_desatualizados']
    print(f"Contatos desatualizados no arquivo consolidado: {len(df_desatualizados_consolidado)}")
    
    # Mostrar os primeiros registros do arquivo original para entender a estrutura
    print("\n=== PRIMEIROS 10 REGISTROS DO ARQUIVO ORIGINAL ===")
    for i, row in df_original.head(10).iterrows():
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
            
        telefone = ''
        for j in range(1, 5):
            phone_col = f'Phone {j} - Value'
            if phone_col in row and pd.notna(row[phone_col]):
                telefone = str(row[phone_col]).strip()
                if ':::' in telefone:
                    telefone = telefone.split(':::')[0].strip()
                break
        
        print(f"Registro {i+1}: Nome='{nome}', Telefone='{telefone}', Org='{row.get('Organization Name', '')}', Título='{row.get('Organization Title', '')}'")
    
    # Processar todos os registros como fazia o script original
    contacts_processados = []
    contacts_rejeitados = []
    
    for _, row in df_original.iterrows():
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
                telefone = str(row[phone_col]).strip()
                if ':::' in telefone:
                    telefone = telefone.split(':::')[0].strip()
                break
        
        if nome and nome != '':
            contacts_processados.append({
                'nome': nome,
                'telefone': telefone,
                'cargo': str(row.get('Organization Title', '')),
                'linha_original': _ + 2  # +2 porque DataFrame começa em 0 e arquivo tem cabeçalho
            })
        else:
            contacts_rejeitados.append({
                'linha_original': _ + 2,
                'first_name': row.get('First Name', ''),
                'middle_name': row.get('Middle Name', ''),
                'last_name': row.get('Last Name', ''),
                'organization_name': row.get('Organization Name', ''),
                'telefone': telefone
            })
    
    print(f"\n=== RESULTADO DO PROCESSAMENTO ===")
    print(f"Contatos processados com sucesso: {len(contacts_processados)}")
    print(f"Contatos rejeitados (sem nome): {len(contacts_rejeitados)}")
    
    if contacts_rejeitados:
        print(f"\n=== CONTATOS REJEITADOS ===")
        for rejected in contacts_rejeitados:
            print(f"Linha {rejected['linha_original']}: FirstName='{rejected['first_name']}', "
                  f"MiddleName='{rejected['middle_name']}', LastName='{rejected['last_name']}', "
                  f"OrgName='{rejected['organization_name']}', Tel='{rejected['telefone']}'")

if __name__ == "__main__":
    verificar_contatos_perdidos()