# Como S�o Calculadas as Cadeiras na C�mara dos Deputados: Guia Completo do Sistema Proporcional

## Introdu��o

O c�lculo das cadeiras na C�mara dos Deputados � um dos aspectos mais complexos do sistema eleitoral brasileiro. Diferentemente das elei��es majorit�rias, onde vence simplesmente quem tem mais votos, a distribui��o das 513 cadeiras da C�mara segue um sistema proporcional que considera tanto a popula��o de cada estado quanto os votos recebidos por partidos e candidatos. Compreender esse processo � fundamental para entender como funciona a representa��o pol�tica no Brasil.

## Fundamentos Constitucionais

### Base Legal
A distribui��o das cadeiras na C�mara dos Deputados est� regulamentada por:
- **Constitui��o Federal de 1988**: Artigos 17, 45 e 46
- **Lei Complementar 78/1993**: Fixa o n�mero de deputados por estado
- **C�digo Eleitoral**: Procedimentos de c�lculo
- **Resolu��es do TSE**: Normas espec�ficas para cada elei��o

### Princ�pios Fundamentais
- **Representa��o proporcional**: Vagas distribu�das conforme for�a eleitoral
- **Representa��o populacional**: Estados com mais habitantes t�m mais deputados
- **Representa��o federativa**: Garantia m�nima e m�xima de deputados por estado
- **Periodicidade**: Redistribui��o a cada censo demogr�fico

## Distribui��o de Cadeiras por Estado

### Crit�rio Populacional
O n�mero de deputados federais por estado � calculado com base na **popula��o apurada no �ltimo censo demogr�fico**, realizado pelo IBGE a cada 10 anos.

### Limites Constitucionais
- **M�nimo**: 8 deputados por estado
- **M�ximo**: 70 deputados por estado
- **Total nacional**: 513 deputados
- **Distrito Federal**: Tratado como estado para fins eleitorais

### F�rmula de C�lculo
```
Deputados por Estado = (Popula��o do Estado � Popula��o Nacional) � 513
```
*Respeitados os limites m�nimo e m�ximo*

### Distribui��o Atual (2022-2026)
**Estados com m�ximo (70 deputados):**
- S�o Paulo: 70 deputados

**Estados com maior representa��o:**
- Minas Gerais: 53 deputados
- Rio de Janeiro: 46 deputados
- Bahia: 39 deputados
- Paran�: 30 deputados
- Rio Grande do Sul: 31 deputados

**Estados com m�nimo (8 deputados):**
- Acre, Amap�, Roraima, Tocantins

## Sistema de Elei��o Proporcional

### Caracter�sticas Gerais
- **Lista aberta**: Eleitor vota em candidato espec�fico ou na legenda
- **Circunscri��o estadual**: Cada estado � uma unidade eleitoral
- **M�ltiplos eleitos**: V�rias cadeiras preenchidas simultaneamente
- **C�lculo complexo**: Envolve quocientes e distribui��o de sobras

### Etapas do C�lculo

#### 1. C�lculo do Quociente Eleitoral
**F�rmula:**
```
Quociente Eleitoral = Votos V�lidos � Cadeiras Dispon�veis
```

**Exemplo - S�o Paulo (70 cadeiras):**
- Total de votos v�lidos: 28.000.000
- Cadeiras dispon�veis: 70
- Quociente Eleitoral: 28.000.000 � 70 = 400.000 votos

#### 2. C�lculo do Quociente Partid�rio
**F�rmula:**
```
Quociente Partid�rio = Votos do Partido � Quociente Eleitoral
```

**Exemplo:**
- Partido A: 2.400.000 votos
- Quociente Partid�rio: 2.400.000 � 400.000 = 6 cadeiras

#### 3. Distribui��o das Sobras
Quando nem todas as cadeiras s�o preenchidas pelo quociente partid�rio, utiliza-se o **M�todo d'Hondt**.

**Procedimento:**
1. Divide-se os votos de cada partido por (cadeiras obtidas + 1)
2. A cadeira vai para o partido com maior resultado
3. Repete-se at� preencher todas as vagas

### Exemplo Pr�tico Completo

**Estado Fict�cio - 10 cadeiras dispon�veis:**
- Total de votos v�lidos: 2.000.000
- Quociente Eleitoral: 2.000.000 � 10 = 200.000

**Resultados por Partido:**

| Partido | Votos | Quociente Partid�rio | Cadeiras |
|---------|-------|---------------------|----------|
| A | 850.000 | 850.000 � 200.000 = 4,25 | 4 |
| B | 650.000 | 650.000 � 200.000 = 3,25 | 3 |
| C | 350.000 | 350.000 � 200.000 = 1,75 | 1 |
| D | 150.000 | 150.000 � 200.000 = 0,75 | 0 |

