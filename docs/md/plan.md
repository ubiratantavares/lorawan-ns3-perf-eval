# Planejamento Estratégico e Arquitetural: Avaliação de Desempenho de Redes LoRaWAN no ns-3

Este documento estabelece o planejamento estratégico, metodológico e de engenharia de software para a execução do trabalho prático da disciplina de Redes de Computadores Sem Fio (período 2026/2), ministrada pelo Prof. Marcelo Rubinstein no Programa de Pós-Graduação em Engenharia Eletrônica (PEL/DETEL/FEN) da Universidade do Estado do Rio de Janeiro (UERJ).

O plano estrutura a concepção, implementação e avaliação experimental do projeto centrado na tecnologia LoRaWAN, integrando simulação de eventos discretos em C++ no ns-3, plataforma analítica e orquestradora em Python, e governança orientada por especificações (Specification-Driven Development - SDD), apoiada nos princípios de Programação Orientada a Objetos (POO), SOLID, Clean Code e Arquitetura Hexagonal.

1. Análise, Verificação e Avaliação da Fonte trcsf26-2v1.pdf

A fonte trcsf26-2v1.pdf define as diretrizes regulatórias e os critérios formais para a realização dos trabalhos da disciplina. A análise crítica do documento estabelece as seguintes restrições e marcos obrigatórios:

* Modalidade de Execução: Trabalho individual obrigatório.

* Escopo Temático: Avaliação de desempenho utilizando simulação em ns-2 ou ns-3. O documento lista temas pré-aprovados (TCP em redes sem fio, Roteamento ad hoc, QoS 802.11e EDCA, Modelos de propagação, ZigBee, Bluetooth, VANET 802.11p, Sensores subaquáticos) e autoriza expressamente a categoria "Outros", na qual se insere com total adequação o projeto LoRaWAN como rede LPWAN (Low Power Wide Area Network).

* Marco 1 — Proposta (Relatório Parcial):

  * Extensão exigida: 10 páginas.

  * Formato: Padrão da Sociedade Brasileira de Computação (SBC).

  * Conteúdo obrigatório: Introdução contextualizada, problema a ser abordado, levantamento e discussão das soluções, proposta de avaliação de desempenho das soluções e referências bibliográficas.

* Marco 2 — Relatório Final:

  * Extensão exigida: 14 páginas.

  * Formato: Padrão da SBC.

  * Conteúdo obrigatório: Todos os elementos do relatório parcial, acrescidos da avaliação experimental efetivamente realizada (gráficos, tabelas, análise crítica detalhada) e conclusão técnica fundamentada.

A avaliação da fonte confirma que o sucesso acadêmico e técnico do projeto depende de uma clara separação entre a fase de formulação metodológica (atendida pela Proposta de 10 páginas) e a fase de experimentação e inferência estatística (consolidada no Relatório Final de 14 páginas).

2. Alinhamento Tecnológico: LoRaWAN e o Ecossistema ns-3

O LoRaWAN opera nas faixas ISM sub-GHz (868 MHz na Europa e 915 MHz nas Américas), combinando modulação por chirp (CSS - Chirp Spread Spectrum) na camada física com topologia estrela de estrelas na camada MAC. As estações finais comunicam-se em salto único com gateways, os quais encaminham os quadros brutos para um servidor de rede central (Network Server).

2.1 Capacidades Disponíveis no ns-3

No ecossistema ns-3, o suporte a LoRaWAN é provido pelo módulo aberto de pesquisa lorawan (desenvolvido por Magrin et al. da Universidade de Pádua). Esse módulo disponibiliza:

* Modelagem da camada física LoRa (transmissores, receptores de gateway multicanal e cálculo de interferência co-canal e ortogonalidade entre Spreading Factors SF7 a SF12).

* Modelos de propagação com desvanecimento log-normal e perda de percurso adaptada para cenários urbanos e suburbanos.

* Mecanismos da classe A do LoRaWAN (abertura estrita de duas janelas temporais de recepção, RX1 e RX2, após transmissões no enlace ascendente).

2.2 Lacunas Técnicas a Serem Implementadas pelo Projeto

Conforme exigido pelo escopo do trabalho, os componentes e comportamentos não implementados nativamente na distribuição base do ns-3 serão construídos pelo projeto (ver ADR-002):

