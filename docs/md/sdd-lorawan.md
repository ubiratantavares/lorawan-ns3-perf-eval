# SDD — Avaliação de Desempenho de Redes LoRaWAN no ns-3

- **Versão:** 1.0 (Sprint 2, 2026-12)

- **Fontes:** `docs/md/plan.md`, `docs/md/backlog.md`, `docs/adr/001`, `docs/adr/002`

- **Convenções:** RF (Requisito Funcional), RNF (Não Funcional), DOM (Domínio), CT (Contrato), CA (Critério de Aceitação), ADR (Decisão Arquitetural)

## 1. Escopo

Avaliar, por simulação de eventos discretos no ns-3.48 com o módulo `lorawan` 0.3.7, o impacto da densidade de dispositivos, da estratégia de alocação de SF, da carga oferecida e do duty cycle
regulatório sobre PDR, vazão, atraso, energia, colisões e equidade em uma célula LoRaWAN Classe A (EU868). Classes B/C e múltiplos gateways estão fora do escopo das campanhas.

## 2. Requisitos Funcionais

| ID | Requisito | Origem |
| :--- | :--- | :--- |
| RF-001 | Configurar 1..N gateways e N dispositivos distribuídos uniformemente em disco de raio 0,1 a 10 km. | plan §3.2 |
| RF-002 | Parametrizar a camada física: SF7–SF12, BW 125 kHz (v1.0), 3 canais EU868, potência de transmissão. | plan §3.2 |
| RF-003 | Executar com `RngSeed`/`RngRun` explícitos, garantindo reprodutibilidade. | plan §3.2 |
| RF-004 | Registrar transmissões e os desfechos SUCCESS, COLLISION, UNDER_SENSITIVITY, NO_MORE_RECEIVERS, GW_TX_BUSY e DUTY_CYCLE_BLOCKED. | plan §3.2, Tarefa 2.1 |
| RF-005 | Exportar cada execução para `data/raw/<campaign_id>/<scenario_id>/` com `metadata.json` (CT-002), `packets.csv` e `nodes.csv` (CT-003). | plan §3.2 |
| RF-006 | Suportar as estratégias de SF `RANDOM`, `DISTANCE`, `ADR` e `FIXED_SF12` via `ISpreadingFactorAllocationStrategy`. | ADR-002 |
| RF-007 | Habilitar/desabilitar o duty cycle regulatório (1% por sub-banda) por cenário. | ADR-002 |
| RF-008 | Expandir campanhas (`configs/campaigns/*.yaml`) em instâncias CT-001 e executá-las em paralelo. | backlog S4/S6 |
| RF-009 | Descartar o warm-up, calcular métricas por execução, IC 95% por ponto e teste t pareado. | ADR-002 |

## 3. Requisitos Não Funcionais

| ID | Requisito |
| :--- | :--- |
| RNF-001 | Reprodutibilidade: mesmo CT-001 (incluindo seed/run) e mesmo commit produzem `packets.csv` byte-idêntico. |
| RNF-002 | Desempenho: a campanha completa (1350 execuções) deve ser paralelizável em processos independentes; o tempo por execução é medido na Sprint 5. |
| RNF-003 | Qualidade Python: `ruff` sem erros, `mypy` sem erros em `src/`, cobertura ≥ 80% em `src/core`. |
| RNF-004 | Qualidade C++: compilação sem warnings no perfil `optimized`, estilo `.clang-format` do ns-3, funções < 20 linhas. |
| RNF-005 | Portabilidade: Ubuntu 22.04/24.04, ns-3.48, Python ≥ 3.14 (ADR-001). |
| RNF-006 | Rastreabilidade: artefatos e commits referenciam IDs RF/CT/CA/ADR. |
| RNF-007 | Isolamento: o domínio (`src/core`) não importa `os`, `subprocess` nem bibliotecas de E/S. |

## 4. Modelo de Domínio

- **Entidades:** `EndDeviceNode` (id, posição, SF inicial/final, energia), `GatewayNode` (id, posição, demoduladores), `NetworkServer` (deduplicação, ADR), `SimulationRun` (cenário CT-001 + metadados CT-002 + amostras CT-003).
- **Objetos de Valor:** `LoraCoordinates`, `SpreadingFactor` (SF7..SF12), `BandwidthHz`, `TransmissionPowerDbm`, `PacketStatus` (6 valores), `SfStrategy` (4 valores), `ConfidenceInterval`.
- **Agregado:** `LoraCellAggregate` (gateways e dispositivos de uma célula).
- **Serviços de Domínio:** `MetricsCalculator` (PDR, vazão, atraso, energia, colisão, duty cycle, JFI) e `StatisticalEngine` (média, variância, IC 95%, teste t pareado).

## 5. Contratos de Dados

| ID | Artefato | Esquema | Produtor → Consumidor |
| :--- | :--- | :--- | :--- |
| CT-001 | Cenário (YAML/JSON) | `configs/schemas/ct-001-scenario.schema.json` | Orquestrador → ns-3 (via CLI) |
| CT-002 | `metadata.json` | `configs/schemas/ct-002-metadata.schema.json` | `SubprocessNs3Adapter` → repositório |
| CT-003 | `packets.csv`, `nodes.csv` | `configs/schemas/ct-003-metrics.schema.json` | ns-3 (`MetricsTracker`) → análise |

Mapeamento `PhyPacketOutcome` → `status`: RECEIVED→SUCCESS, INTERFERED→COLLISION, UNDER_SENSITIVITY→UNDER_SENSITIVITY, NO_MORE_RECEIVERS→NO_MORE_RECEIVERS, LOST_BECAUSE_TX→GW_TX_BUSY; 
trace `CannotSendBecauseDutyCycle`→ DUTY_CYCLE_BLOCKED (`gateway_id = -1`).

## 6. Critérios de Aceitação

| ID | Critério | Verificação |
| :--- | :--- | :--- |
| CA-001 | Cenário que viola o CT-001 ou com `warmup_seconds ≥ duration_seconds` é rejeitado antes de executar o ns-3. | pytest (integração) |
| CA-002 | Duas execuções com o mesmo CT-001 geram `packets.csv` com SHA-256 idêntico. | pytest (integração, Sprint 4) |
| CA-003 | Teste degenerado D-SINGLE resulta em PDR ≥ 0,99. | Sprint 5 |
| CA-004 | Conservação: `packets_generated = transmitidos + DUTY_CYCLE_BLOCKED` e, por gateway, `transmitidos = Σ desfechos PHY`. | pytest (unitário) |
| CA-005 | Diretório de execução existente nunca é sobrescrito (erro explícito). | pytest (unitário) |
| CA-006 | Linhas com `timestamp_s < warmup_seconds` não entram no cálculo das métricas. | pytest (unitário) |
| CA-007 | IC 95% calculado pelo `StatisticalEngine` confere com `scipy.stats.t.interval` (tolerância 1e-9). | pytest (unitário) |

## 7. Matriz de Rastreabilidade

| RF | CT | CA | Sprint |
| :--- | :--- | :--- | :--- |
| RF-001, RF-002, RF-006, RF-007 | CT-001 | CA-001 | S2 (spec), S3 (C++) |
| RF-003 | CT-001, CT-002 | CA-002 | S3, S4 |
| RF-004 | CT-003 | CA-004 | S3 |
| RF-005 | CT-002, CT-003 | CA-005 | S4 |
| RF-008 | CT-001 | CA-001 | S4, S6 |
| RF-009 | CT-003 | CA-006, CA-007 | S5, S7 |
