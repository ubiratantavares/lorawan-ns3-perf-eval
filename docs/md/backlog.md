O cronograma cobre o período de **23/11/2026 a 25/01/2027**, distribuído em **9 Sprints semanais** com alinhamento estrito aos dois marcos da fonte `trcsf26-2v1.pdf`:

* 📌 **Marco 1 — Proposta / Relatório Parcial (10 páginas no padrão SBC):** **08/12/2026** (Fim da Sprint 2).

* 📌 **Marco 2 — Relatório Final (14 páginas no padrão SBC):** **25/01/2027** (Fim da Sprint 9).

### **1. Estrutura do Scrum e Definição de Pronto (*Definition of Done - DoD*)**

* **Papéis Adaptados:** O aluno acumula os papéis de *Product Owner* (direcionamento dos requisitos e escopo acadêmico) e *Developers* (engenharia de software e análise), tendo o professor e a ementa como partes interessadas (*stakeholders*).

* **Artefatos:** *Product Backlog* priorizado, *Sprint Backlogs* semanais, *Burndown* de entregáveis e *Increments* testados a cada sprint.

* **Definition of Done (DoD) Geral:**

  * Código C++ compilando sem alertas com `ns-3` (Waf/CMake), tipado defensivamente e testado.

  * Código Python formatado (`black`/`flake8`), com cobertura de testes unitários (`pytest`) para as regras do domínio analítico.

  * Metadados experimentais persistidos e rastreáveis (JSON/CSV).

  * Seções textuais escritas estritamente no template da **SBC** (*LaTeX/Overleaf*), respeitando a contagem rigorosa de páginas (10 páginas no parcial; 14 páginas no final).

### **2. Product Backlog (Épicos e Histórias de Usuário)**

| ID Épico | Épico | Descrição |
| :--- | :--- | :--- |
| **EP-01** | **Infraestrutura e Ambiente ns-3** | Preparação do ambiente Linux/Ubuntu, compilação do ns-3 e integração do módulo LoRaWAN. |
| **EP-02** | **Governança SDD e Especificação Técnica** | Formalização de requisitos (RF/RNF), modelo de domínio (DDD) e contratos de dados (YAML/JSON). |
| **EP-03** | **Proposta / Relatório Parcial (10 págs SBC)** | Redação da introdução, problema, soluções e proposta metodológica para o marco de 08/12/2026. |
| **EP-04** | **Arquitetura Hexagonal & Engenharia C++/Python** | Implementação dos componentes de rádio/MAC LoRaWAN em C++ e do orquestrador analítico em Python. |
| **EP-05** | **Campanhas de Simulação e Controle Estocástico** | Execução de matrizes de testes fatoriais com controle estrito de sementes (`RngSeed`/`RngRun`). |
| **EP-06** | **Processamento Estatístico & Visualização (Raj Jain)** | Análise amostral, intervalos de confiança de 95%, testes de hipóteses e geração de gráficos sem viés. |
| **EP-07** | **Relatório Final SBC (14 págs) & Fechamento** | Consolidação do documento completo, conclusões e empacotamento para reprodutibilidade. |

### **3. Cronograma das Sprints Semanais (Passo a Passo)**

```
[23/11/2026] ── Sprint 1 ── Sprint 2 ──► 🏁 [08/12/2026: Relatório Parcial - 10 págs]
                                           │
[08/12/2026] ── Sprints 3 a 8 ───────────► 🏁 [25/01/2027: Relatório Final - 14 págs]
```

#### **FASE 1: CONCEPÇÃO, AMBIENTE E RELATÓRIO PARCIAL (Até 08/12/2026)**

#### **Sprint 1 (23/11/2026 a 29/11/2026)**

* **Objetivo da Sprint:** Instalar e validar o ecossistema ns-3 com o módulo LoRaWAN e elaborar a estrutura base do documento de especificação (SDD) e do template SBC.