1. Estratégias de Alocação de Fator de Espalhamento: o módulo `lorawan` 0.3.7 já oferece alocação por distribuição (`SetSpreadingFactorsGivenDistribution`, usada para SF fixo e aleatório), estática por orçamento de enlace (`SetSpreadingFactorsUp`) e ADR dinâmico (`AdrComponent`). O projeto encapsula essas opções sob a interface `ISpreadingFactorAllocationStrategy` e distingue explicitamente alocação estática por RSSI/distância (`DISTANCE`) de ADR dinâmico (`ADR`).

2. Camada de Suporte a Classes B e C: Modelagem de beacons periódicos para janelas sincronizadas de recepção (Classe B) e escuta contínua (Classe C) para atuadores. *(Fora do escopo das campanhas; trabalho futuro.)*

3. Instrumentação do Duty Cycle Regulatório: o controle de 1% por sub-banda já existe no módulo (`SubBand`, trace `CannotSendBecauseDutyCycle`). O projeto não o reimplementa: instrumenta os descartes e permite desabilitá-lo para isolar seu efeito (experimento E-DC).

4. Instrumentação Desacoplada de Métricas: Sistema de tracing e exportação estruturada de eventos das camadas MAC e PHY em formato padronizado (JSON e CSV), viabilizando rastreabilidade experimental completa.

3. Governança por Especificação: Abordagem SDD (Specification-Driven Development)

Adotando o padrão metodológico formalizado na especificação sdd.md, o projeto LoRaWAN estabelece uma referência técnica única antes de qualquer linha de código ser escrita.

3.1 Convenções de Nomenclatura e Rastreabilidade

* RF: Requisito Funcional.

* RNF: Requisito Não Funcional.

* DOM: Elemento do Modelo de Domínio.

* CT: Contrato de Dados e Integração.

* CA: Critério de Aceitação.

* ADR: Architecture Decision Record.

3.2 Requisitos Funcionais Centrais

* RF-001 (Configuração da Topologia LPWAN): O sistema deve configurar gateways e dispositivos finais distribuídos no espaço bidimensional com raio de cobertura parametrizável (1 a 10 km).

* RF-002 (Parametrização da Camada Física LoRa): O sistema deve permitir a configuração do Fator de Espalhamento (SF7 a SF12), largura de banda (125, 250 ou 500 kHz), frequência de canal e potência de transmissão.

* RF-003 (Execução com Controle Estocástico): O sistema deve suportar execuções controladas via semente aleatória (SimulationSeed) e identificador de replicação (RngRun), garantindo reprodutibilidade matemática.

* RF-004 (Instrumentação de Camada MAC): O sistema deve registrar eventos de transmissão, colisão no ar por sobreposição de SF, descartes por limite de duty cycle e recepções bem-sucedidas no Gateway.

* RF-005 (Exportação Estruturada): Ao término da simulação, os dados brutos devem ser salvos em diretório isolado contendo arquivos de métricas e metadados de execução (metadata.json).

3.3 Modelo de Domínio (DDD)

A modelagem orientada a objetos do domínio LoRaWAN é composta por:

* Entidades: EndDeviceNode (identificador, classe A/B/C, bateria residual), GatewayNode (demoduladores paralelos, coordenadas), NetworkServer (gerenciador central de deduplicação e ADR).

* Objetos de Valor (Value Objects): LoraCoordinates (posição espacial imutável), SpreadingFactor (enumeração SF7..SF12), BandwidthHz, TransmissionPowerDbm, LoraFrame (quadro físico com estampa de tempo, canal e payload).

* Agregado: LoraCellAggregate (coordena a relação espacial entre um conjunto de End Devices e seus Gateways associados).

3.4 Contratos de Dados (CT)

Para garantir desacoplamento absoluto entre o orquestrador em Python e o motor em C++, os seguintes contratos estruturados são estabelecidos:

* CT-001 (Arquivo de Cenário - YAML/JSON):

  * scenario_id: Identificador único do cenário.

  * duration_seconds: Tempo total de simulação.

  * topology: Parâmetros do raio da célula, número de gateways e quantidade de nós.

  * lora_settings: Banda base, canais habilitados e estratégia de alocação de SF (Fixo, Aleatório ou ADR).