**Subtotal:** 8 cadeiras distribu�das, restam 2 sobras.

**Distribui��o de Sobras (M�todo d'Hondt):**

*Primeira sobra:*
- Partido A: 850.000 � (4+1) = 170.000
- Partido B: 650.000 � (3+1) = 162.500
- Partido C: 350.000 � (1+1) = 175.000 � **Maior**
- Partido D: 150.000 � (0+1) = 150.000

**Partido C ganha 1 sobra � Total: 2 cadeiras**

*Segunda sobra:*
- Partido A: 850.000 � (4+1) = 170.000 � **Maior**
- Partido B: 650.000 � (3+1) = 162.500
- Partido C: 350.000 � (2+1) = 116.667
- Partido D: 150.000 � (0+1) = 150.000

**Partido A ganha 1 sobra � Total: 5 cadeiras**

**Resultado Final:**
- Partido A: 5 cadeiras
- Partido B: 3 cadeiras
- Partido C: 2 cadeiras
- Partido D: 0 cadeiras

## Elei��o dos Candidatos Individuais

### Ordem de Prioridade
Dentro de cada partido/coliga��o, os candidatos s�o eleitos na seguinte ordem:
1. **Candidatos que atingiram o quociente eleitoral individualmente**
2. **Candidatos mais votados** (na ordem decrescente de votos)

### Quociente Eleitoral Individual
Um candidato atinge o quociente eleitoral quando seus votos individuais s�o iguais ou superiores ao quociente eleitoral do estado.

**Exemplo:**
- Quociente Eleitoral: 400.000 votos
- Candidato X: 450.000 votos � **Eleito automaticamente**
- Candidato Y: 350.000 votos � Depende das cadeiras do partido

### Vota��o de Legenda
- **Voto na legenda**: Conta para o quociente partid�rio
- **Distribui��o**: Beneficia os candidatos mais votados do partido
- **Estrat�gia**: Pode fortalecer candidatos com menos votos individuais

## Mudan�as Recentes: Fim das Coliga��es

### Antes de 2020
- **Coliga��es permitidas**: Partidos podiam se unir para elei��es proporcionais
- **C�lculo conjunto**: Votos de todos os partidos coligados somados
- **Distribui��o interna**: Cadeiras distribu�das entre partidos da coliga��o

### A partir de 2020
- **Fim das coliga��es proporcionais**: Cada partido concorre isoladamente
- **Federa��es partid�rias**: Nova modalidade de uni�o permanente
- **C�lculo individual**: Cada partido tem seu pr�prio quociente

### Impacto das Mudan�as
**Para Partidos Pequenos:**
- Maior dificuldade para atingir quociente eleitoral
- Necessidade de estrat�gias alternativas
- Busca por federa��es partid�rias

**Para o Sistema:**
- Redu��o do n�mero de partidos com representa��o
- Maior clareza na escolha do eleitor
- Poss�vel concentra��o partid�ria

## Federa��es Partid�rias

### Conceito
Uni�o permanente de partidos que funciona como uma �nica legenda nas elei��es, durando no m�nimo 4 anos.

### Funcionamento Eleitoral
- **C�lculo �nico**: Votos de todos os partidos federados somados
- **Distribui��o proporcional**: Cadeiras distribu�das conforme acordo interno
- **Atua��o conjunta**: Obrigatoriedade de votar em bloco no Congresso

### Vantagens
- **Viabilidade eleitoral**: Partidos pequenos mant�m competitividade
- **Estabilidade**: Alian�as duradouras
- **Governabilidade**: Blocos coesos no Parlamento

## Aspectos Pr�ticos do C�lculo

### Votos V�lidos
**Incluem:**
- Votos em candidatos
- Votos de legenda
- Votos em federa��es

**Excluem:**
- Votos brancos
- Votos nulos
- Absten��es

### Casos Especiais

#### Empate no M�todo d'Hondt
Em caso de empate na distribui��o de sobras:
1. **Partido com mais votos totais** leva a vaga
2. **Persistindo empate**: Sorteio p�blico

#### Candidato com Quociente Eleitoral em Partido sem Cadeiras
- **Situa��o rara**: Candidato individual atinge quociente, mas partido n�o
- **Solu��o**: Candidato � eleito e partido ganha a cadeira correspondente

#### Ren�ncia ou Morte de Candidato Eleito
- **Substitui��o**: Pr�ximo candidato mais votado do mesmo partido
- **Ordem**: Respeitada a ordem original de vota��o

## Compara��o com Outros Pa�ses

### Sistema Brasileiro vs. Internacional

**Brasil:**
- Lista aberta com voto preferencial
- M�todo d'Hondt para sobras
- Circunscri��o estadual

**Portugal:**
- Lista fechada
- M�todo d'Hondt
- C�rculos eleitorais menores

**Alemanha:**
- Sistema misto (distrital + proporcional)
- Compensa��o proporcional nacional
- Duas c�dulas de vota��o

### Vantagens do Sistema Brasileiro
- **Escolha individual**: Eleitor pode escolher candidato espec�fico
- **Representa��o estadual**: Garante representa��o de todos os estados
- **Flexibilidade**: Permite renova��o dos quadros pol�ticos

### Desvantagens Identificadas
- **Complexidade**: Dificuldade de compreens�o pelo eleitor
- **Campanha personalizada**: Enfraquecimento dos partidos
- **Custo elevado**: Campanhas individuais caras

## Impacto na Representa��o Nacional

### Representatividade Regional
- **Norte**: Sub-representado em termos populacionais
- **Nordeste**: Representa��o pr�xima � proporcional
- **Sudeste**: Concentra maior n�mero de deputados
- **Sul**: Representa��o equilibrada
- **Centro-Oeste**: Crescimento da representa��o

### Consequ�ncias Pol�ticas
- **Federalismo**: Equilibrio entre estados grandes e pequenos
- **Governabilidade**: Necessidade de construir maiorias amplas
- **Representa��o**: Diversidade de correntes pol�ticas

## Perspectivas e Reformas

### Propostas em Discuss�o

#### Sistema Distrital
- **Divis�o em distritos**: Cada distrito elege um deputado
- **Voto majorit�rio**: Vence quem tem mais votos no distrito
- **Proximidade**: Maior rela��o eleitor-representante

#### Sistema Misto
- **Parte distrital**: Metade dos deputados eleitos por distrito
- **Parte proporcional**: Metade por representa��o proporcional
- **Compensa��o**: Resultado final proporcional

#### Lista Fechada
- **Voto apenas no partido**: Eleitor escolhe legenda, n�o candidato
- **Ordem pr�-definida**: Partido determina ordem dos candidatos
- **Disciplina partid�ria**: Fortalecimento dos partidos

### Argumentos do Debate

**Defensores do Sistema Atual:**
- Tradi��o democr�tica consolidada
- Representa��o da diversidade brasileira
- Capacidade de renova��o pol�tica
- Equil�brio federativo

**Defensores de Reformas:**
- Necessidade de maior governabilidade
- Simplifica��o para o eleitor
- Fortalecimento dos partidos
- Maior proximidade representante-eleitor

## Educa��o Pol�tica e Transpar�ncia

### Informa��o ao Eleitor
- **Simuladores**: Ferramentas online para entender o c�lculo
- **Divulga��o**: TSE explica o processo em linguagem acess�vel
- **Transpar�ncia**: Disponibiliza��o de dados detalhados
- **Educa��o c�vica**: Programas de esclarecimento

### Papel da M�dia
- **Cobertura educativa**: Explica��o do sistema durante elei��es
- **An�lise cr�tica**: Debate sobre vantagens e desvantagens
- **Fiscaliza��o**: Acompanhamento dos c�lculos oficiais

## Tecnologia e Moderniza��o

### Sistemas Informatizados
- **C�lculo autom�tico**: Software espec�fico para apura��o
- **Auditoria digital**: Verifica��o eletr�nica dos resultados
- **Transpar�ncia online**: Divulga��o em tempo real
- **Simula��es**: Ferramentas para cen�rios hipot�ticos

### Inova��es Futuras
- **Intelig�ncia artificial**: Otimiza��o dos c�lculos
- **Blockchain**: Garantia de transpar�ncia e auditabilidade
- **Visualiza��o**: Ferramentas gr�ficas para compreens�o

## Conclus�o

O c�lculo das cadeiras na C�mara dos Deputados representa um dos aspectos mais sofisticados do sistema eleitoral brasileiro, buscando equilibrar representa��o populacional, diversidade pol�tica e governabilidade. Embora complexo, o sistema garante que a composi��o da C�mara reflita tanto a for�a eleitoral dos partidos quanto a distribui��o populacional do pa�s.

As recentes mudan�as, como o fim das coliga��es proporcionais e a cria��o das federa��es partid�rias, demonstram a capacidade de evolu��o do sistema. O debate sobre poss�veis reformas continuar� sendo importante para aperfei�oar a representa��o democr�tica, sempre considerando as particularidades de um pa�s continental e diverso como o Brasil.

A compreens�o desse processo pelos cidad�os � fundamental para o exerc�cio consciente do voto e para o fortalecimento da democracia. Quanto melhor os eleitores entenderem como seus votos se transformam em representa��o pol�tica, mais qualificada ser� a participa��o democr�tica e mais leg�timos ser�o os resultados eleitorais.

O sistema brasileiro, com suas especificidades e complexidades, continua evoluindo para atender �s demandas de uma sociedade democr�tica moderna, sempre buscando o equil�brio entre efici�ncia governamental e representatividade pol�tica.