* **Backlog da Sprint:**

  1. *[EP-01]* Provisionar ambiente Linux (Ubuntu LTS), instalar dependências de build (`gcc`, `g++`, `cmake`, `python3-dev`, `ninja`).

  2. *[EP-01]* Clonar e compilar a distribuição do **ns-3** e integrar o módulo de simulação `lorawan`.

  3. *[EP-01]* Executar e validar o cenário de exemplo padrão (`lora-packet-tracker.cc`) para confirmar a compilação e a geração de traços.

  4. *[EP-02]* Criar o repositório Git com a estrutura de diretórios em Arquitetura Hexagonal (`/core`, `/ports`, `/adapters`, `/sim-ns3`, `/analysis`).

  5. *[EP-03]* Configurar o template oficial da **SBC** no LaTeX e redigir o esqueleto do Relatório Parcial (Seções 1 e 2: Introdução contextualizada e Definição do Problema).

* **Entregável da Sprint:** Simulador compilado e executando; template LaTeX SBC estruturado; repositório configurado.

#### **Sprint 2 (30/11/2026 a 07/12/2026)**

* **Objetivo da Sprint:** Consolidar a metodologia de avaliação experimental de LoRaWAN e redigir, revisar e fechar o **Relatório Parcial de 10 páginas (Marco de 08/12/2026)**.

* **Backlog da Sprint:**

  1. *[EP-02]* Especificar formalmente os contratos de dados (CT-001 para cenários em YAML/JSON e CT-003 para saída de métricas em CSV).

  2. *[EP-03]* Redigir a Seção 3 da Proposta: Levantamento do estado da arte e discussão comparativa das soluções LoRaWAN (mecanismos de alocação de Spreading Factor, classes A/B/C e modelos de canal).

  3. *[EP-03]* Redigir a Seção 4 da Proposta: Planejamento detalhado da avaliação de desempenho (cenário fatorial, variáveis independentes e dependentes, métricas HB/LB segundo Raj Jain).

  4. *[EP-03]* Diagramar as figuras conceituais e a arquitetura hexagonal da solução no formato SBC.

  5. *[EP-03]* Revisão textual, bibliográfica e contagem rigorosa de páginas: **exatamente 10 páginas**.

* **Entregável da Sprint:** **PDF do Relatório Parcial (10 páginas SBC) submetido em 08/12/2026**.

#### **FASE 2: DESENVOLVIMENTO, SIMULAÇÃO E RELATÓRIO FINAL (08/12/2026 a 25/01/2027)**

#### **Sprint 3 (08/12/2026 a 14/12/2026)**

* **Objetivo da Sprint:** Implementar o núcleo de simulação em C++ das extensões de rádio e do mecanismo de métricas do LoRaWAN no ns-3.

* **Backlog da Sprint:**

  1. *[EP-04]* Implementar classes de domínio em C++ seguindo SOLID: `DutyCycleEnforcer` como camada de instrumentação e configuração do controle regulatório nativo do módulo (1% por sub-banda, trace `CannotSendBecauseDutyCycle`), com opção de desabilitá-lo para o experimento E-DC.

  2. *[EP-04]* Construir a interface `ISpreadingFactorAllocationStrategy` (OCP) com as implementações `RANDOM`, `DISTANCE`, `ADR` e `FIXED_SF12` (degenerado), encapsulando `SetSpreadingFactorsGivenDistribution`, `SetSpreadingFactorsUp` e `AdrComponent`.

  3. *[EP-04]* Instrumentar a subcamada de rastreamento de eventos PHY/MAC para exportar colisões por co-canal, perdas por sensibilidade e chegadas bem-sucedidas no Gateway via callbacks do ns-3.

* **Entregável da Sprint:** Binário C++ do ns-3 recebendo parâmetros via linha de comando e gerando registros em formato CSV limpo.

#### **Sprint 4 (15/12/2026 a 21/12/2026)**

* **Objetivo da Sprint:** Implementar a plataforma de orquestração e análise em Python utilizando Arquitetura Hexagonal e Clean Code.

