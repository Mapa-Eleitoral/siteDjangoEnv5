#!/usr/bin/env python3
"""
Script para criar três arquivos CSV separados por cargo político:
1. vereadores.csv
2. d_federais.csv  
3. d_estaduais.csv
"""

import pandas as pd
import re
from pathlib import Path

def extrair_email_markdown(email_str):
    """Extrai email do formato markdown"""
    if pd.isna(email_str) or not email_str:
        return ""
    
    # Formato: [texto](mailto:email) -> extrai email
    if '[' in email_str and 'mailto:' in email_str:
        start = email_str.find('mailto:') + 7
        end = email_str.find(')', start)
        if start > 6 and end > start:
            return email_str[start:end]
    
    return str(email_str).strip()

def processar_deputados_federais():
    """Processa deputados federais do arquivo markdown"""
    print("🏛️ Processando Deputados Federais...")
    
    file_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_dep_fed.csv"
    deputados_federais = []
    
    # Ler como texto para processar markdown
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines[2:]:  # Pular cabeçalho markdown
        if '|' in line and 'Nome' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                nome = parts[1].strip()
                email = extrair_email_markdown(parts[2])
                telefone = parts[3].strip()
                
                if nome and nome != '':
                    deputados_federais.append({
                        'nome': nome,
                        'email': email,
                        'telefone': telefone,
                        'cargo': 'Deputado Federal',
                        'uf': 'RJ',
                        'partido': '',  # Será preenchido depois com dados do consolidado
                        'gabinete': '',
                        'instagram': '',
                        'twitter': '',
                        'facebook': '',
                        'observacoes': ''
                    })
    
    print(f"✅ {len(deputados_federais)} deputados federais processados")
    return deputados_federais

def processar_vereadores():
    """Processa vereadores do arquivo CSV estruturado"""
    print("🏛️ Processando Vereadores...")
    
    file_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_vereadores.csv"
    df = pd.read_csv(file_path, encoding='utf-8')
    
    vereadores = []
    for _, row in df.iterrows():
        nome = str(row.get('Nome', '')).strip()
        if nome and nome != '' and 'Observações' not in nome:
            
            # Criar email estimado se não tiver
            email = str(row.get('Email', '')).strip()
            if not email or email == 'nan':
                nome_email = nome.lower().replace(' ', '.').replace('dr. ', 'dr.')
                nome_email = re.sub(r'[áàâã]', 'a', nome_email)
                nome_email = re.sub(r'[éèê]', 'e', nome_email)
                nome_email = re.sub(r'[íìî]', 'i', nome_email)
                nome_email = re.sub(r'[óòôõ]', 'o', nome_email)
                nome_email = re.sub(r'[úùû]', 'u', nome_email)
                nome_email = re.sub(r'[ç]', 'c', nome_email)
                email = f"{nome_email}@camara.rj.gov.br"
            
            vereadores.append({
                'nome': nome,
                'email': email,
                'telefone': str(row.get('Telefone', '(21) 3814-2121')),
                'cargo': 'Vereador',
                'uf': 'RJ',
                'municipio': 'Rio de Janeiro',
                'partido': str(row.get('Partido', '')),
                'votos': str(row.get('Votos', '')),
                'gabinete': str(row.get('Gabinete', '')),
                'instagram': str(row.get('Instagram', '')),
                'twitter': str(row.get('Twitter', '')),
                'facebook': str(row.get('Facebook', '')),
                'observacoes': str(row.get('Observações', ''))
            })
    
    print(f"✅ {len(vereadores)} vereadores processados")
    return vereadores

