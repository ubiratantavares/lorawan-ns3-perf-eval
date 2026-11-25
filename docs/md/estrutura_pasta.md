Aqui está o esqueleto completo da estrutura de pastas para o projeto **`lorawan-ns3-perf-eval`**, concebido sob os princípios de **Arquitetura Hexagonal (Ports & Adapters)**, **Clean Code**, **SOLID** e **Specification-Driven Development (SDD)**, com separação estrita entre o núcleo de simulação em **C++ (ns-3)** e a plataforma de orquestração e análise estatística em **Python**:

```text
lorawan-ns3-perf-eval/
│
├── .gitignore                          # Ignora binários ns-3, saídas pesadas (.pcap, logs) e venv
├── README.md                           # Visão geral, requisitos, build e instruções de execução
├── LICENSE                             # Licença do projeto (ex.: MIT / GPLv2 compatível com ns-3)
├── pyproject.toml / requirements.txt   # Dependências Python (numpy, scipy, pandas, matplotlib, pytest, pyyaml)
├── CMakeLists.txt                      # Script de integração ou compilação C++ externa/ns-3
│
├── docs/                               # Governança, SDD e Documentação Acadêmica (SBC)
│   ├── sdd-lorawan.md                  # Especificação Técnica Central (Single Source of Truth)
│   ├── adr/                            # Architecture Decision Records
│   │   ├── 001-escolha-ns3-lorawan.md
│   │   ├── 002-arquitetura-hexagonal-python.md
│   │   └── 003-estrategia-alocacao-adr.md
│   └── sbc-papers/                     # Documentos LaTeX no padrão da SBC
│       ├── proposta-parcial/           # Relatório Parcial (10 páginas - Entrega 08/12/2026)
│       │   ├── sbc-template.sty
│       │   ├── proposta.tex
│       │   ├── referencias.bib
│       │   └── figures/
│       └── relatorio-final/            # Relatório Final (14 páginas - Entrega 25/01/2027)
│           ├── sbc-template.sty
│           ├── relatorio_final.tex
│           ├── referencias.bib
│           └── figures/
│
├── sim-ns3/                            # Núcleo de Simulação em C++ (Extensões e Módulos ns-3)
│   ├── CMakeLists.txt
│   ├── scenarios/                      # Ponto de entrada das simulações (executáveis ns-3)
│   │   └── lora-urban-scenario.cc      # Script principal que orquestra nós, canal e callbacks
│   ├── model/                          # Classes de Domínio e Extensões do Protocolo (SOLID / C++)
│   │   ├── lora-duty-cycle-manager.h   # Controle regulatório de tempo no ar (1%)
│   │   ├── lora-duty-cycle-manager.cc
│   │   ├── spreading-factor-strategy.h # Interface abstrata (OCP/DIP) para alocação de SF
│   │   ├── spreading-factor-strategy.cc
│   │   ├── lora-adr-custom.h           # Algoritmo de alocação dinâmica (ADR estendido)
│   │   └── lora-adr-custom.cc
│   └── helper/                         # Utilitários de instrumentação e métricas
│       ├── lora-metrics-tracker.h      # Callbacks de camada PHY/MAC para tracing desacoplado
│       └── lora-metrics-tracker.cc
│
├── src/                                # Plataforma em Python (Arquitetura Hexagonal)
│   ├── core/                           # Inside: Domínio e Regras de Negócio Puras
│   │   ├── domain/
│   │   │   ├── entities.py             # SimulationRun, EndDevice, Gateway, MetricSample
│   │   │   ├── value_objects.py        # SpreadingFactor, FrequencyHz, Coordinates, SnrDb
│   │   │   └── enums.py                # PacketStatus (SUCCESS, COLLISION, UNDER_SENSITIVITY)
│   │   └── services/
│   │       ├── metrics_calculator.py   # Cálculos de PDR, Throughput, Jitter e Energia/Bit
│   │       └── statistical_engine.py   # Raj Jain: Média, Variância, IC 95%, Teste t pareado
│   │
│   ├── ports/                          # Interfaces / Contratos Abstratos (DIP)
│   │   ├── driving/                    # Portas de Entrada (Casos de Uso)
│   │   │   ├── orchestrator_port.py    # Interface para execução de campanhas
│   │   │   └── analysis_port.py        # Interface para processamento e exportação
│   │   └── driven/                     # Portas de Saída (Infraestrutura)
│   │       ├── simulation_runner_port.py  # Interface para disparar o motor ns-3
│   │       └── results_repository_port.py # Interface para persistência de dados
│   │
│   └── adapters/                       # Outside: Adaptadores Concretos (Infraestrutura)
│       ├── driving/
│       │   └── cli/
│       │       └── main.py             # CLI para executar campanhas e processar resultados
│       └── driven/
│           ├── ns3_subprocess_adapter.py    # Executa binário C++ via subprocess sem acoplamento
│           ├── filesystem_repo_adapter.py   # Leitura/escrita de CSV, JSON e YAML
│           └── sbc_figure_generator.py      # Matplotlib/Seaborn formatado para padrão SBC
│
├── configs/                            # Contratos de Dados de Entrada (CT-001)
│   ├── default_scenario.yaml           # Topologia base, raio de cobertura, canal e antenas
│   └── campaigns/                      # Matrizes de experimentos fatoriais
│       ├── density_sweep.yaml          # Variação de densidade de nós (100 a 2000 nós)
│       └── traffic_sweep.yaml          # Variação de intervalos de transmissão
│
├── data/                               # Armazenamento Isolado de Resultados (CT-002 e CT-003)
│   ├── raw/                            # Dados brutos das simulações (protegidos contra sobrescrita)
│   │   └── .gitkeep
│   └── processed/                      # Tabelas agregadas e métricas com intervalos de confiança
│       └── .gitkeep
│
└── tests/                              # Pirâmide de Testes Automatizados (pytest)
    ├── unit/
    │   ├── test_metrics_calculator.py  # Validação matemática das fórmulas de PDR/Vazão
    │   └── test_statistical_engine.py  # Validação do teste t pareado e intervalos de confiança
    └── integration/
        ├── test_config_contract.py     # Validação dos esquemas YAML/JSON (CT-001)
        └── test_output_contract.py     # Validação do formato do CSV emitido pelo ns-3 (CT-003)
```

### **Destaques das Divisões Arquiteturais**

1. **Isolamento C++ (`sim-ns3/`):**

   * Contém apenas o código que roda dentro do ciclo de eventos discretos do ns-3.

   * Não possui dependência direta de bibliotecas externas de análise gráfica, exportando eventos limpos em streams e arquivos estruturados via `lora-metrics-tracker`.

2. **Núcleo Hexagonal Python (`src/`):**

   * **`core/`**: Não importa nada de `os`, `sys` ou `subprocess`. Contém apenas a lógica de negócio (cálculo de PDR, equações de energia e os testes estatísticos de Raj Jain).

   * **`ports/`**: Define os contratos abstratos em Python (`typing.Protocol` ou `abc.ABC`).

   * **`adapters/`**: Isola o sistema operacional. Se amanhã o ns-3 rodar via Docker ou em um cluster HPC, apenas o `ns3_subprocess_adapter.py` é alterado.

3. **Governança e Rastreabilidade (`docs/` e `configs/`):**

   * Mantém os templates e arquivos LaTeX dos relatórios parcial (10 p.) e final (14 p.) no mesmo ciclo de vida do código, assegurando que as figuras geradas em `adapters/driven/sbc_figure_generator.py` sejam exportadas diretamente para a pasta de figuras dos relatórios.
   