* CT-002 (Metadados de Execução - JSON):

  * Registro de semente aleatória (seed), replicação (run), versão do ns-3, hash do código fonte Git e estampa de tempo da execução.

* CT-003 (Métricas Brutas de Saída - CSV):

  * Colunas padronizadas: verifique a referência `./docs/md/sdd-lorawan.md §5`

4. Arquitetura de Software: POO, SOLID, Clean Code e Arquitetura Hexagonal

A solução divide-se em dois macrocomponentes desacoplados: o Núcleo de Simulação (C++) e a Plataforma Analítica e Orquestradora (Python), conectados exclusivamente pelos contratos de dados.

4.1 Arquitetura Hexagonal (Ports & Adapters) na Plataforma Python

A orquestração e o processamento de resultados em Python são construídos sobre uma arquitetura hexagonal estrita:

* Domínio Central (Inside):

  * Entidades e regras de agregação de métricas (cálculo de vazão, taxa de entrega de pacotes - PDR, energia consumida por bit útil entregue).

  * Serviços de domínio estatístico (cálculo de intervalos de confiança, teste t pareado e teste de normalidade).

* Portas de Entrada (Driving Ports):

  * IExperimentOrchestrator: Interface para execução parametrizada de campanhas experimentais.

  * IAnalysisService: Interface para geração de tabelas e figuras no padrão SBC.

* Portas de Saída (Driven Ports):

  * INs3SimulationRunner: Interface abstrata para invocação do binário de simulação C++.

  * IResultsRepository: Interface para leitura e persistência de arquivos CSV e JSON.

* Adaptadores (Adapters):

  * SubprocessNs3Adapter: Implementa a execução do ns-3 via linha de comando, capturando saídas de log sem acoplamento direto de bibliotecas.

  * FileSystemResultsAdapter: Manipula a persistência e isolamento dos arquivos brutos em disco.

4.2 Diretrizes de SOLID e Clean Code no Núcleo C++

* Princípio da Responsabilidade Única (SRP): Classes especializadas para cada função de rede. A classe LoraMacProtocol gerencia apenas temporizações e janelas de recepção; a classe PropagationModel resolve apenas equações de atenuação; e MetricsTracker cuida exclusivamente do registro de eventos.

* Princípio Aberto/Fechado (OCP): Novos algoritmos de alocação de Fator de Espalhamento são introduzidos através da implementação de uma interface abstrata ISpreadingFactorAllocationStrategy, sem alterar a máquina de estados central do rádio.

* Princípio da Inversão de Dependência (DIP): O simulador depende de interfaces abstratas de canais de comunicação, permitindo alternar entre modelos de canal livre e canais com sombreamento e interferência urbana.

* Clean Code: Funções pequenas (menos de 20 linhas), nomes autoexplicativos sem codificação húngara, tratamento defensivo de ponteiros via smart pointers (std::shared_ptr / ns3::Ptr) e ausência de efeitos colaterais ocultos.

5. Metodologia de Avaliação de Desempenho (Arcabouço de Raj Jain)

O planejamento experimental e a análise de resultados apoiam-se rigorosamente na taxonomia do livro The Art of Computer Systems Performance Analysis do Prof. Raj Jain:

5.1 Seleção Sistemática de Métricas

* Higher is Better (HB):

  * Taxa de Entrega de Pacotes (PDR - Packet Delivery Ratio): Razão entre pacotes recebidos pelo Network Server e pacotes gerados pelos End Devices.

  * Vazão Efetiva da Rede (Throughput Global em bps): Total de bits úteis entregues por unidade de tempo.

* Lower is Better (LB):

  * Atraso Fim a Fim (Latency em ms): Intervalo entre o início da transmissão no nó sensor e a recepção no servidor de rede.

  * Consumo de Energia por Pacote Útil (Joules): Energia gasta pelo transmissor dividida pelo número de pacotes com sucesso.

  * Taxa de Colisão Co-canal: Proporção de transmissões destruídas por interferência de mesmo SF e canal.