def buscar_deputados_estaduais_consolidado():
    """Busca deputados estaduais do arquivo consolidado se existir"""
    print("🏛️ Buscando Deputados Estaduais no arquivo consolidado...")
    
    consolidado_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_geral.csv"
    deputados_estaduais = []
    
    try:
        df = pd.read_csv(consolidado_path, encoding='utf-8')
        
        # Filtrar deputados estaduais
        mask_estaduais = df['cargo'] == 'Deputado Estadual'
        df_estaduais = df[mask_estaduais]
        
        for _, row in df_estaduais.iterrows():
            deputados_estaduais.append({
                'nome': str(row.get('nome', '')),
                'email': str(row.get('email', '')),
                'telefone': str(row.get('telefone', '(21) 2588-1000')),
                'cargo': 'Deputado Estadual',
                'uf': 'RJ',
                'partido': str(row.get('partido', '')),
                'gabinete': '',
                'instagram': '',
                'twitter': '',
                'facebook': '',
                'observacoes': ''
            })
        
        print(f"✅ {len(deputados_estaduais)} deputados estaduais encontrados")
        
    except FileNotFoundError:
        print("⚠️ Arquivo consolidado não encontrado, criando deputados estaduais básicos...")
        
        # Lista básica dos deputados estaduais conhecidos
        nomes_estaduais = [
            'Márcio Canella', 'Douglas Ruas', 'Renata Souza', 'Dr. Serginho',
            'Dani Monteiro', 'Mônica Francisco', 'Flavio Serafini', 'Carlos Minc',
            'Rodrigo Amorim', 'Alexandre Freitas', 'Danniel Librelon'
        ]
        
        for nome in nomes_estaduais:
            nome_email = nome.lower().replace(' ', '.').replace('dr. ', 'dr.')
            deputados_estaduais.append({
                'nome': nome,
                'email': f"dep.{nome_email}@alerj.rj.gov.br",
                'telefone': '(21) 2588-1000',
                'cargo': 'Deputado Estadual',
                'uf': 'RJ',
                'partido': '',
                'gabinete': '',
                'instagram': '',
                'twitter': '',
                'facebook': '',
                'observacoes': ''
            })
    
    return deputados_estaduais

def completar_dados_partidos():
    """Completa dados de partidos baseado no conhecimento consolidado"""
    partidos_conhecidos = {
        # Deputados Federais
        'Altineu Côrtes': 'PL', 'Áureo Ribeiro': 'Solidariedade', 'Eduardo Bandeira de Mello': 'PSB',
        'Bebeto': 'PP', 'Benedita da Silva': 'PT', 'Carlos Jordy': 'PL', 'Chico Alencar': 'PSOL',
        'Delegado Ramagem': 'PL', 'General Pazuello': 'PL', 'Talíria Petrone': 'PSOL',
        
        # Deputados Estaduais  
        'Márcio Canella': 'União Brasil', 'Douglas Ruas': 'PL', 'Renata Souza': 'PSOL',
        'Dr. Serginho': 'PL', 'Dani Monteiro': 'PSOL', 'Mônica Francisco': 'PSOL',
        'Carlos Minc': 'PSB', 'Rodrigo Amorim': 'PL', 'Alexandre Freitas': 'PL'
    }
    
    return partidos_conhecidos

def criar_arquivos_finais():
    """Cria os três arquivos CSV finais"""
    print("\n🚀 Iniciando criação dos arquivos por cargo...")
    
    # Processar cada categoria
    deputados_federais = processar_deputados_federais()
    vereadores = processar_vereadores() 
    deputados_estaduais = buscar_deputados_estaduais_consolidado()
    
    # Completar dados de partidos
    partidos_conhecidos = completar_dados_partidos()
    
    # Atualizar partidos para deputados federais
    for dep in deputados_federais:
        if dep['nome'] in partidos_conhecidos:
            dep['partido'] = partidos_conhecidos[dep['nome']]
    
    # Atualizar partidos para deputados estaduais
    for dep in deputados_estaduais:
        if dep['nome'] in partidos_conhecidos:
            dep['partido'] = partidos_conhecidos[dep['nome']]
    
    # Criar DataFrames
    df_federais = pd.DataFrame(deputados_federais)
    df_vereadores = pd.DataFrame(vereadores)
    df_estaduais = pd.DataFrame(deputados_estaduais)
    
    # Ordenar por nome
    df_federais = df_federais.sort_values('nome')
    df_vereadores = df_vereadores.sort_values('nome') 
    df_estaduais = df_estaduais.sort_values('nome')
    
    # Salvar arquivos
    base_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/"
    
    df_federais.to_csv(f"{base_path}d_federais.csv", index=False, encoding='utf-8')
    df_vereadores.to_csv(f"{base_path}vereadores.csv", index=False, encoding='utf-8')
    df_estaduais.to_csv(f"{base_path}d_estaduais.csv", index=False, encoding='utf-8')
    
    print(f"\n📁 Arquivos criados:")
    print(f"├── d_federais.csv: {len(df_federais)} registros")
    print(f"├── vereadores.csv: {len(df_vereadores)} registros") 
    print(f"└── d_estaduais.csv: {len(df_estaduais)} registros")
    
    print(f"\n📊 Total de políticos catalogados: {len(df_federais) + len(df_vereadores) + len(df_estaduais)}")
    
    # Estatísticas por partido (apenas vereadores que têm dados completos)
    print(f"\n🎯 Distribuição partidária dos vereadores:")
    partidos_vereadores = df_vereadores['partido'].value_counts()
    for partido, count in partidos_vereadores.head(5).items():
        if partido and partido != 'nan':
            print(f"   {partido}: {count} vereadores")

if __name__ == "__main__":
    criar_arquivos_finais()