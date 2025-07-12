#!/usr/bin/env python3
"""
Script para reprocessar contatos desatualizados corretamente
"""

import pandas as pd
import os

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

def reprocessar_desatualizados():
    """Reprocessa arquivo de contatos desatualizados"""
    
    # Ler o arquivo original
    original_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_desatualizados.csv"
    df_original = pd.read_csv(original_path, encoding='utf-8')
    
    # Ler o arquivo consolidado atual
    consolidado_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_geral.csv"
    df_consolidado = pd.read_csv(consolidado_path, encoding='utf-8')
    
    # Remover todos os contatos desatualizados atuais
    df_sem_desatualizados = df_consolidado[df_consolidado['origem'] != 'contatos_desatualizados']
    
    print(f"Arquivo consolidado original: {len(df_consolidado)} contatos")
    print(f"Após remover desatualizados: {len(df_sem_desatualizados)} contatos")
    
    # Reprocessar todos os contatos desatualizados
    novos_contatos = []
    
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
                telefone = clean_phone(row[phone_col])
                break
        
        if nome and nome != '':
            novos_contatos.append({
                'nome': nome,
                'email': '',  # Não há campo de email claro neste arquivo
                'telefone': telefone,
                'cargo': str(row.get('Organization Title', '')),
                'partido': '',
                'origem': 'contatos_desatualizados'
            })
    
    print(f"Novos contatos desatualizados processados: {len(novos_contatos)}")
    
    # Adicionar os novos contatos ao DataFrame
    df_novos_contatos = pd.DataFrame(novos_contatos)
    df_final = pd.concat([df_sem_desatualizados, df_novos_contatos], ignore_index=True)
    
    # Remover duplicatas baseado no nome (case insensitive) - mas preservar os desatualizados originais
    print(f"Total antes de remover duplicatas: {len(df_final)}")
    
    # Criar uma coluna temporária para detecção de duplicatas
    df_final['nome_lower'] = df_final['nome'].str.lower()
    
    # Remover duplicatas mantendo o primeiro (prioridade para dep_fed, depois vereadores, depois desatualizados)
    df_final['prioridade'] = df_final['origem'].map({
        'contatos_dep_fed': 1,
        'contatos_vereadores': 2, 
        'contatos_desatualizados': 3
    })
    
    df_final = df_final.sort_values('prioridade')
    df_final = df_final.drop_duplicates(subset=['nome_lower'], keep='first')
    df_final = df_final.drop(['nome_lower', 'prioridade'], axis=1)
    
    print(f"Total após remoção de duplicatas: {len(df_final)}")
    
    # Reorganizar colunas
    df_final = df_final[['nome', 'email', 'telefone', 'cargo', 'partido', 'origem']]
    
    # Salvar arquivo consolidado corrigido
    df_final.to_csv(consolidado_path, index=False, encoding='utf-8')
    
    print(f"Arquivo consolidado corrigido salvo em: {consolidado_path}")
    
    # Estatísticas finais
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de contatos únicos: {len(df_final)}")
    
    origem_stats = df_final['origem'].value_counts()
    for origem, count in origem_stats.items():
        print(f"{origem}: {count} contatos")
    
    # Verificar especificamente os desatualizados
    desatualizados_final = df_final[df_final['origem'] == 'contatos_desatualizados']
    print(f"\nContatos desatualizados no arquivo final: {len(desatualizados_final)}")

if __name__ == "__main__":
    reprocessar_desatualizados()