* Índice de Equidade:

  * Jain's Fairness Index (JFI): Avaliação da equidade de acesso ao canal entre nós situados em distâncias heterogêneas do gateway.

* Métrica de Diagnóstico:

  * Descartes por Duty Cycle: Proporção de pacotes não transmitidos por esgotamento da janela regulatória (trace `CannotSendBecauseDutyCycle`).

5.2 Fatores Experimentais e Tratamento Estatístico (ver ADR-002)

* Fatorial Completo Principal (5 × 3 × 2 = 30 pontos):

  1. Fator A — Densidade de Nós: 100, 250, 500, 1000 e 2000 End Devices.

  2. Fator B — Estratégia de Fator de Espalhamento: `RANDOM` (uniforme SF7–SF12), `DISTANCE` (estática por orçamento de enlace) e `ADR` (dinâmica no Network Server).

  3. Fator C — Período de Envio: 60 s (carga alta) e 600 s (carga baixa).

* Parâmetros Fixos do Cenário Base: raio de 2 km, 1 gateway central, EU868 com 3 canais, payload de 20 bytes, duty cycle de 1% habilitado.

* Experimentos Complementares (um fator por vez):

  * E-DC (H3/QP-03): duty cycle ligado vs. desligado, com B = ADR e C = 60 s, para todos os níveis de A (5 pontos).

  * E-R (sensibilidade ao raio): raio de 6 km, com B ∈ {DISTANCE, ADR} e C = 600 s, para todos os níveis de A (10 pontos).

* Testes Degenerados de Validação (Jain, cap. 25): SF12 fixo para todos os nós; 1 nó isolado (PDR ≈ 100%); 5 nós a 100 m do gateway.

* Tratamento de Transientes e Parada: Descarte do período de inicialização (warm-up phase) de 10 minutos; tempo de medição em regime permanente de no mínimo 1 hora simulada (≥ 3 × período de envio).

* Replicações e Confiança: `RngSeed = 1` fixo e `RngRun = 1..30` (30 replicações independentes por ponto), reportando a média amostral com IC de 95% (t de Student). Comparação ADR × RANDOM por teste t pareado (mesmo `RngRun`, α = 0,05).

* Custo Computacional: 45 pontos × 30 replicações = 1350 execuções, paralelizáveis via multiprocessing.

6. Planejamento Editorial: Estruturação dos Relatórios SBC

Para assegurar conformidade irrestrita com os limites de páginas definidos em trcsf26-2v1.pdf, a distribuição de páginas por seção é detalhada abaixo:

6.1 Distribuição de Páginas: Proposta Parcial (10 Páginas SBC)

Seção do Artigo SBC	Conteúdo Principal	Meta de Páginas

Cabeçalho & Resumo/Abstract	Título, autor, afiliação UERJ, resumo e palavras-chave.	0,5 pág.

1. Introdução e Justificativa	Cenário das redes LPWAN, IoT e relevância do LoRaWAN.	1,5 págs.

2. O Problema de Pesquisa	Escalabilidade sob ALOHA puro, colisões e perda de ortogonalidade.	1,5 págs.

3. Revisão Bibliográfica e Soluções	Estado da arte em alocação de SF, ADR e simulação em ns-3.	2,5 págs.

4. Metodologia de Avaliação Proposta	Variáveis, fatores, métricas de Jain, modelo de simulação e ferramentas.	2,5 págs.

5. Referências Bibliográficas	Fontes científicas formatadas estritamente no estilo da SBC.	1,5 págs.

TOTAL OBRIGATÓRIO		10,0 págs.

6.2 Distribuição de Páginas: Relatório Final (14 Páginas SBC)

Seção do Artigo SBC	Conteúdo Principal	Meta de Páginas

Cabeçalho & Resumo/Abstract	Resumo atualizado com os principais achados quantitativos.	0,5 pág.

1. Introdução	Contextualização consolidada e objetivos da pesquisa.	1,5 págs.

2. O Problema de Pesquisa	Formulação rigorosa e hipóteses experimentais testadas.	1,0 pág.

3. Trabalhos Relacionados	Síntese comparativa da literatura.	2,0 págs.

4. Arquitetura e Modelo Experimental	Descrição do modelo ns-3, módulos C++ e governança SDD.	2,0 págs.

