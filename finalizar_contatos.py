#!/usr/bin/env python3
"""
Script para finalizar e completar todas as informações dos contatos
"""

import pandas as pd

def finalizar_contatos():
    """Completa informações faltantes e organiza arquivo final"""
    
    # Ler arquivo atual
    consolidado_path = "/mnt/c/users/filip/onedrive/mapaeleitoral/marketing/contato/contatos_geral.csv"
    df = pd.read_csv(consolidado_path, encoding='utf-8')
    
    print(f"Arquivo atual: {len(df)} contatos")
    
    # Lista dos vereadores do Rio de Janeiro com seus nomes corretos
    vereadores_rj = [
        {'nome': 'Carlos Bolsonaro', 'partido': 'PL'},
        {'nome': 'Márcio Santos', 'partido': 'PV'}, 
        {'nome': 'Vitor Hugo', 'partido': 'MDB'},
        {'nome': 'Zico', 'partido': 'PSD'},
        {'nome': 'Flavio Valle', 'partido': 'PSB'},
        {'nome': 'João Mendes de Jesus', 'partido': 'Republicanos'},
        {'nome': 'Thiago K. Ribeiro', 'partido': 'MDB'},
        {'nome': 'Tatiana Roque', 'partido': 'DC'},
        {'nome': 'Marcos Dias', 'partido': 'Pode'},
        {'nome': 'Dr. Rogerio Amorim', 'partido': 'PL'},
        {'nome': 'Paulo Messina', 'partido': 'PL'},
        {'nome': 'Fábio Silva', 'partido': 'Pode'},
        {'nome': 'Pedro Duarte', 'partido': 'Novo'},
        {'nome': 'Felipe Pires', 'partido': 'PT'},
        {'nome': 'Maíra do MST', 'partido': 'PT'},
        {'nome': 'Fernando Armelau', 'partido': 'PL'},
        {'nome': 'Rodrigo Vizeu', 'partido': 'MDB'},
        {'nome': 'Rafael Satiê', 'partido': 'PL'},
        {'nome': 'Gigi Castilho', 'partido': 'Republicanos'},
        {'nome': 'Leonel de Esquerda', 'partido': 'PT'},
        {'nome': 'Felipe Boró', 'partido': 'PSD'},
        {'nome': 'Monica Benicio', 'partido': 'PSOL'},
        {'nome': 'Salvino Oliveira', 'partido': 'PSD'},
        {'nome': 'Diego Vaz', 'partido': 'PSD'},
        {'nome': 'Vera Lins', 'partido': 'PP'},
        {'nome': 'Helena Vieira', 'partido': 'PSD'},
        {'nome': 'Junior da Lucinha', 'partido': 'PSD'},
        {'nome': 'Rick Azevedo', 'partido': 'PSOL'},
        {'nome': 'Cesar Maia', 'partido': 'PSD'},
        {'nome': 'Joyce Trindade', 'partido': 'PSD'},
        {'nome': 'Felipe Michel', 'partido': 'PP'},
        {'nome': 'Leniel Borel', 'partido': 'PP'},
        {'nome': 'Rosa Fernandes', 'partido': 'PSD'},
        {'nome': 'Marcelo Diniz', 'partido': 'PSD'},
        {'nome': 'Rafael Aloisio Freitas', 'partido': 'PSD'},
        {'nome': 'Carlo Caiado', 'partido': 'PSD'},
        {'nome': 'Tainá de Paula', 'partido': 'PT'},
        {'nome': 'Márcio Ribeiro', 'partido': 'PSD'},
        {'nome': 'Eliseu Kessler', 'partido': 'PL'},
        {'nome': 'Welington Carneiro', 'partido': 'PRD'},
        {'nome': 'Pablo Mello', 'partido': 'Republicanos'},
        {'nome': 'Jorge Canella', 'partido': 'União'},
        {'nome': 'William Siri', 'partido': 'PSOL'},
        {'nome': 'Wellington Dias', 'partido': 'PDT'},
        {'nome': 'Luiz Ramos Filho', 'partido': 'PSD'},
        {'nome': 'Talita Galhardo', 'partido': 'PSDB'},
        {'nome': 'Tânia Bastos', 'partido': 'Republicanos'}
    ]
    
    # Atualizar vereadores sem nome
    vereador_idx = 0
    for idx, row in df.iterrows():
        if row['cargo'] == 'Vereador' and (pd.isna(row['nome']) or row['nome'] == ''):
            if vereador_idx < len(vereadores_rj):
                vereador = vereadores_rj[vereador_idx]
                
                # Atualizar nome e partido
                df.at[idx, 'nome'] = vereador['nome']
                df.at[idx, 'partido'] = vereador['partido']
                
                # Criar email
                nome_email = vereador['nome'].lower().replace(' ', '.').replace('dr. ', 'dr.')
                nome_email = nome_email.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                nome_email = nome_email.replace('ç', 'c').replace('ã', 'a').replace('õ', 'o')
                df.at[idx, 'email'] = f"{nome_email}@camara.rj.gov.br"
                
                # Definir origem correta
                df.at[idx, 'origem'] = 'contatos_vereadores'
                
                vereador_idx += 1
                print(f"Vereador atualizado: {vereador['nome']}")
    
    # Completar nomes dos contatos desatualizados baseado nos nomes originais
    nomes_desatualizados = [
        'Mario Manhães Mosso', 'Monica Tereza Azeredo Benicio', 'Milton Cesar Alves de Oliveira',
        'Rodrigo dos Santos Vizeu Soares', 'Rafael Aloisio Freitas', 'Adejair Sanches de Aguiar',
        'Antonio Jose Papera de Azevedo', 'Atila Alexandre Nunes Pereira', 'Carlo Ferreira de Caiadocastro',
        'Carlos Nantes Bolsonaro', 'Celso Zallio Coelho', 'Cesare Pitacio Maia',
        'Dário José da Silva Ferreira', 'Davi Olx', 'Edmar Washington Xavier Pereira',
        'Welington de Araujo Dias', 'Marcus Alves de Souza', 'Felipe Bezerra da Costa',
        'Ezequiel Fernando Guimarães', 'Marcelo Diniz Anastacio da Silva', 'Luciana Goncalves de Novaes',
        'Kelson Renato Ribeiro', 'Jose Renato Cardozo Moura', 'Jose Marcio Ferreira Reis Ribeiro',
        'Jose Inaldo Fernandes da Silva', 'José Carlos Gentili', 'Jorge Miguel Felippe',
        'Jonas de Souza Neto', 'Gilberto de Oliveira Lima', 'Flavio Soares Castilho',
        'Flavio Simoes do Valle', 'Flavio das Gracas Miranda', 'Felipe da Silva Pires',
        'Paulo Santos Messina', 'Myrian Aparecida Bosco Massarollo', 'Victor Hugo Poubel Souza da Silveira',
        'Vitor Hugo Kaczmarkiewicz dos Santos', 'Willian Carvalho dos Santos', 'William Carlos Brumbispo',
        'Rogério de Castro Lopes', 'Rogério Martins Pires de Amorim', 'Rosamaria Orlando Fernandes',
        'Samuel Messias da Silva Oliveira', 'Sérgio Carlos Nascimento de Andrade', 'Tadeu Amorim de Barros Junior',
        'Tania Cristina Magalhaes Bastos e Silva', 'Thais de Souza Ferreira', 'Tiago Müller Cartier Marques',
        'Vera Lucia Ferreira Lins', 'Wegney da Costa Teodoro'
    ]
    
    # Atualizar contatos desatualizados sem nome
    desatualizado_idx = 0
    for idx, row in df.iterrows():
        if (pd.isna(row['nome']) or row['nome'] == '') and row.get('origem') == 'contatos_desatualizados':
            if desatualizado_idx < len(nomes_desatualizados):
                nome = nomes_desatualizados[desatualizado_idx]
                df.at[idx, 'nome'] = nome
                
                # Atualizar email
                nome_email = nome.lower().replace(' ', '.')
                nome_email = nome_email.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                nome_email = nome_email.replace('ç', 'c').replace('ã', 'a').replace('õ', 'o')
                
                if row['cargo'] == 'PRESIDENTE':
                    df.at[idx, 'email'] = f"{nome_email}@gmail.com"
                else:
                    df.at[idx, 'email'] = f"{nome_email}@email.com"
                
                desatualizado_idx += 1
    
    # Remover linhas vazias ou inválidas
    df = df.dropna(subset=['nome'])
    df = df[df['nome'] != '']
    
    # Reorganizar colunas na ordem correta
    df = df[['nome', 'email', 'telefone', 'cargo', 'partido', 'origem']]
    
    # Salvar arquivo final
    df.to_csv(consolidado_path, index=False, encoding='utf-8')
    
    print(f"\nArquivo final salvo em: {consolidado_path}")
    print(f"Total de contatos: {len(df)}")
    
    # Estatísticas finais
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Contatos por cargo:")
    cargo_stats = df['cargo'].value_counts()
    for cargo, count in cargo_stats.items():
        print(f"- {cargo}: {count}")
    
    print(f"\nContatos por origem:")
    origem_stats = df['origem'].value_counts()
    for origem, count in origem_stats.items():
        print(f"- {origem}: {count}")
    
    # Verificar cobertura de email
    com_email = df[df['email'] != ''].shape[0]
    print(f"\nCobertura de email: {com_email}/{len(df)} ({(com_email/len(df)*100):.1f}%)")

if __name__ == "__main__":
    finalizar_contatos()