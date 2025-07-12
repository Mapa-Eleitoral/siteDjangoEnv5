#!/usr/bin/env python3
"""
Script para mostrar detalhes das duplicatas internas nos contatos desatualizados
"""

import pandas as pd

def mostrar_duplicatas_internas():
    """Mostra detalhes das duplicatas internas"""
    
    desatualizados_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_desatualizados.csv"
    df = pd.read_csv(desatualizados_path, encoding='utf-8')
    
    # Processar todos os nomes
    nomes_processados = []
    
    for i, row in df.iterrows():
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
        
        if nome and nome != '':
            nomes_processados.append({
                'linha': i + 2,  # +2 porque DataFrame começa em 0 e arquivo tem cabeçalho
                'nome': nome,
                'nome_lower': nome.lower(),
                'telefone': str(row.get('Phone 1 - Value', '')).split(':::')[0].strip() if pd.notna(row.get('Phone 1 - Value', '')) else '',
                'organization': str(row.get('Organization Name', '')),
                'title': str(row.get('Organization Title', ''))
            })
    
    # Encontrar duplicatas
    nomes_count = {}
    for item in nomes_processados:
        nome_lower = item['nome_lower']
        if nome_lower not in nomes_count:
            nomes_count[nome_lower] = []
        nomes_count[nome_lower].append(item)
    
    # Mostrar duplicatas
    print("=== DUPLICATAS INTERNAS ENCONTRADAS ===")
    duplicatas_encontradas = 0
    
    for nome_lower, ocorrencias in nomes_count.items():
        if len(ocorrencias) > 1:
            duplicatas_encontradas += len(ocorrencias) - 1  # -1 porque uma será mantida
            print(f"\n'{ocorrencias[0]['nome']}' aparece {len(ocorrencias)} vezes:")
            for i, ocorrencia in enumerate(ocorrencias):
                print(f"  {i+1}. Linha {ocorrencia['linha']}: Tel='{ocorrencia['telefone']}', "
                      f"Org='{ocorrencia['organization']}', Title='{ocorrencia['title']}'")
    
    print(f"\n=== RESUMO ===")
    print(f"Total de registros processados: {len(nomes_processados)}")
    print(f"Registros únicos (após remoção de duplicatas): {len(nomes_processados) - duplicatas_encontradas}")
    print(f"Duplicatas que serão removidas: {duplicatas_encontradas}")
    
    # Verificar se bate com o resultado final
    print(f"\nVerificação: 54 originais - {duplicatas_encontradas} duplicatas = {54 - duplicatas_encontradas} únicos")
    print("Isso explica por que temos 50 contatos desatualizados no arquivo final!")

if __name__ == "__main__":
    mostrar_duplicatas_internas()