5. Avaliação de Desempenho e Resultados	Gráficos (PDR, vazão, energia, atraso), tabelas e análise estatística com IC 95%.	4,5 págs.

6. Conclusões e Trabalhos Futuros	Síntese das contribuições e diretrizes de dimensionamento.	1,0 pág.

7. Referências Bibliográficas	Fontes científicas formatadas no estilo da SBC.	1,5 págs.

TOTAL OBRIGATÓRIO		14,0 págs.

7. Roteiro Passo a Passo de Execução

O cronograma operacional estrutura-se em cinco etapas lógicas:

[Etapa 1: Especificação SDD] 
       │
       ▼
[Etapa 2: Proposta Parcial - 10 págs SBC]
       │
       ▼
[Etapa 3: Implementação C++ & Python]
       │
       ▼
[Etapa 4: Campanha Experimental & Análise]
       │
       ▼
[Etapa 5: Relatório Final - 14 págs SBC]


Passo 1: Elaboração da Especificação Técnica (Semana 1)

1. Escrever o documento formal de requisitos e arquitetura (sdd-lorawan.md) com todos os RFs, RNFs e contratos de interface.

2. Definir os esquemas de dados JSON para troca de parâmetros entre o orquestrador Python e o simulador ns-3.

Passo 2: Redação e Entrega da Proposta Parcial de 10 Páginas (Semanas 2 e 3)

1. Redigir os textos das seções 1 a 4 conforme a distribuição de páginas da Tabela 6.1.

2. Formatar o documento no template oficial LaTeX da SBC (sbc-template.tex).

3. Revisar as referências para garantir o alinhamento com a literatura fundamental de redes sem fio e análise de desempenho.

Passo 3: Implementação e Verificação do Software (Semanas 4 a 6)

1. Configurar o ambiente ns-3 com o módulo lorawan fixado em versão estável.

2. Implementar em C++ os módulos complementares ou customizações de alocação de canal e tracing, validando-os por meio de testes unitários e testes degenerados (conforme recomendado por Jain no Capítulo 25).

3. Construir a biblioteca de orquestração e coleta em Python aplicando Arquitetura Hexagonal, com testes unitários automatizados via pytest.

Passo 4: Execução da Campanha Experimental (Semanas 7 e 8)

1. Executar os ensaios de validação de conectividade em cenário reduzido (1 gateway e 5 nós).

2. Disparar a matriz experimental completa automatizada pelo orquestrador Python, variando sementes e densidades de nós.

3. Consolidar os dados brutos e executar a sumarização estatística (médias, variâncias e intervalos de confiança de 95%).

Passo 5: Redação e Finalização do Relatório Final de 14 Páginas (Semanas 9 e 10)

1. Incorporar os capítulos da Proposta Parcial, refinando a introdução com base nas descobertas práticas.

2. Adicionar a seção completa de Avaliação de Desempenho e Resultados utilizando os dados consolidados:

  * Gráficos com barras de erro comparando PDR vs. Densidade de Nós para cada estratégia de SF.

  * Gráficos de atraso médio e vazão agregada do gateway.

  * Tabelas de dispersão e análise comparativa de equidade (Jain's Fairness Index).

3. Redigir a Conclusão Técnica, apontando as limitações da tecnologia sob tráfego massivo e sugerindo diretrizes operacionais para implantações reais de cidades inteligentes e sensores ambientais.

8. Matriz de Riscos Técnicos e Mitigações

Risco Técnico Identificado	Impacto	Estratégia de Mitigação
Incompatibilidade da API do módulo LoRa com a versão do ns-3	Alto	Fixar o container ou ambiente de compilação em versão documentada antes do início do código.
Tempo excessivo de CPU para simular 1000 nós com dezenas de replicações	Médio	Utilizar paralelização de execuções independentes no Python via multiprocessing, já que as replicações são desacopladas.
Subestimação de colisões no modelo de rádio	Alto	Validar o modelo físico com testes degenerados e verificar se matrizes de sobreposição de SF estão habilitadas no módulo.
Desvio de formatação do artigo em relação às normas SBC	Médio	Utilizar o template oficial LaTeX da SBC (sbc-template.tex) desde o primeiro rascunho do relatório parcial.