* **Backlog da Sprint:**

  1. *[EP-04]* Implementar as portas e adaptadores em Python: `SubprocessNs3Adapter` (para invocar as execuções do simulador sem acoplamento) e `FileSystemResultsAdapter`.

  2. *[EP-04]* Criar o serviço de domínio `ExperimentOrchestrator` responsável por ler os arquivos de configuração do cenário (YAML/JSON) e gerenciar a fila de simulações.

  3. *[EP-04]* Implementar testes unitários em `pytest` garantindo que os contratos de dados (CT-001 e CT-003) sejam validados antes e depois de cada simulação.

* **Entregável da Sprint:** Script Python orquestrador executando uma simulação teste do ns-3 de ponta a ponta e persistindo o log com metadados.

#### **Sprint 5 (22/12/2026 a 28/12/2026)**

* **Objetivo da Sprint:** Calibrar os cenários de simulação, remover o período transitório (*warm-up*) e validar as condições iniciais (Capítulo 24 de Raj Jain).

* **Backlog da Sprint:**

  1. *[EP-05]* Configurar a topologia experimental base: 1 Gateway central, raio de 2 km (6 km no experimento E-R), EU868 com 3 canais, payload de 20 bytes e modelo de perda de percurso log-normal.

  2. *[EP-05]* Executar testes preliminares de tráfego e os testes degenerados (SF12 fixo, 1 nó, 5 nós a 100 m) para verificar a duração mínima de simulação (alvo: 10 min de warm-up + ≥ 1 h de medição).

  3. *[EP-05]* Implementar no pipeline Python o truncamento dos 10 minutos iniciais (*warm-up period deletion*), garantindo que apenas métricas em regime permanente (*steady-state*) sejam coletadas.

* **Entregável da Sprint:** Cenário base validado tecnicamente, sem erros de inicialização e pronto para execuções massivas.

#### **Sprint 6 (29/12/2026 a 04/01/2027)**

* **Objetivo da Sprint:** Executar as campanhas experimentais com variação controlada de fatores e controle rigoroso de aleatoriedade (Capítulo 26 de Raj Jain).

* **Backlog da Sprint:**

  1. *[EP-05]* Automatizar a matriz experimental (ADR-002, `configs/campaigns/main_factorial.yaml`):

     * Fator A: Densidade de dispositivos (100, 250, 500, 1000, 2000 nós).

     * Fator B: Estratégia de Fator de Espalhamento (`RANDOM`, `DISTANCE`, `ADR`).

     * Fator C: Período de envio (60 s e 600 s).

     * Complementares: E-DC (duty cycle on/off, ADR, 60 s) e E-R (raio de 6 km, DISTANCE/ADR, 600 s).

  2. *[EP-05]* Configurar o pipeline para executar **30 replicações independentes** por ponto (45 pontos, 1350 execuções), iterando `RngRun = 1..30` e fixando `RngSeed = 1`.

  3. *[EP-05]* Monitorar e consolidar os arquivos brutos de saída em diretório protegido contra sobrescrita acidental.

* **Entregável da Sprint:** Base completa de dados brutos consolidados para todos os cenários experimentais.

#### **Sprint 7 (05/01/2027 a 11/01/2027)**

* **Objetivo da Sprint:** Processamento analítico, agregação estatística e inferência sobre as métricas coletadas (Capítulos 12 e 13 de Raj Jain).

* **Backlog da Sprint:**

  1. *[EP-06]* Implementar no domínio Python o cálculo estatístico das métricas:

     * **HB (*Higher is Better*):** Taxa de Entrega de Pacotes (PDR) e Vazão Global (*Throughput*).

     * **LB (*Lower is Better*):** Atraso fim a fim, Energia gasta por pacote entregue com sucesso, Taxa de colisão e Descartes por duty cycle.

     * **Equidade:** Jain's Fairness Index (JFI) do PDR por nó, estratificado por distância ao gateway.

  2. *[EP-06]* Computar média amostral, variância e **intervalos de confiança de 95%** para todas as métricas em cada nível fatorial.

  3. *[EP-06]* Aplicar o **teste \\(t\\) pareado** (mesmo `RngRun`, α = 0,05) para comparar o ganho do ADR frente à alocação aleatória (`RANDOM`) de SF (H2), e duty cycle on × off (H3).

* **Entregável da Sprint:** Módulo Python gerando relatórios estatísticos tabulados e consolidados com significância matemática comprovada.

#### **Sprint 8 (12/01/2027 a 18/01/2027)**

* **Objetivo da Sprint:** Construção visual dos gráficos científicos e redação da seção de Avaliação Experimental no padrão SBC (Capítulo 10 de Raj Jain).

* **Backlog da Sprint:**

  1. *[EP-06]* Gerar os gráficos de publicação (`matplotlib`/`seaborn` formatados para escala cinza/alto contraste e vetores PDF):

     * Curva PDR vs. Densidade de Nós (com barras de erro representando o intervalo de confiança de 95%).

     * Gráfico de Colisões vs. Fator de Espalhamento (SF7 a SF12).

     * Distribuição do consumo energético por nó em função da distância ao Gateway.

  2. *[EP-07]* Incorporar os gráficos e tabelas ao documento LaTeX no padrão SBC.

  3. *[EP-07]* Redigir a Seção 5 do relatório: Análise detalhada dos resultados experimentais, confrontando as hipóteses formuladas no relatório parcial com as evidências empíricas obtidas.

* **Entregável da Sprint:** Seção de resultados experimentais completamente escrita e ilustrada com figuras de rigor científico.

#### **Sprint 9 (19/01/2027 a 25/01/2027)**

* **Objetivo da Sprint:** Redação da conclusão, revisão cruzada, ajuste de formatação e fechamento do **Relatório Final de 14 páginas (Marco de 25/01/2027)**.

* **Backlog da Sprint:**

  1. *[EP-07]* Redigir a Seção 6 (Conclusão e Trabalhos Futuros), sintetizando as contribuições e limitações observadas na rede LoRaWAN sob interferência.

  2. *[EP-07]* Revisar todas as seções originárias da proposta parcial, atualizando-as com os aprendizados obtidos na fase experimental.

  3. *[EP-07]* Auditoria formal das restrições da fonte `trcsf26-2v1.pdf`:

     * Contagem exata de páginas: **rigorosamente 14 páginas** no template SBC.

     * Qualidade das referências bibliográficas (normas e consistência).

  4. *[EP-07]* Congelar a versão final do código no repositório Git com tag `v1.0-final`, acompanhada do arquivo `README.md` com instruções reprodutíveis de execução.

* **Entregável da Sprint:** **PDF do Relatório Final (14 páginas SBC) submetido em 25/01/2027** e repositório finalizado.

### **4. Quadro Resumo de Rastreabilidade e Marcos**

| Semana / Sprint | Período | Foco Principal | Marco / Entregável |
| :---: | :---: | :--- | :--- |
| **Sprint 1** | 23/11 a 29/11/2026 | Build do ns-3, módulo LoRaWAN e estrutura SBC | Ambiente operacional e rascunho LaTeX |
| **Sprint 2** | 30/11 a 07/12/2026 | Metodologia, proposta e fechamento textual | 🏁 **Relatório Parcial (10 págs SBC) em 08/12/2026** |
| **Sprint 3** | 08/12 a 14/12/2026 | Extensões C++ (SOLID/Clean Code) e tracing | Módulo C++ instrumentado |
| **Sprint 4** | 15/12 a 21/12/2026 | Arquitetura Hexagonal em Python e testes | Orquestrador automatizado |
| **Sprint 5** | 22/12 a 28/12/2026 | Calibração de cenários e regime permanente | Validação da fase transitória (*warm-up*) |
| **Sprint 6** | 29/12 a 04/01/2027 | Execução de campanhas fatoriais massivas | Base de dados de 30+ replicações |
| **Sprint 7** | 05/01 a 11/01/2027 | Estatística de Raj Jain (Intervalos de confiança) | Tabelas consolidadas com teste \\(t\\) |
| **Sprint 8** | 12/01 a 18/01/2027 | Gráficos científicos e escrita dos resultados | Seção experimental concluída |
| **Sprint 9** | 19/01 a 25/01/2027 | Revisão geral, conclusões e validação SBC | 🏁 **Relatório Final (14 págs SBC) em 25/01/2027** |
