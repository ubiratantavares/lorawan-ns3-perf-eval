# **Sprint 2 (30/11/2026 a 07/12/2026)**

* **Objetivo da Sprint:** Consolidar a metodologia de avaliação experimental de LoRaWAN e redigir, revisar e fechar o **Relatório Parcial de 10 páginas (Marco de 08/12/2026)**.

* **Backlog da Sprint:**

1. *[EP-02]* Especificar formalmente os contratos de dados (CT-001 para cenários em YAML/JSON, CT-002 para metadados de execução e CT-003 para saída de métricas em CSV) 
no documento central `docs/sdd-lorawan.md`.

2. *[EP-03]* Redigir a Seção 3 da Proposta: Levantamento do estado da arte e discussão comparativa das soluções LoRaWAN (mecanismos de alocação de Spreading Factor, ADR, ortogonalidade 
imperfeita e simulação no ns-3).

3. *[EP-03]* Redigir a Seção 4 da Proposta: Planejamento detalhado da avaliação de desempenho (desenho fatorial do ADR-002, variáveis independentes e dependentes, métricas HB/LB segundo Raj Jain).

4. *[EP-03]* Diagramar as figuras conceituais (topologia LoRaWAN) e a arquitetura hexagonal da solução no formato SBC.

5. *[EP-03]* Revisão textual, bibliográfica e contagem rigorosa de páginas: **exatamente 10 páginas**.

* **Entregável da Sprint:** **PDF do Relatório Parcial (10 páginas SBC) submetido em 08/12/2026**, acompanhado da especificação SDD versionada no repositório.

* **Insumos Herdados da Sprint 1:**

  * `docs/adr/001-versao-ns3-e-modulo-lorawan.md` — ns-3.48 + lorawan 0.3.7.

  * `docs/adr/002-desenho-experimental.md` — fatorial 5 × 3 × 2 + E-DC + E-R (1350 execuções).

  * `configs/campaigns/main_factorial.yaml` — matriz experimental preliminar.

  * `docs/sbc-papers/proposta-parcial/proposta.tex` — Seções 1 e 2 redigidas, QP/H alinhadas ao ADR-002.

## [EP-02] - Tarefa 2.1: Especificar formalmente os contratos de dados (CT-001, CT-002 e CT-003) no documento SDD.

# Especificação Técnica de Execução: Documento SDD e Contratos de Dados

* **Identificador no Backlog:** `[EP-02] - Tarefa 2.1`

* **Épico Vinculado:** EP-02 — Governança SDD e Especificação Técnica

* **Sprint:** Sprint 2 (30/11/2026 a 07/12/2026)

* **Status:** Pronto para Execução

* **Objetivo:** Criar a fonte única de verdade técnica do projeto (`docs/sdd-lorawan.md`), formalizando requisitos (RF/RNF), modelo de domínio (DOM), critérios de aceitação (CA) e 
os três contratos de dados que desacoplam o orquestrador Python do motor ns-3: 

	**CT-001** (cenário), 

	**CT-002** (metadados de execução) e 

	**CT-003** (métricas brutas). Os contratos devem ser materializados em **JSON Schema (draft 2020-12)** e validados automaticamente por `pytest`.

## 1. Fundamentação e Decisões de Projeto

O `plan.md` (§3.4) define os contratos em alto nível. A Tarefa 2.1 os refina considerando três fatos levantados no código do módulo `lorawan` 0.3.7 e no ADR-002:

| Fato Técnico | Consequência no Contrato |
| :--- | :--- |
| O `LoraPacketTracker` classifica cada recepção em `RECEIVED`, `INTERFERED`, `NO_MORE_RECEIVERS`, `UNDER_SENSITIVITY` e `LOST_BECAUSE_TX` (`helper/lora-packet-tracker.h`). | O campo `status` do CT-003 passa a ter **seis** valores (os cinco mapeados + `DUTY_CYCLE_BLOCKED`), e não apenas três. |
| O duty cycle é nativo e emite o trace `CannotSendBecauseDutyCycle` (`model/lorawan-mac.h`). | Descartes por duty cycle são registrados no CT-003 com `gateway_id = -1`. |
| As métricas do ADR-002 exigem atraso, energia e JFI estratificado por distância. | O CT-003 ganha `packet_id`, `distance_m` e `tx_power_dbm`, e um arquivo complementar por nó (`nodes.csv`) com energia consumida. |

**Mapeamento de status (PHY → CT-003):**

| `PhyPacketOutcome` (ns-3) | `status` (CT-003) | Interpretação |
| :--- | :--- | :--- |
| `RECEIVED` | `SUCCESS` | Pacote demodulado com sucesso no gateway |
| `INTERFERED` | `COLLISION` | Destruído por interferência (mesmo SF ou inter-SF) |
| `UNDER_SENSITIVITY` | `UNDER_SENSITIVITY` | Potência recebida abaixo da sensibilidade do SF |
| `NO_MORE_RECEIVERS` | `NO_MORE_RECEIVERS` | Todos os demoduladores paralelos do gateway ocupados |
| `LOST_BECAUSE_TX` | `GW_TX_BUSY` | Gateway transmitindo downlink no instante da recepção |
| *(trace MAC)* `CannotSendBecauseDutyCycle` | `DUTY_CYCLE_BLOCKED` | Pacote gerado, mas não transmitido pelo nó |

## 2. Passo a Passo de Execução

Execute os comandos a partir da raiz do projeto:

```bash
cd /home/bira/github/projetos/lorawan-ns3-perf-eval
source .venv/bin/activate
```

### Passo 1: Instalação da Dependência de Validação de Esquemas

O orquestrador validará cenários em tempo de execução (antes de disparar o ns-3); por isso `jsonschema` é dependência de runtime. Os stubs de tipos atendem ao `mypy`:

```bash
uv add jsonschema
uv add --dev types-jsonschema types-PyYAML
uv sync
```

### Passo 2: Criação da Estrutura de Diretórios dos Contratos

```bash
mkdir -p configs/schemas tests/fixtures
```

### Passo 3: Esquema do CT-001 — Cenário de Simulação (`configs/schemas/ct-001-scenario.schema.json`)

Cada instância do CT-001 descreve **uma única execução** (um ponto experimental × uma replicação). Campanhas (`configs/campaigns/*.yaml`) são expandidas pelo orquestrador em instâncias CT-001.

```bash
cat << 'EOF' > configs/schemas/ct-001-scenario.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ct-001-scenario.schema.json",
  "title": "CT-001 - Cenario de Simulacao LoRaWAN",
  "description": "Parametros de uma unica execucao do ns-3 (ponto experimental x replicacao).",
  "type": "object",
  "additionalProperties": false,
  "required": ["contract_version", "scenario_id", "duration_seconds", "warmup_seconds",
               "topology", "lora_settings", "traffic", "stochastic"],
  "properties": {
    "contract_version": { "const": "1.0" },
    "scenario_id": { "type": "string", "pattern": "^[a-z0-9_-]+$" },
    "duration_seconds": { "type": "number", "exclusiveMinimum": 0 },
    "warmup_seconds": { "type": "number", "minimum": 0 },
    "topology": {
      "type": "object",
      "additionalProperties": false,
      "required": ["radius_m", "n_gateways", "n_devices"],
      "properties": {
        "radius_m": { "type": "number", "minimum": 100, "maximum": 10000 },
        "n_gateways": { "type": "integer", "minimum": 1 },
        "n_devices": { "type": "integer", "minimum": 1 }
      }
    },
    "lora_settings": {
      "type": "object",
      "additionalProperties": false,
      "required": ["region", "n_channels", "sf_strategy", "duty_cycle_enabled"],
      "properties": {
        "region": { "enum": ["EU868"] },
        "n_channels": { "type": "integer", "minimum": 1, "maximum": 16 },
        "sf_strategy": { "enum": ["RANDOM", "DISTANCE", "ADR", "FIXED_SF12"] },
        "duty_cycle_enabled": { "type": "boolean" },
        "realistic_channel": { "type": "boolean", "default": false }
      }
    },
    "traffic": {
      "type": "object",
      "additionalProperties": false,
      "required": ["app_period_s", "payload_bytes"],
      "properties": {
        "app_period_s": { "type": "number", "exclusiveMinimum": 0 },
        "payload_bytes": { "type": "integer", "minimum": 1, "maximum": 222 }
      }
    },
    "stochastic": {
      "type": "object",
      "additionalProperties": false,
      "required": ["rng_seed", "rng_run"],
      "properties": {
        "rng_seed": { "type": "integer", "minimum": 1 },
        "rng_run": { "type": "integer", "minimum": 1 }
      }
    }
  }
}
EOF
```

* **Nota:** a restrição cruzada `warmup_seconds < duration_seconds` não é expressável em JSON Schema puro; ela é verificada pelo critério de aceitação **CA-001** 
(teste dedicado no Passo 8 e, na Sprint 4, no domínio Python).

### Passo 4: Instância de Referência do CT-001 (`configs/default_scenario.yaml`)

```bash
cat << 'EOF' > configs/default_scenario.yaml
# Instancia de referencia do CT-001 (cenario base do ADR-002)
contract_version: "1.0"
scenario_id: base_n100_adr_p600_r01
duration_seconds: 4200        # 600 s de warm-up + 3600 s de medicao
warmup_seconds: 600
topology:
  radius_m: 2000
  n_gateways: 1
  n_devices: 100
lora_settings:
  region: EU868
  n_channels: 3
  sf_strategy: ADR
  duty_cycle_enabled: true
  realistic_channel: false
traffic:
  app_period_s: 600
  payload_bytes: 20
stochastic:
  rng_seed: 1
  rng_run: 1
EOF
```

### Passo 5: Alinhamento da Campanha ao CT-001 (`configs/campaigns/main_factorial.yaml`)

A versão preliminar da matriz (Sprint 1) agrupava `payload_bytes` em `lora_settings`. Reescreva-a para que `base_scenario` seja um CT-001 parcial e cada fator aponte explicitamente 
para o caminho que preenche:

```bash
cat << 'EOF' > configs/campaigns/main_factorial.yaml
# Matriz experimental principal (ADR-002). Cada combinacao + rng_run gera uma instancia CT-001.
campaign_id: main_factorial
contract_version: "1.0"

base_scenario:                  # CT-001 parcial (campos comuns a todos os pontos)
  duration_seconds: 4200
  warmup_seconds: 600
  topology: {radius_m: 2000, n_gateways: 1}
  lora_settings: {region: EU868, n_channels: 3, duty_cycle_enabled: true, realistic_channel: false}
  traffic: {payload_bytes: 20}

stochastic:
  rng_seed: 1
  rng_runs: {first: 1, last: 30}

factors:                        # fatorial completo 5 x 3 x 2 = 30 pontos
  - {name: n_devices,   path: topology.n_devices,       levels: [100, 250, 500, 1000, 2000]}
  - {name: sf_strategy, path: lora_settings.sf_strategy, levels: [RANDOM, DISTANCE, ADR]}
  - {name: app_period_s, path: traffic.app_period_s,    levels: [60, 600]}

complementary:
  - id: E-DC                    # 5 pontos (H3 / QP-03)
    overrides: {lora_settings.sf_strategy: ADR, traffic.app_period_s: 60, lora_settings.duty_cycle_enabled: false}
    vary: [n_devices]
  - id: E-R                     # 10 pontos (sensibilidade ao raio)
    overrides: {topology.radius_m: 6000, traffic.app_period_s: 600}
    vary: [n_devices]
    levels: {sf_strategy: [DISTANCE, ADR]}

degenerate_tests:               # validacao (Jain, cap. 25)
  - {id: D-SF12,   overrides: {topology.n_devices: 100, lora_settings.sf_strategy: FIXED_SF12, traffic.app_period_s: 600}}
  - {id: D-SINGLE, overrides: {topology.n_devices: 1,   lora_settings.sf_strategy: DISTANCE,   traffic.app_period_s: 600}}
  - {id: D-NEAR,   overrides: {topology.n_devices: 5,   lora_settings.sf_strategy: DISTANCE,   traffic.app_period_s: 600, topology.radius_m: 100}}
EOF
```

### Passo 6: Esquema do CT-002 — Metadados de Execução (`configs/schemas/ct-002-metadata.schema.json`)

Gerado pelo adaptador `SubprocessNs3Adapter` ao final de cada execução, como `metadata.json`:

```bash
cat << 'EOF' > configs/schemas/ct-002-metadata.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ct-002-metadata.schema.json",
  "title": "CT-002 - Metadados de Execucao",
  "type": "object",
  "additionalProperties": false,
  "required": ["contract_version", "scenario_id", "campaign_id", "rng_seed", "rng_run",
               "ns3_version", "lorawan_version", "git_commit", "git_dirty",
               "scenario_sha256", "started_at", "finished_at", "wall_clock_s", "exit_code"],
  "properties": {
    "contract_version": { "const": "1.0" },
    "scenario_id": { "type": "string" },
    "campaign_id": { "type": "string" },
    "rng_seed": { "type": "integer", "minimum": 1 },
    "rng_run": { "type": "integer", "minimum": 1 },
    "ns3_version": { "const": "3.48" },
    "lorawan_version": { "const": "0.3.7" },
    "git_commit": { "type": "string", "pattern": "^[0-9a-f]{40}$" },
    "git_dirty": { "type": "boolean" },
    "scenario_sha256": { "type": "string", "pattern": "^[0-9a-f]{64}$" },
    "started_at": { "type": "string", "format": "date-time" },
    "finished_at": { "type": "string", "format": "date-time" },
    "wall_clock_s": { "type": "number", "minimum": 0 },
    "exit_code": { "type": "integer" },
    "host": {
      "type": "object",
      "properties": {
        "os": { "type": "string" },
        "cpu_count": { "type": "integer", "minimum": 1 }
      }
    }
  }
}
EOF
```

### Passo 7: Esquema do CT-003 — Métricas Brutas (`configs/schemas/ct-003-metrics.schema.json`)

O CT-003 é composto por dois arquivos CSV (UTF-8, separador `,`, cabeçalho obrigatório) por execução: **`packets.csv`** (uma linha por par pacote × gateway, ou por bloqueio de duty cycle) 
e **`nodes.csv`** (uma linha por nó). O esquema descreve as colunas no estilo *Table Schema*:

```bash
cat << 'EOF' > configs/schemas/ct-003-metrics.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ct-003-metrics.schema.json",
  "title": "CT-003 - Metricas Brutas de Saida (CSV)",
  "type": "object",
  "properties": {
    "packets_csv": {
      "const": [
        {"name": "timestamp_s",      "type": "number",  "constraints": {"minimum": 0}},
        {"name": "packet_id",        "type": "integer", "constraints": {"minimum": 0}},
        {"name": "node_id",          "type": "integer", "constraints": {"minimum": 0}},
        {"name": "gateway_id",       "type": "integer", "constraints": {"minimum": -1}},
        {"name": "distance_m",       "type": "number",  "constraints": {"minimum": 0}},
        {"name": "channel_hz",       "type": "number"},
        {"name": "spreading_factor", "type": "integer", "constraints": {"minimum": 7, "maximum": 12}},
        {"name": "tx_power_dbm",     "type": "number"},
        {"name": "rssi_dbm",         "type": "number",  "nullable": true},
        {"name": "snr_db",           "type": "number",  "nullable": true},
        {"name": "status",           "type": "string",
         "constraints": {"enum": ["SUCCESS", "COLLISION", "UNDER_SENSITIVITY",
                                  "NO_MORE_RECEIVERS", "GW_TX_BUSY", "DUTY_CYCLE_BLOCKED"]}}
      ]
    },
    "nodes_csv": {
      "const": [
        {"name": "node_id",           "type": "integer", "constraints": {"minimum": 0}},
        {"name": "distance_m",        "type": "number",  "constraints": {"minimum": 0}},
        {"name": "sf_initial",        "type": "integer", "constraints": {"minimum": 7, "maximum": 12}},
        {"name": "sf_final",          "type": "integer", "constraints": {"minimum": 7, "maximum": 12}},
        {"name": "packets_generated", "type": "integer", "constraints": {"minimum": 0}},
        {"name": "energy_j",          "type": "number",  "constraints": {"minimum": 0}}
      ]
    }
  }
}
EOF
```

Crie também uma amostra mínima (fixture) para os testes de contrato da Sprint 4:

```bash
cat << 'EOF' > tests/fixtures/ct003_packets_sample.csv
timestamp_s,packet_id,node_id,gateway_id,distance_m,channel_hz,spreading_factor,tx_power_dbm,rssi_dbm,snr_db,status
612.40,0,3,0,845.2,868100000,7,14,-98.3,6.1,SUCCESS
615.02,1,7,0,1720.9,868300000,10,14,-121.7,-9.4,COLLISION
620.88,2,9,0,1985.0,868500000,12,14,-138.2,-21.0,UNDER_SENSITIVITY
633.10,3,3,-1,845.2,868100000,7,14,,,DUTY_CYCLE_BLOCKED
EOF
```

### Passo 8: Testes de Contrato (`tests/integration/test_config_contract.py`)

```bash
cat << 'EOF' > tests/integration/test_config_contract.py
"""Validacao dos contratos de dados CT-001/CT-002/CT-003 (EP-02, Tarefa 2.1)."""

import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "configs" / "schemas"


def _schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def _default_scenario() -> dict[str, Any]:
    text = (ROOT / "configs" / "default_scenario.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(text)


CT001 = Draft202012Validator(_schema("ct-001-scenario.schema.json"))


@pytest.mark.parametrize(
    "name",
    ["ct-001-scenario.schema.json", "ct-002-metadata.schema.json", "ct-003-metrics.schema.json"],
)
def test_schemas_are_valid_draft_2020_12(name: str) -> None:
    Draft202012Validator.check_schema(_schema(name))


def test_default_scenario_conforms_to_ct001() -> None:
    CT001.validate(_default_scenario())


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("lora_settings", "sf_strategy", "SF_MAGIC"),
        ("topology", "n_devices", 0),
        ("topology", "radius_m", 50),
        ("stochastic", "rng_run", 0),
        ("traffic", "payload_bytes", 300),
    ],
)
def test_invalid_scenarios_are_rejected(section: str, field: str, value: Any) -> None:
    scenario = _default_scenario()
    scenario[section][field] = value
    assert not CT001.is_valid(scenario)


def test_ca001_warmup_shorter_than_duration() -> None:
    scenario = _default_scenario()
    assert scenario["warmup_seconds"] < scenario["duration_seconds"]


def test_ct003_sample_header_matches_schema() -> None:
    expected = [c["name"] for c in _schema("ct-003-metrics.schema.json")["properties"]["packets_csv"]["const"]]
    header = (ROOT / "tests" / "fixtures" / "ct003_packets_sample.csv").read_text(encoding="utf-8").splitlines()[0]
    assert header.split(",") == expected
EOF

uv run pytest -q
```

* **Resultado Esperado:** `12 passed` (1 smoke test + 11 testes de contrato).

### Passo 9: Redação do Documento Central `docs/md/sdd-lorawan.md`

Crie o documento com o conteúdo abaixo. Ele é a referência normativa para as Sprints 3 a 9; qualquer divergência entre código e SDD deve ser resolvida alterando primeiro o SDD 
(e, se for decisão arquitetural, registrando um ADR).

```markdown
# SDD — Avaliação de Desempenho de Redes LoRaWAN no ns-3

- **Versão:** 1.0 (Sprint 2, 2026-12)
- **Fontes:** `docs/md/plan.md`, `docs/md/backlog.md`, `docs/adr/001`, `docs/adr/002`
- **Convenções:** RF (Requisito Funcional), RNF (Não Funcional), DOM (Domínio), CT (Contrato), CA (Critério de Aceitação), ADR (Decisão Arquitetural)

## 1. Escopo

Avaliar, por simulação de eventos discretos no ns-3.48 com o módulo `lorawan` 0.3.7, o impacto da
densidade de dispositivos, da estratégia de alocação de SF, da carga oferecida e do duty cycle
regulatório sobre PDR, vazão, atraso, energia, colisões e equidade em uma célula LoRaWAN Classe A
(EU868). Classes B/C e múltiplos gateways estão fora do escopo das campanhas.

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

Mapeamento `PhyPacketOutcome` → `status`: RECEIVED→SUCCESS, INTERFERED→COLLISION,
UNDER_SENSITIVITY→UNDER_SENSITIVITY, NO_MORE_RECEIVERS→NO_MORE_RECEIVERS,
LOST_BECAUSE_TX→GW_TX_BUSY; trace `CannotSendBecauseDutyCycle`→DUTY_CYCLE_BLOCKED (`gateway_id = -1`).

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
```

Por fim, atualize a seção §3.4 do `plan.md` para remeter ao SDD como fonte normativa (substituindo a lista de colunas do CT-003 pela referência `docs/sdd-lorawan.md §5`).

### Passo 10: Registro e Versionamento no Git

```bash
uv run ruff format .
uv run ruff check . --fix --unsafe-fixes

uv run pytest -q

git add docs/sdd-lorawan.md docs/md/plan.md configs/ tests/ pyproject.toml uv.lock
git commit -m "docs(sdd): especifica RF/RNF/DOM/CA e contratos CT-001/002/003 em JSON Schema (EP-02 Tarefa 2.1)"
```

## 3. Matriz de Verificação e Homologação

| Verificação | Procedimento | Critério de Aceitação |
| :--- | :--- | :--- |
| **Esquemas válidos** | `test_schemas_are_valid_draft_2020_12` | Os três esquemas passam em `check_schema` (draft 2020-12). |
| **Instância de referência** | `test_default_scenario_conforms_to_ct001` | `default_scenario.yaml` valida contra o CT-001. |
| **Rejeição de inválidos** | `test_invalid_scenarios_are_rejected` | Os cinco casos inválidos são rejeitados. |
| **Cabeçalho CT-003** | `test_ct003_sample_header_matches_schema` | Ordem e nomes das colunas idênticos ao esquema. |
| **Campanha alinhada** | Inspeção de `main_factorial.yaml` | Todo `path` de fator existe no CT-001. |
| **SDD completo** | Leitura de `docs/sdd-lorawan.md` | RF-001..009, RNF-001..007, CA-001..007 e matriz de rastreabilidade presentes. |

## 4. Definição de Pronto (*Definition of Done - DoD*)

A atividade **`[EP-02] - Tarefa 2.1`** é considerada **Concluída (Done)** quando:

1. [X] `docs/sdd-lorawan.md` estiver versionado com requisitos, domínio, contratos, critérios de aceitação e matriz de rastreabilidade.
2. [X] Os esquemas CT-001, CT-002 e CT-003 estiverem em `configs/schemas/` e forem válidos em JSON Schema draft 2020-12.
3. [X] `configs/default_scenario.yaml` e `configs/campaigns/main_factorial.yaml` estiverem alinhados ao CT-001 v1.0.
4. [X] `uv run pytest -q` retornar `12 passed`.
5. [X] O `plan.md` §3.4 remeter ao SDD, e o commit estiver registrado, liberando a redação da Metodologia (Tarefa 2.3) com contratos estáveis.

## [EP-03] - Tarefa 2.2: Redigir a Seção 3 da Proposta (Levantamento do estado da arte e discussão comparativa das soluções).

# Especificação Técnica de Execução: Revisão Bibliográfica e Levantamento das Soluções

* **Identificador no Backlog:** `[EP-03] - Tarefa 2.2`

* **Épico Vinculado:** EP-03 — Proposta / Relatório Parcial (10 págs SBC)

* **Sprint:** Sprint 2 (30/11/2026 a 07/12/2026)

* **Meta de Extensão:** **2,5 páginas** (Tabela 6.1 do `plan.md`)

* **Status:** Pronto para Execução

* **Objetivo:** Substituir o *placeholder* da Seção 3 (`sec:revisao`) do `proposta.tex` por uma revisão estruturada do estado da arte, cobrindo (i) a camada física LoRa e a ortogonalidade imperfeita, (ii) os limites de escalabilidade do ALOHA no LoRaWAN, (iii) as estratégias de alocação de SF e ADR e (iv) a simulação de LoRaWAN no ns-3, encerrando com uma síntese comparativa que justifique a lacuna atacada pelo trabalho.

## 1. Estrutura e Orçamento da Seção

| Subseção | Conteúdo | Referências-Âncora | Extensão |
| :--- | :--- | :--- | :---: |
| 3.1 Camada Física LoRa e Ortogonalidade | CSS, SF, tempo no ar, quase-ortogonalidade | `semtech2015an1200`, `augustin2016study`, `croce2018impact` | 0,5 pág. |
| 3.2 Limites de Escalabilidade | ALOHA, duty cycle, análise estocástica | `bor2016lora`, `georgiou2017lpwan`, `adelantado2017understanding` | 0,6 pág. |
| 3.3 Alocação de SF e ADR | ADR da especificação, EXPLoRa, RS-LoRa, FLoRa | `lorawan_spec_v103`, `cuomo2017explora`, `reynders2018improving`, `slabicki2018adaptive`, `bor2017transmission` | 0,7 pág. |
| 3.4 Simulação no ns-3 | Módulos de Pádua e de Gante | `riley2010ns3`, `magrin2017performance`, `vandenabeele2017scalability`, `magrin2020thorough` | 0,4 pág. |
| 3.5 Síntese e Lacuna | Tabela comparativa | — | 0,3 pág. |

## 2. Passo a Passo de Execução

```bash
cd /home/bira/github/projetos/lorawan-ns3-perf-eval/docs/sbc-papers/proposta-parcial
```

### Passo 1: Correção das Entradas Existentes em `referencias.bib`

A auditoria da Sprint 1 identificou três entradas incorretas no arquivo real (já corrigidas na listagem do `sprint01.md`). Aplique as mesmas correções em `referencias.bib`:

* `magrin2017performance`: trabalho publicado no **IEEE ICC 2017** (autores Magrin, Centenaro e **Vangelista**), não na *IEEE Transactions on Wireless Communications* → tipo `@inproceedings`.
* `bor2016lora`: artigo de conferência (MSWiM 2016) → tipo `@inproceedings` (o campo `booktitle` já está correto).
* `adelantado2017understanding`: acentuação do autor → `Joan Meli{\`a}-Segu{\'\i}`.

```bibtex
@inproceedings{magrin2017performance,
  author    = {Davide Magrin and Marco Centenaro and Lorenzo Vangelista},
  title     = {Performance Evaluation of {LoRa} Networks in a Smart City Scenario},
  booktitle = {Proceedings of the IEEE International Conference on Communications (ICC)},
  address   = {Paris, France},
  pages     = {1--7},
  year      = {2017},
  publisher = {IEEE}
}
```

### Passo 2: Inclusão das Novas Referências em `referencias.bib`

Acrescente ao final do arquivo as entradas abaixo. **Todas devem ser conferidas (volume, páginas e DOI) no IEEE Xplore, ACM DL, MDPI ou DBLP na Tarefa 2.5** antes da submissão:

```bibtex
@techreport{semtech2015an1200,
  author      = {{Semtech Corporation}},
  title       = {{LoRa} Modulation Basics},
  institution = {Semtech Corporation},
  type        = {Application Note},
  number      = {AN1200.22},
  year        = {2015}
}

@article{augustin2016study,
  author  = {Aloÿs Augustin and Jiazi Yi and Thomas Clausen and William Mark Townsley},
  title   = {A Study of {LoRa}: Long Range \& Low Power Networks for the Internet of Things},
  journal = {Sensors},
  volume  = {16},
  number  = {9},
  pages   = {1466},
  year    = {2016}
}

@article{croce2018impact,
  author  = {Daniele Croce and Michele Gucciardo and Stefano Mangione and Giuseppe Santaromita and Ilenia Tinnirello},
  title   = {Impact of {LoRa} Imperfect Orthogonality: Analysis of Link-Level Performance},
  journal = {IEEE Communications Letters},
  volume  = {22},
  number  = {4},
  pages   = {796--799},
  year    = {2018}
}

@article{georgiou2017lpwan,
  author  = {Orestis Georgiou and Usman Raza},
  title   = {Low Power Wide Area Network Analysis: Can {LoRa} Scale?},
  journal = {IEEE Wireless Communications Letters},
  volume  = {6},
  number  = {2},
  pages   = {162--165},
  year    = {2017}
}

@inproceedings{cuomo2017explora,
  author    = {Francesca Cuomo and Manuel Campo and Alberto Caponi and Giuseppe Bianchi and Giampaolo Rossini and Patrizio Pisani},
  title     = {{EXPLoRa}: Extending the Performance of {LoRa} by Suitable Spreading Factor Allocations},
  booktitle = {Proceedings of the IEEE International Conference on Wireless and Mobile Computing, Networking and Communications (WiMob)},
  pages     = {1--8},
  year      = {2017}
}

@article{reynders2018improving,
  author  = {Brecht Reynders and Qing Wang and Pere Tuset-Peiro and Xavier Vilajosana and Sofie Pollin},
  title   = {Improving Reliability and Scalability of {LoRaWANs} Through Lightweight Scheduling},
  journal = {IEEE Internet of Things Journal},
  volume  = {5},
  number  = {3},
  pages   = {1830--1842},
  year    = {2018}
}

@inproceedings{slabicki2018adaptive,
  author    = {Mariusz Slabicki and Gopika Premsankar and Mario {Di Francesco}},
  title     = {Adaptive Configuration of {LoRa} Networks for Dense {IoT} Deployments},
  booktitle = {Proceedings of the IEEE/IFIP Network Operations and Management Symposium (NOMS)},
  pages     = {1--9},
  year      = {2018}
}

@inproceedings{bor2017transmission,
  author    = {Martin Bor and Utz Roedig},
  title     = {{LoRa} Transmission Parameter Selection},
  booktitle = {Proceedings of the 13th International Conference on Distributed Computing in Sensor Systems (DCOSS)},
  pages     = {27--34},
  year      = {2017}
}

@incollection{riley2010ns3,
  author    = {George F. Riley and Thomas R. Henderson},
  title     = {The ns-3 Network Simulator},
  booktitle = {Modeling and Tools for Network Simulation},
  editor    = {Klaus Wehrle and Mesut G{\"u}ne{\c{s}} and James Gross},
  publisher = {Springer},
  pages     = {15--34},
  year      = {2010}
}

@article{vandenabeele2017scalability,
  author  = {Floris {Van den Abeele} and Jetmir Haxhibeqiri and Ingrid Moerman and Jeroen Hoebeke},
  title   = {Scalability Analysis of Large-Scale {LoRaWAN} Networks in ns-3},
  journal = {IEEE Internet of Things Journal},
  volume  = {4},
  number  = {6},
  pages   = {2186--2198},
  year    = {2017}
}

@article{magrin2020thorough,
  author  = {Davide Magrin and Martina Capuzzo and Andrea Zanella},
  title   = {A Thorough Study of {LoRaWAN} Performance Under Different Parameter Settings},
  journal = {IEEE Internet of Things Journal},
  volume  = {7},
  number  = {1},
  pages   = {116--127},
  year    = {2020}
}
```

### Passo 3: Redação da Seção 3 no `proposta.tex`

Substitua o bloco atual (título `Revisão Bibliográfica e Levantamento das Soluções` seguido do parágrafo em itálico com o *placeholder*) pelo texto abaixo:

```latex
% =========================================================================
% SEÇÃO 3: REVISÃO BIBLIOGRÁFICA E LEVANTAMENTO DAS SOLUÇÕES
% =========================================================================
\section{Revisão Bibliográfica e Levantamento das Soluções}
\label{sec:revisao}

Esta seção organiza o estado da arte em quatro eixos: as propriedades da camada física LoRa que condicionam a interferência, os limites teóricos e empíricos de escalabilidade do LoRaWAN, as estratégias de alocação de fatores de espalhamento e, por fim, as ferramentas de simulação disponíveis no ns-3.

\subsection{Camada Física LoRa e Ortogonalidade Imperfeita}
\label{subsec:phy}

A modulação LoRa codifica cada símbolo como um \textit{chirp} linear cuja frequência varre toda a largura de banda $B$; o fator de espalhamento $SF \in \{7,\ldots,12\}$ define o número de \textit{chips} por símbolo ($2^{SF}$) e, portanto, a duração de símbolo $T_s = 2^{SF}/B$ \cite{semtech2015an1200}. Cada incremento unitário de SF dobra $T_s$, elevando a sensibilidade do receptor ao custo de reduzir a taxa de bits e multiplicar o tempo no ar (\textit{Time-on-Air} -- ToA) do quadro. Para um mesmo \textit{payload}, o ToA em SF12 supera em mais de uma ordem de grandeza o ToA em SF7, o que torna a escolha do SF o principal determinante tanto do alcance quanto da ocupação do canal \cite{augustin2016study}.

A literatura inicial assumia que transmissões simultâneas com SFs distintos seriam perfeitamente ortogonais. \citeauthor{croce2018impact} \cite{croce2018impact} demonstraram, por análise de enlace e experimentos com rádios reais, que essa ortogonalidade é imperfeita: um sinal interferente com SF diferente pode impedir a demodulação quando a relação sinal-interferência cai abaixo de limiares específicos para cada par de SFs. Em cenários com nós próximos ao gateway transmitindo em potência elevada, o efeito inter-SF deixa de ser desprezível e deve ser contemplado pelo modelo de simulação --- requisito atendido pelo módulo \texttt{lorawan} do ns-3, que implementa matrizes de isolamento entre SFs.

\subsection{Limites de Escalabilidade do LoRaWAN}
\label{subsec:escalabilidade}

\citeauthor{bor2016lora} \cite{bor2016lora} desenvolveram o simulador LoRaSim e, combinando medições com simulação, mostraram que configurações estáticas típicas limitam fortemente o número de dispositivos atendidos por gateway, apontando a seleção dinâmica de parâmetros de transmissão e a adição de gateways como mecanismos necessários para escalar. Sob a ótica analítica, \citeauthor{georgiou2017lpwan} \cite{georgiou2017lpwan} modelaram a rede por geometria estocástica e concluíram que a probabilidade de cobertura decai exponencialmente com o número de dispositivos, em razão da interferência entre nós que compartilham o mesmo SF.

\citeauthor{adelantado2017understanding} \cite{adelantado2017understanding} analisaram os limites impostos conjuntamente pelo acesso ALOHA e pela regulamentação de \textit{duty cycle}, evidenciando o compromisso entre tamanho da rede, taxa de envio e confiabilidade: o limite de ocupação de 1\% restringe a vazão por dispositivo e, nos gateways, a capacidade de enviar confirmações e comandos no enlace descendente. Esses resultados sustentam as questões QP-01 e QP-03 deste trabalho, mas tratam o \textit{duty cycle} como restrição fixa, sem isolar quantitativamente sua contribuição para as perdas totais.

\subsection{Estratégias de Alocação de SF e Adaptive Data Rate}
\label{subsec:adr}

A especificação LoRaWAN \cite{lorawan_spec_v103} define o mecanismo de \textit{Adaptive Data Rate} (ADR) apenas no nível de protocolo --- comandos \texttt{LinkADRReq}/\texttt{LinkADRAns} pelos quais o servidor de rede ajusta SF e potência dos dispositivos ---, deixando o algoritmo de decisão a cargo da implementação. Em geral, o servidor estima a margem de enlace a partir da SNR dos últimos quadros recebidos e reduz o SF enquanto houver margem, confinando nós próximos em SFs de menor ToA.

Diversas propostas buscam distribuir melhor a carga entre os SFs. O EXPLoRa \cite{cuomo2017explora} propõe alocações que equilibram o número de nós por SF (EXPLoRa-SF) ou o tempo de ocupação por SF (EXPLoRa-AT), superando a alocação baseada apenas no alcance. \citeauthor{reynders2018improving} \cite{reynders2018improving} agrupam dispositivos e atribuem SF e potência de forma coordenada (RS-LoRa), melhorando confiabilidade e equidade. \citeauthor{bor2017transmission} \cite{bor2017transmission} propõem um algoritmo de seleção de parâmetros de transmissão que reduz o consumo energético, e \citeauthor{slabicki2018adaptive} \cite{slabicki2018adaptive}, com o simulador FLoRa (OMNeT++), mostram que o ADR do lado da rede melhora a taxa de entrega e a eficiência energética em implantações densas e estáticas. Em comum, esses trabalhos comparam suas propostas a \textit{baselines} heterogêneas, o que dificulta isolar o ganho atribuível ao ADR em relação a uma alocação aleatória ou puramente geométrica.

\subsection{Simulação de LoRaWAN no ns-3}
\label{subsec:ns3}

O ns-3 é um simulador de eventos discretos de código aberto, escrito em C++, amplamente adotado na pesquisa em redes \cite{riley2010ns3}. Dois módulos LoRaWAN se destacam: o desenvolvido na Universidade de Pádua \cite{magrin2017performance}, base do módulo \texttt{lorawan} mantido pelo SignetLab, e o da Universidade de Gante \cite{vandenabeele2017scalability}. O primeiro foi usado para avaliar um cenário de cidade inteligente com milhares de nós e múltiplos gateways \cite{magrin2017performance} e, posteriormente, para um estudo abrangente do impacto de parâmetros como tráfego confirmado, número de retransmissões e ADR \cite{magrin2020thorough}. O segundo enfatiza o efeito do tráfego confirmado e do enlace descendente sobre a escalabilidade \cite{vandenabeele2017scalability}. O presente trabalho adota o módulo \texttt{lorawan} 0.3.7 sobre o ns-3.48, que oferece nativamente modelos de interferência inter-SF, rastreamento de desfechos por pacote (\texttt{LoraPacketTracker}), controle de \textit{duty cycle} por sub-banda, ADR no servidor de rede e modelo de energia do rádio.

\subsection{Síntese Comparativa e Lacuna}
\label{subsec:sintese}

A Tabela~\ref{tab:sintese} resume os trabalhos discutidos. Até onde foi possível verificar, poucos estudos comparam, sob um mesmo modelo de canal e com tratamento estatístico explícito (intervalos de confiança e testes pareados), as alocações aleatória, geométrica e ADR, isolando simultaneamente o efeito do \textit{duty cycle} regulatório. Essa é a lacuna que motiva o desenho experimental apresentado na Seção~\ref{sec:metodologia}.

\begin{table}[ht]
\centering
\caption{Síntese comparativa dos trabalhos relacionados.}
\label{tab:sintese}
\footnotesize
\begin{tabular}{@{}p{3.0cm}p{2.3cm}p{4.6cm}p{4.6cm}@{}}
\toprule
\textbf{Trabalho} & \textbf{Ferramenta} & \textbf{Foco} & \textbf{Limitação frente a este estudo} \\
\midrule
Bor et al. (2016) & LoRaSim & Escalabilidade e parâmetros estáticos & Sem ADR dinâmico no servidor \\
Georgiou e Raza (2017) & Analítico & Cobertura sob interferência co-SF & Modelo idealizado, sem MAC completo \\
Adelantado et al. (2017) & Analítico & Limites de ALOHA e \textit{duty cycle} & Não isola o efeito do \textit{duty cycle} \\
Cuomo et al. (2017) & Simulação & Alocação equilibrada de SF & Não compara com ADR padrão \\
Slabicki et al. (2018) & FLoRa & ADR em redes densas & Outro simulador e modelo de canal \\
Magrin et al. (2017; 2020) & ns-3 & Cidade inteligente e parâmetros & Foco multi-gateway e tráfego confirmado \\
\midrule
\textbf{Este trabalho} & ns-3.48 & RANDOM $\times$ DISTANCE $\times$ ADR, \textit{duty cycle} on/off & --- \\
\bottomrule
\end{tabular}
\end{table}
```

* **Nota de Estilo:** o comando `\citeauthor` pode não estar definido no estilo `sbc.bst` sem o pacote `natbib`. Se a compilação acusar erro, substitua cada ocorrência `\citeauthor{chave} \cite{chave}` pelo sobrenome escrito manualmente seguido de `\cite{chave}` (ex.: `Croce et al. \cite{croce2018impact}`).

### Passo 4: Compilação e Conferência da Extensão

```bash
./build_paper.sh
grep -E "Citation .* undefined" proposta.log || echo "Nenhuma citação indefinida."
```

Meça a extensão da Seção 3 no PDF (do título 3 até o título 4). Se exceder 2,5 páginas, condense primeiro a Subseção 3.3 (agrupando EXPLoRa e RS-LoRa em uma frase) antes de remover linhas da tabela.

### Passo 5: Registro e Versionamento no Git

```bash
cd /home/bira/github/projetos/lorawan-ns3-perf-eval
git add docs/sbc-papers/proposta-parcial/proposta.tex docs/sbc-papers/proposta-parcial/referencias.bib
git commit -m "docs(sbc): redige secao 3 (revisao bibliografica) e corrige referencias (EP-03 Tarefa 2.2)"
```

## 3. Matriz de Verificação e Homologação

| Item Avaliado | Procedimento de Verificação | Critério de Aceitação |
| :--- | :--- | :--- |
| **Cobertura temática** | Leitura das subseções 3.1–3.5 | PHY/ortogonalidade, escalabilidade, ADR/alocação, ns-3 e síntese presentes. |
| **Citações** | `grep "undefined" proposta.log` | Nenhuma citação `[?]`. |
| **Correção bibliográfica** | Inspeção de `referencias.bib` | `magrin2017performance` e `bor2016lora` como `@inproceedings`; acentos corretos. |
| **Lacuna explícita** | Leitura de 3.5 | Lacuna conecta-se diretamente às QP-02/QP-03 e à Seção 4. |
| **Extensão** | Medição no PDF | ≤ 2,5 páginas, incluindo a Tabela~\ref{tab:sintese}. |

## 4. Definição de Pronto (*Definition of Done - DoD*)

A atividade **`[EP-03] - Tarefa 2.2`** é considerada **Concluída (Done)** quando:

1. [ ] O *placeholder* da Seção 3 tiver sido integralmente substituído pelas subseções 3.1 a 3.5.
2. [ ] As três entradas incorretas de `referencias.bib` estiverem corrigidas e as 11 novas referências incluídas.
3. [ ] A compilação via `./build_paper.sh` terminar sem citações indefinidas.
4. [ ] A Seção 3 ocupar no máximo 2,5 páginas no PDF.
5. [ ] O commit estiver registrado, liberando a Tarefa 2.3 (Metodologia).

## [EP-03] - Tarefa 2.3: Redigir a Seção 4 da Proposta (Planejamento detalhado da avaliação de desempenho).

# Especificação Técnica de Execução: Metodologia de Avaliação de Desempenho (Raj Jain)

* **Identificador no Backlog:** `[EP-03] - Tarefa 2.3`

* **Épico Vinculado:** EP-03 — Proposta / Relatório Parcial (10 págs SBC)

* **Sprint:** Sprint 2 (30/11/2026 a 07/12/2026)

* **Meta de Extensão:** **2,5 páginas** (Tabela 6.1 do `plan.md`)

* **Status:** Pronto para Execução

* **Objetivo:** Substituir o *placeholder* da Seção 4 (`sec:metodologia`) por uma metodologia reprodutível que transcreva fielmente o **ADR-002** e o **SDD**: modelo de simulação, fatores e níveis, métricas com definição matemática, controle estatístico e procedimentos de validação, seguindo a sequência sistemática de Jain (objetivos → métricas → parâmetros → fatores → técnica → carga → desenho → análise).

## 1. Correspondência entre o Arcabouço de Jain e a Seção 4

| Etapa de Jain (cap. 2) | Onde é Atendida | Fonte no Repositório |
| :--- | :--- | :--- |
| Objetivos e fronteiras do sistema | Seções 2 e 4.1 | `proposta.tex` (QP/H) |
| Seleção de métricas | Subseção 4.3 | `plan.md` §5.1, SDD §4 |
| Parâmetros do sistema e da carga | Subseção 4.1 | `default_scenario.yaml` |
| Fatores e níveis | Subseção 4.2 | ADR-002, `main_factorial.yaml` |
| Técnica de avaliação | Subseção 4.1 (simulação) | ADR-001 |
| Desenho de experimentos | Subseção 4.2 | ADR-002 |
| Análise e interpretação | Subseção 4.4 | SDD CA-006/CA-007 |

## 2. Passo a Passo de Execução

```bash
cd /home/bira/github/projetos/lorawan-ns3-perf-eval/docs/sbc-papers/proposta-parcial
```

### Passo 1: Conferência dos Parâmetros do Modelo no Código-Fonte

Os valores citados na Subseção 4.1 foram extraídos do exemplo canônico do módulo e devem ser reconferidos caso o cenário customizado (Sprint 3) os altere:

```bash
grep -n "SetPathLossExponent\|SetReference\|CorrelatedShadowing\|SetSpreadingFactorsUp" \
  ../../../sim-ns3/ns-3.48/src/lorawan/examples/complete-network-example.cc
grep -n "EnableAdr\|EndDeviceLorawanMac::ADR" \
  ../../../sim-ns3/ns-3.48/src/lorawan/examples/adr-example.cc
```

* **Valores esperados:** perda log-distância com expoente $n = 3{,}76$ e perda de referência de 7,7 dB a 1 m; ADR habilitado por `NetworkServerHelper::EnableAdr` e pelo atributo `ns3::EndDeviceLorawanMac::ADR`.

### Passo 2: Inclusão das Referências Metodológicas em `referencias.bib`

```bibtex
@techreport{jain1984fairness,
  author      = {Raj Jain and Dah-Ming Chiu and William R. Hawe},
  title       = {A Quantitative Measure of Fairness and Discrimination for Resource Allocation in Shared Computer Systems},
  institution = {Digital Equipment Corporation},
  number      = {DEC-TR-301},
  year        = {1984}
}

@article{pawlikowski2002credibility,
  author  = {Krzysztof Pawlikowski and Hae-Duck Joshua Jeong and Jong-Suk Ruth Lee},
  title   = {On Credibility of Simulation Studies of Telecommunication Networks},
  journal = {IEEE Communications Magazine},
  volume  = {40},
  number  = {1},
  pages   = {132--139},
  year    = {2002}
}
```

### Passo 3: Redação da Seção 4 no `proposta.tex`

Substitua o bloco atual (título `Metodologia Proposta para Avaliação de Desempenho` seguido do *placeholder* em itálico) pelo texto abaixo. A figura `fig:arquitetura` é produzida na Tarefa 2.4; até lá, a referência aparecerá como `??`.

```latex
% =========================================================================
% SEÇÃO 4: METODOLOGIA PROPOSTA PARA AVALIAÇÃO DE DESEMPENHO
% =========================================================================
\section{Metodologia Proposta para Avaliação de Desempenho}
\label{sec:metodologia}

A avaliação segue a abordagem sistemática de \cite{jain1991art}: definidos os objetivos (Seção~\ref{sec:problema}), especificam-se o modelo de simulação, os fatores e níveis, as métricas e o tratamento estatístico. A técnica escolhida é a simulação de eventos discretos, que permite controlar a interferência e o tráfego em escalas inviáveis para experimentação física, desde que acompanhada de cuidados de credibilidade estatística \cite{pawlikowski2002credibility}.

\subsection{Modelo de Simulação e Parâmetros Fixos}
\label{subsec:modelo}

O sistema é modelado no ns-3.48 com o módulo \texttt{lorawan} 0.3.7. A célula possui um gateway central e $N$ dispositivos Classe A distribuídos uniformemente em um disco de raio $R = 2$~km, com perda de percurso log-distância (expoente $n = 3{,}76$ e perda de referência de 7,7~dB a 1~m). Os dispositivos operam no plano EU868 com três canais de 125~kHz e \textit{duty cycle} de 1\% por sub-banda, gerando quadros \textit{uplink} não confirmados de 20~bytes de \textit{payload} com período $T$ por meio da aplicação \texttt{PeriodicSender}. O gateway encaminha os quadros ao servidor de rede por enlace ponto-a-ponto ideal; o consumo de energia é contabilizado pelo modelo de energia do rádio LoRa do próprio módulo.

Cada execução simula 4200~s: os primeiros 600~s são descartados como período transitório (\textit{warm-up}) e as métricas são computadas nos 3600~s seguintes, intervalo que corresponde a pelo menos seis períodos de envio no nível de carga mais baixo.

\subsection{Fatores, Níveis e Desenho Experimental}
\label{subsec:fatores}

Adota-se um desenho fatorial completo com três fatores (Tabela~\ref{tab:fatores}), totalizando $5 \times 3 \times 2 = 30$ pontos experimentais. A estratégia \texttt{RANDOM} sorteia o SF uniformemente entre SF7 e SF12; \texttt{DISTANCE} atribui o menor SF compatível com o orçamento de enlace de cada nó no início da simulação; e \texttt{ADR} parte da alocação geométrica e permite que o servidor de rede ajuste SF e potência durante a operação.

\begin{table}[ht]
\centering
\caption{Fatores e níveis do desenho fatorial principal.}
\label{tab:fatores}
\footnotesize
\begin{tabular}{@{}llp{6.5cm}@{}}
\toprule
\textbf{Fator} & \textbf{Níveis} & \textbf{Relação com QP/H} \\
\midrule
A -- Densidade $N$ & 100, 250, 500, 1000, 2000 & QP-01, $H_1$ \\
B -- Estratégia de SF & \texttt{RANDOM}, \texttt{DISTANCE}, \texttt{ADR} & QP-02, $H_2$ \\
C -- Período $T$ & 60~s, 600~s & Carga oferecida alta e baixa \\
\bottomrule
\end{tabular}
\end{table}

Dois experimentos complementares, variando um fator por vez, completam o desenho: (i) \textbf{E-DC}, que desabilita o \textit{duty cycle} com \texttt{ADR} e $T = 60$~s para todos os níveis de $N$, isolando seu efeito ($H_3$, QP-03); e (ii) \textbf{E-R}, que repete \texttt{DISTANCE} e \texttt{ADR} com $T = 600$~s em raio de 6~km, avaliando a sensibilidade ao tamanho da célula. Somados, são 45 pontos experimentais.

\subsection{Métricas de Desempenho}
\label{subsec:metricas}

Seja $G$ o número de pacotes gerados, $R_x$ o número de pacotes recebidos com sucesso, $L$ o tamanho do \textit{payload} em bytes e $T_m = 3600$~s o tempo de medição. As métricas, classificadas segundo \cite{jain1991art} em \textit{higher is better} (HB) e \textit{lower is better} (LB), são:

\begin{itemize}
    \item \textbf{PDR (HB):} $\mathrm{PDR} = R_x / G$.
    \item \textbf{Vazão efetiva (HB):} $S = 8 L R_x / T_m$ (bit/s).
    \item \textbf{Atraso médio (LB):} média do intervalo entre o início da transmissão e a recepção no servidor de rede.
    \item \textbf{Energia por pacote útil (LB):} $E_u = \sum_{i=1}^{N} E_i / R_x$, sendo $E_i$ a energia consumida pelo rádio do nó $i$.
    \item \textbf{Taxa de colisão (LB):} fração das transmissões perdidas por interferência (mesmo SF ou inter-SF).
    \item \textbf{Taxa de bloqueio por \textit{duty cycle} (LB):} fração de $G$ não transmitida por esgotamento da janela regulatória.
    \item \textbf{Equidade:} índice de Jain \cite{jain1984fairness} aplicado ao PDR individual $x_i$ dos nós,
    \begin{equation}
    \mathrm{JFI} = \frac{\left(\sum_{i=1}^{N} x_i\right)^2}{N \sum_{i=1}^{N} x_i^2}, \qquad \frac{1}{N} \leq \mathrm{JFI} \leq 1,
    \label{eq:jfi}
    \end{equation}
    complementado pela estratificação do PDR por anéis de distância ao gateway (QP-04).
\end{itemize}

\subsection{Controle Estocástico e Tratamento Estatístico}
\label{subsec:estatistica}

Cada ponto experimental é replicado $n = 30$ vezes, mantendo-se a semente global fixa (\texttt{RngSeed} = 1) e variando-se o identificador de execução (\texttt{RngRun} = 1, \ldots, 30), o que produz subsequências independentes do gerador do ns-3. Para cada métrica, reporta-se a média amostral $\bar{x}$ com intervalo de confiança de 95\%,
\begin{equation}
\bar{x} \pm t_{0{,}975;\,n-1}\,\frac{s}{\sqrt{n}},
\label{eq:ic}
\end{equation}
em que $s$ é o desvio padrão amostral. A hipótese $H_2$ é testada por teste $t$ pareado sobre as diferenças $d_j = \mathrm{PDR}_{\mathrm{ADR},j} - \mathrm{PDR}_{\mathrm{RANDOM},j}$, emparelhadas pelo mesmo \texttt{RngRun} (mesma topologia), com nível de significância $\alpha = 0{,}05$; procedimento análogo compara E-DC ao ponto correspondente com \textit{duty cycle} habilitado ($H_3$). Ao todo, $45 \times 30 = 1350$ execuções independentes são processadas em paralelo.

\subsection{Validação do Modelo e Plataforma Experimental}
\label{subsec:validacao}

Antes das campanhas, o modelo é verificado por testes degenerados \cite{jain1991art}: (i) um único nó, para o qual se espera PDR próximo de 100\%; (ii) cinco nós a até 100~m do gateway, sem perdas por sensibilidade; e (iii) todos os nós em SF12, condição de máximo ToA e máxima colisão. Verifica-se ainda a conservação de pacotes: gerados = transmitidos + bloqueados por \textit{duty cycle}, e transmitidos = soma dos desfechos na camada física.

A orquestração e a análise são implementadas em Python segundo a Arquitetura Hexagonal (Figura~\ref{fig:arquitetura}): o domínio concentra as regras de cálculo de métricas e estatística, isolado por portas abstratas dos adaptadores que invocam o binário do ns-3 e persistem os resultados. Os artefatos trocados são regidos por contratos formais em JSON Schema --- cenário (CT-001), metadados de execução com versão do simulador e \textit{hash} do código (CT-002) e métricas brutas por pacote e por nó (CT-003) ---, garantindo rastreabilidade e reprodutibilidade de cada resultado.
```

### Passo 4: Compilação e Conferência

```bash
./build_paper.sh
grep -E "Reference .* undefined|Citation .* undefined" proposta.log
```

* **Resultado Esperado:** apenas `fig:arquitetura` (e `fig:topologia`, se já citada) indefinidas até a conclusão da Tarefa 2.4.

### Passo 5: Registro e Versionamento no Git

```bash
cd /home/bira/github/projetos/lorawan-ns3-perf-eval
git add docs/sbc-papers/proposta-parcial/proposta.tex docs/sbc-papers/proposta-parcial/referencias.bib
git commit -m "docs(sbc): redige secao 4 (metodologia Raj Jain, ADR-002) (EP-03 Tarefa 2.3)"
```

## 3. Matriz de Verificação e Homologação

| Item Avaliado | Procedimento de Verificação | Critério de Aceitação |
| :--- | :--- | :--- |
| **Fidelidade ao ADR-002** | Comparação da Tabela~\ref{tab:fatores} e do texto com o ADR-002 | Níveis, E-DC, E-R, 30 replicações e 1350 execuções idênticos. |
| **Fidelidade ao código** | Passo 1 (`grep` nos exemplos) | Expoente 3,76 e referência 7,7 dB conferem. |
| **Métricas definidas** | Leitura de 4.3 | Sete métricas com classificação HB/LB e definição operacional. |
| **Estatística** | Leitura de 4.4 | IC 95% (Eq.~\ref{eq:ic}) e teste $t$ pareado com emparelhamento explícito. |
| **Validação** | Leitura de 4.5 | Três testes degenerados e conservação de pacotes descritos. |
| **Extensão** | Medição no PDF | ≤ 2,5 páginas. |

## 4. Definição de Pronto (*Definition of Done - DoD*)

A atividade **`[EP-03] - Tarefa 2.3`** é considerada **Concluída (Done)** quando:

1. [ ] O *placeholder* da Seção 4 tiver sido substituído pelas subseções 4.1 a 4.6.
2. [ ] Todos os valores numéricos coincidirem com o ADR-002, o `default_scenario.yaml` e o código do módulo.
3. [ ] As referências `jain1984fairness` e `pawlikowski2002credibility` estiverem incluídas e compilando.
4. [ ] A Seção 4 ocupar no máximo 2,5 páginas.
5. [ ] O commit estiver registrado, restando apenas as figuras da Tarefa 2.4 como referências pendentes.

## [EP-03] - Tarefa 2.4: Diagramar as figuras conceituais e a arquitetura hexagonal da solução no formato SBC.

# Especificação Técnica de Execução: Figuras Vetoriais em TikZ

* **Identificador no Backlog:** `[EP-03] - Tarefa 2.4`

* **Épico Vinculado:** EP-03 — Proposta / Relatório Parcial (10 págs SBC)

* **Sprint:** Sprint 2 (30/11/2026 a 07/12/2026)

* **Status:** Pronto para Execução

* **Objetivo:** Produzir duas figuras vetoriais, em tons de cinza (legíveis em impressão monocromática), versionadas como código-fonte TikZ em `docs/sbc-papers/proposta-parcial/figures/`: **Figura 1** — topologia estrela-de-estrelas do LoRaWAN (Seção 1) e **Figura 2** — Arquitetura Hexagonal da plataforma experimental (Seção 4.6).

## 1. Decisões de Projeto

| Critério | Decisão | Justificativa |
| :--- | :--- | :--- |
| Ferramenta | TikZ (código LaTeX) | Vetorial, versionável no Git, fontes idênticas às do texto e sem dependência de editor gráfico. |
| Paleta | Tons de cinza | Diretriz de alto contraste do backlog (Sprint 8) aplicada desde a proposta. |
| Inclusão | `\input{figures/*.tex}` | Mantém o `proposta.tex` enxuto. |
| Largura | `\resizebox{\linewidth}{!}{...}` na Figura 2 | Garante que a figura nunca ultrapasse a mancha gráfica do template SBC. |
| Legenda | Abaixo da figura, conforme o template SBC | Padrão da SBC (legendas de tabela acima, de figura abaixo). |

## 2. Passo a Passo de Execução

```bash
cd /home/bira/github/projetos/lorawan-ns3-perf-eval/docs/sbc-papers/proposta-parcial
```

### Passo 1: Habilitação do TikZ no Preâmbulo

Acrescente ao preâmbulo do `proposta.tex`, logo após `\usepackage{microtype}`:

```latex
\usepackage{tikz}
\usetikzlibrary{arrows.meta,shapes.geometric}
```

Confirme que o pacote está instalado:

```bash
kpsewhich tikz.sty || sudo apt install -y texlive-pictures
```

### Passo 2: Figura 1 — Topologia LoRaWAN (`figures/topologia.tex`)

```bash
cat << 'EOF' > figures/topologia.tex
% Figura 1 - Topologia estrela-de-estrelas do LoRaWAN (Classe A, uplink ALOHA)
\begin{tikzpicture}[font=\scriptsize, >={Stealth[length=2mm]},
  ed/.style={circle, draw, fill=gray!30, minimum size=3mm, inner sep=0pt},
  gw/.style={draw, fill=gray!50, minimum width=13mm, minimum height=6mm},
  ns/.style={draw, rounded corners, fill=gray!15, align=center, minimum width=20mm, minimum height=8mm}]
  \draw[gray, dashed] (0,0) circle (2.4cm);
  \foreach \ang/\rad/\lab in {95/0.9/SF7, 130/1.6/SF9, 165/2.2/SF12, 200/1.2/SF8, 235/1.9/SF10, 270/0.7/SF7} {
    \node[ed] (n) at (\ang:\rad) {};
    \node[font=\tiny, anchor=south] at (n.north) {\lab};
    \draw[->, gray] (n) -- (0,0);
  }
  \node[gw] (gw) at (0,0) {Gateway};
  \node[ns] (ns) at (4.6,0) {Network\\ Server};
  \draw[<->, thick] (gw) -- node[above]{backhaul IP} (ns);
  \node[align=center] at (-3.2,1.9) {End Devices\\ (Classe A)};
  \node at (0,-2.75) {$R = 2$~km (6~km no experimento E-R)};
  \node[align=left, anchor=west] at (2.6,-1.6) {$\rightarrow$ \textit{uplink} LoRa\\ \phantom{$\rightarrow$} (ALOHA, SF7--SF12)};
\end{tikzpicture}
EOF
```

### Passo 3: Figura 2 — Arquitetura Hexagonal (`figures/arquitetura-hexagonal.tex`)

```bash
cat << 'EOF' > figures/arquitetura-hexagonal.tex
% Figura 2 - Arquitetura Hexagonal (Ports & Adapters) da plataforma experimental
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[font=\scriptsize, >={Stealth[length=2mm]},
  port/.style={draw, fill=white, rounded corners=2pt, align=center, minimum width=27mm, minimum height=6mm},
  adapter/.style={draw, fill=gray!25, align=center, minimum width=27mm, minimum height=7mm},
  ext/.style={draw, dashed, align=center, minimum width=22mm, minimum height=8mm}]
  % Dominio
  \node[draw, thick, regular polygon, regular polygon sides=6, minimum size=52mm, fill=gray!8] (core) at (0,0) {};
  \node[align=center] at (0,0) {\textbf{Domínio (core)}\\[1mm] Entidades e VOs\\ PDR, vazão, energia, JFI\\ IC 95\%, teste $t$ pareado};
  % Portas de entrada (driving)
  \node[port] (p1) at (-3.3, 0.7) {IExperimentOrchestrator};
  \node[port] (p2) at (-3.3,-0.7) {IAnalysisService};
  % Portas de saida (driven)
  \node[port] (p3) at (3.3, 0.7) {INs3SimulationRunner};
  \node[port] (p4) at (3.3,-0.7) {IResultsRepository};
  % Adaptadores
  \node[adapter] (a1) at (-6.8, 0) {CLI / scripts\\ (adaptador de entrada)};
  \node[adapter] (a3) at (6.8, 0.7) {SubprocessNs3Adapter};
  \node[adapter] (a4) at (6.8,-0.7) {FileSystemResultsAdapter};
  % Sistemas externos
  \node[ext] (e3) at (10.2, 0.7) {ns-3.48 +\\ lorawan 0.3.7};
  \node[ext] (e4) at (10.2,-0.7) {data/raw,\\ data/processed};
  % Relacoes
  \draw[->] (a1) -- (p1);
  \draw[->] (a1) -- (p2);
  \draw[->, dashed] (a3) -- (p3);
  \draw[->, dashed] (a4) -- (p4);
  \draw[<->] (a3) -- (e3);
  \draw[<->] (a4) -- (e4);
  % Legenda
  \node[align=center] at (1.7,-3.2) {Setas sólidas: invocação \quad Setas tracejadas: implementação de porta (DIP) \quad Contratos: CT-001, CT-002, CT-003};
\end{tikzpicture}%
}
EOF
```

### Passo 4: Inserção das Figuras no `proposta.tex`

**Figura 1** — ao final do terceiro parágrafo da Seção 1 (o que descreve a topologia estrela-de-estrelas), acrescente a frase `A Figura~\ref{fig:topologia} ilustra essa organização.` e, logo após o parágrafo:

```latex
\begin{figure}[ht]
\centering
\input{figures/topologia.tex}
\caption{Topologia estrela-de-estrelas do LoRaWAN: dispositivos Classe A transmitem por ALOHA ao gateway, que encaminha os quadros ao servidor de rede.}
\label{fig:topologia}
\end{figure}
```

**Figura 2** — ao final da Subseção 4.6 (`subsec:validacao`):

```latex
\begin{figure}[ht]
\centering
\input{figures/arquitetura-hexagonal.tex}
\caption{Arquitetura Hexagonal da plataforma de orquestração e análise: o domínio é isolado por portas abstratas dos adaptadores de execução do ns-3 e de persistência.}
\label{fig:arquitetura}
\end{figure}
```

### Passo 5: Compilação e Inspeção Visual

```bash
./build_paper.sh
grep -E "Reference .* undefined" proposta.log || echo "Todas as referências cruzadas resolvidas."
grep -c "Overfull \\\\hbox" proposta.log
```

Inspecione o PDF em zoom de 100% e em impressão simulada em escala de cinza: rótulos legíveis (corpo mínimo equivalente a 7 pt), nenhum elemento cortado e nenhuma sobreposição entre setas e textos.

### Passo 6: Registro e Versionamento no Git

```bash
cd /home/bira/github/projetos/lorawan-ns3-perf-eval
git add docs/sbc-papers/proposta-parcial/figures/ docs/sbc-papers/proposta-parcial/proposta.tex
git commit -m "docs(sbc): adiciona figuras TikZ de topologia e arquitetura hexagonal (EP-03 Tarefa 2.4)"
```

## 3. Matriz de Verificação e Homologação

| Item Avaliado | Procedimento de Verificação | Critério de Aceitação |
| :--- | :--- | :--- |
| **Compilação** | `./build_paper.sh` | Sem erros de TikZ; PDF gerado. |
| **Referências cruzadas** | `grep "undefined" proposta.log` | `fig:topologia` e `fig:arquitetura` resolvidas. |
| **Dimensões** | Contagem de `Overfull \hbox` | Nenhum *overfull* originado nas figuras. |
| **Monocromia** | Visualização em escala de cinza | Todos os elementos distinguíveis sem cor. |
| **Consistência** | Comparação com SDD/`plan.md` §4.1 | Nomes de portas e adaptadores idênticos aos da especificação. |

## 4. Definição de Pronto (*Definition of Done - DoD*)

A atividade **`[EP-03] - Tarefa 2.4`** é considerada **Concluída (Done)** quando:

1. [ ] `figures/topologia.tex` e `figures/arquitetura-hexagonal.tex` estiverem versionados.
2. [ ] As duas figuras estiverem referenciadas no texto e com legenda abaixo.
3. [ ] A compilação não apresentar referências indefinidas nem *overfull boxes* nas figuras.
4. [ ] Os nomes de componentes coincidirem com o SDD e o `plan.md` §4.1.
5. [ ] O commit estiver registrado, liberando a revisão final (Tarefa 2.5).

## [EP-03] - Tarefa 2.5: Revisão textual, bibliográfica e contagem rigorosa de páginas (exatamente 10 páginas).

# Especificação Técnica de Execução: Auditoria Final e Submissão do Relatório Parcial

* **Identificador no Backlog:** `[EP-03] - Tarefa 2.5`

* **Épico Vinculado:** EP-03 — Proposta / Relatório Parcial (10 págs SBC)

* **Sprint:** Sprint 2 (30/11/2026 a 07/12/2026)

* **Marco Acadêmico:** **Entrega em 08/12/2026** (Marco 1 da fonte `trcsf26-2v1.pdf`)

* **Status:** Pronto para Execução

* **Objetivo:** Auditar o documento completo quanto a conteúdo obrigatório, consistência técnica, qualidade das referências e formatação SBC; ajustar a extensão para **exatamente 10 páginas**; gerar o PDF de entrega e congelar a versão no Git com a tag `v0.2-proposta-parcial`.

## 1. Requisitos Normativos do Marco 1

| Requisito (`trcsf26-2v1.pdf`) | Seção do Documento | Situação Esperada |
| :--- | :--- | :--- |
| Introdução contextualizada | Seção 1 | Redigida (Sprint 1) e revisada |
| Problema a ser abordado | Seção 2 | Redigida (Sprint 1), QP/H alinhadas ao ADR-002 |
| Levantamento e discussão das soluções | Seção 3 | Tarefa 2.2 |
| Proposta de avaliação de desempenho | Seção 4 | Tarefa 2.3 (+ figuras da Tarefa 2.4) |
| Referências bibliográficas | Referências | Formatadas por `sbc.bst` |
| 10 páginas no padrão SBC | Documento inteiro | Verificado automaticamente (Passo 1) |

## 2. Passo a Passo de Execução

```bash
cd /home/bira/github/projetos/lorawan-ns3-perf-eval/docs/sbc-papers/proposta-parcial
```

### Passo 1: Script de Compilação com Auditoria Automática (`build_paper.sh`)

Substitua o script da Sprint 1 por uma versão que interrompe a execução em erros de LaTeX, detecta citações/referências indefinidas e, no modo estrito, exige exatamente 10 páginas:

```bash
cat << 'EOF' > build_paper.sh
#!/bin/bash
# Compila o Relatorio Parcial SBC e audita referencias e numero de paginas.
# Uso: ./build_paper.sh            (modo informativo)
#      STRICT_PAGES=1 ./build_paper.sh  (falha se paginas != 10)
set -euo pipefail

DOC=proposta
TARGET_PAGES=10

echo "=== Compilando Documento SBC (LaTeX + BibTeX) ==="
pdflatex -interaction=nonstopmode -halt-on-error "$DOC.tex" > /dev/null
bibtex "$DOC" > /dev/null
pdflatex -interaction=nonstopmode -halt-on-error "$DOC.tex" > /dev/null
pdflatex -interaction=nonstopmode -halt-on-error "$DOC.tex" > /dev/null

echo "=== Auditoria ==="
if grep -qE "(Citation|Reference) .* undefined" "$DOC.log"; then
  echo "ERRO: citacoes ou referencias indefinidas:"
  grep -E "(Citation|Reference) .* undefined" "$DOC.log"
  exit 1
fi

if grep -q "Warning--" "$DOC.blg"; then
  echo "AVISO (BibTeX):"
  grep "Warning--" "$DOC.blg"
fi

OVERFULL=$(grep -c "Overfull \\\\hbox" "$DOC.log" || true)
echo "Overfull hbox: $OVERFULL"

TOTAL_PAGES=$(pdfinfo "$DOC.pdf" | awk '/^Pages:/ {print $2}')
echo "Paginas: $TOTAL_PAGES (meta: $TARGET_PAGES)"

if [ "${STRICT_PAGES:-0}" = "1" ] && [ "$TOTAL_PAGES" -ne "$TARGET_PAGES" ]; then
  echo "ERRO: o documento deve ter exatamente $TARGET_PAGES paginas."
  exit 1
fi
echo "=== Concluido ==="
EOF

chmod +x build_paper.sh
./build_paper.sh
```

### Passo 2: Revisão de Consistência Técnica

Aplique as correções abaixo, identificadas na auditoria cruzada entre o texto, o ADR-002 e o código do módulo:

| # | Local | Problema | Correção |
| :---: | :--- | :--- | :--- |
| 1 | Seção 2.1, 2º parágrafo | "tempos no ar de até dez vezes superiores" subestima a razão real: para o mesmo quadro a 125 kHz, o ToA em SF12 é cerca de 25 vezes o ToA em SF7 (ex.: ≈ 72 ms × ≈ 1,8 s para PHYPayload de 33 bytes, isto é, 20 bytes de aplicação + 13 de cabeçalho LoRaWAN). | Substituir por "tempos no ar mais de vinte vezes superiores", citando `semtech2015an1200`. |
| 2 | Seção 2.1, 1º parágrafo | "despolarizar" não descreve o fenômeno (LoRa não envolve polarização). | Substituir "pode despolarizar e degradar" por "pode degradar", citando também `croce2018impact`. |
| 3 | Resumo/Abstract | Não mencionam o desenho experimental aprovado. | Usar os textos do Passo 3. |
| 4 | Cabeçalho | Nome e e-mail do autor divergem dos metadados do repositório (`pyproject.toml`). | **Confirmar** o nome e o e-mail institucional corretos e uniformizar. |
| 5 | Seção 1, último parágrafo | Menciona "extensões de protocolo não implementadas", mas o duty cycle e o ADR já são nativos (ADR-002). | Reescrever como "instrumentação e encapsulamento das estratégias de alocação e do controle de \textit{duty cycle}". |
| 6 | Seções 3 e 4 | Comentários de *placeholder* remanescentes. | Remover todo texto em itálico entre colchetes. |

### Passo 3: Atualização do Resumo e do Abstract

```latex
\begin{abstract}
This paper proposes a simulation-based performance evaluation of LoRaWAN networks in ns-3 (version 3.48, \texttt{lorawan} module 0.3.7). A full factorial design crosses network density (100 to 2000 end devices), spreading factor allocation (random, distance-based and network-side ADR) and offered load, complemented by experiments that isolate the regulatory 1\% duty cycle and the cell radius. Packet delivery ratio, throughput, delay, energy per delivered packet, collision rate and Jain's fairness index are estimated from 30 independent replications per point, reported with 95\% confidence intervals and compared with paired $t$-tests, following Raj Jain's methodology. Experiments are orchestrated by a Python platform built on Hexagonal Architecture and formal data contracts.
\end{abstract}

\begin{resumo}
Este trabalho propõe a avaliação de desempenho de redes LoRaWAN por simulação no ns-3 (versão 3.48, módulo \texttt{lorawan} 0.3.7). Um desenho fatorial completo cruza a densidade de dispositivos (100 a 2000 nós), a estratégia de alocação de fatores de espalhamento (aleatória, geométrica e ADR no servidor de rede) e a carga oferecida, complementado por experimentos que isolam o \textit{duty cycle} regulatório de 1\% e o raio da célula. Taxa de entrega de pacotes, vazão, atraso, energia por pacote entregue, taxa de colisão e índice de equidade de Jain são estimados a partir de 30 replicações independentes por ponto, com intervalos de confiança de 95\% e testes $t$ pareados, segundo a metodologia de Raj Jain. Os experimentos são orquestrados por uma plataforma em Python baseada em Arquitetura Hexagonal e contratos formais de dados.
\end{resumo}
```

### Passo 4: Auditoria Bibliográfica

Para **cada** entrada de `referencias.bib`, confirme em fonte primária (IEEE Xplore, ACM Digital Library, MDPI, Springer Link ou DBLP) autores, título, veículo, volume, número, páginas e ano, e acrescente o campo `doi` quando existir:

```bash
grep -E "^@" referencias.bib | sort        # inventario das entradas
grep -c "^@" referencias.bib               # total esperado: 20
grep -oE "\\\\cite\{[^}]+\}" proposta.tex | tr ',' '\n' | sort -u   # chaves citadas
```

* **Critérios:** (i) toda entrada do `.bib` é citada ao menos uma vez (o `sbc.bst` só lista as citadas, mas entradas órfãs indicam texto removido); (ii) nenhuma citação aponta para chave inexistente; (iii) o arquivo `proposta.blg` não contém `Warning--`.

### Passo 5: Ajuste Rigoroso para 10 Páginas

```bash
STRICT_PAGES=1 ./build_paper.sh
```

Se o total diferir de 10 páginas, aplique os ajustes na ordem abaixo (do menos para o mais invasivo), recompilando após cada um:

| Situação | Ajuste (em ordem de preferência) |
| :--- | :--- |
| **Excesso** | 1) Condensar a Subseção 3.3; 2) reduzir a Figura 1 para `\scalebox{0.85}`; 3) mesclar 4.5 e 4.6; 4) remover a linha "Magrin et al." da Tabela~\ref{tab:sintese}. |
| **Falta** | 1) Expandir 3.5 com a justificativa da escolha do módulo de Pádua; 2) acrescentar em 4.3 a definição operacional de atraso; 3) incluir em 4.2 a contagem de execuções por experimento. |

* **Restrição:** não alterar margens, corpo de fonte nem espaçamentos definidos por `sbc-template.sty`.

### Passo 6: Geração do Artefato de Entrega e Congelamento da Versão

```bash
# 1. Cópia nomeada do PDF de entrega
mkdir -p ../entregas
cp proposta.pdf ../entregas/relatorio-parcial-2026-12-08.pdf

# 2. Registro no Git
cd /home/bira/github/projetos/lorawan-ns3-perf-eval
git add docs/sbc-papers/
git commit -m "docs(sbc): revisao final do relatorio parcial com 10 paginas (EP-03 Tarefa 2.5)"

# 3. Tag do Marco 1
git tag -a v0.2-proposta-parcial -m "Marco 1: Relatorio Parcial (10 paginas SBC) - entrega 08/12/2026"
git push origin main --tags
```

## 3. Matriz de Verificação e Homologação

| Item Avaliado | Procedimento de Verificação | Critério de Aceitação |
| :--- | :--- | :--- |
| **Contagem de páginas** | `STRICT_PAGES=1 ./build_paper.sh` | Retorno `0` com exatamente 10 páginas. |
| **Referências cruzadas** | Auditoria automática do script | Nenhuma citação ou referência indefinida. |
| **Bibliografia** | Passo 4 | 20 entradas conferidas em fonte primária, sem avisos do BibTeX. |
| **Conteúdo obrigatório** | Tabela da Seção 1 desta tarefa | Os cinco elementos exigidos pela fonte presentes. |
| **Consistência técnica** | Tabela do Passo 2 | As seis correções aplicadas. |
| **Formatação SBC** | Inspeção visual | Template sem alterações; legendas de tabelas acima e de figuras abaixo. |
| **Versionamento** | `git tag -l "v0.2*"` | Tag `v0.2-proposta-parcial` publicada no `origin`. |

## 4. Definição de Pronto (*Definition of Done - DoD*) da Tarefa 2.5 e Fechamento da Sprint 2

A atividade **`[EP-03] - Tarefa 2.5`** e a **Sprint 2 (30/11 a 07/12/2026)** estarão formalmente **Concluídas (Done)** quando:

1. [ ] **[EP-02]** `docs/sdd-lorawan.md` e os esquemas CT-001/CT-002/CT-003 estiverem versionados e validados por `pytest` (Tarefa 2.1).
2. [ ] **[EP-03]** As Seções 3 e 4 estiverem integralmente redigidas, sem *placeholders* (Tarefas 2.2 e 2.3).
3. [ ] **[EP-03]** As Figuras 1 e 2 estiverem incorporadas e referenciadas (Tarefa 2.4).
4. [ ] **[EP-03]** `STRICT_PAGES=1 ./build_paper.sh` retornar `0` com **exatamente 10 páginas**, sem referências indefinidas.
5. [ ] **[EP-03]** O PDF `docs/sbc-papers/entregas/relatorio-parcial-2026-12-08.pdf` tiver sido **submetido em 08/12/2026** e a tag `v0.2-proposta-parcial` publicada.

Com isso, o **Marco 1** estará cumprido. Na **Sprint 3 (08/12 a 14/12/2026)**, os próximos passos consistem em:

1. Implementar o cenário customizado em C++ (`sim-ns3/scenarios/`) recebendo os parâmetros do CT-001 via linha de comando.

2. Implementar `ISpreadingFactorAllocationStrategy` (RANDOM, DISTANCE, ADR, FIXED_SF12) e o `DutyCycleEnforcer` como instrumentação do controle nativo.

3. Implementar o `MetricsTracker`, que emite `packets.csv` e `nodes.csv` conforme o CT-003.

* **Entregável da Sprint:** **PDF do Relatório Parcial (10 páginas SBC) submetido em 08/12/2026**, acompanhado da especificação SDD versionada no repositório.

Links úteis

https://github.com/signetlabdei/lorawan

https://www.nsnam.org/documentation/

https://json-schema.org/specification

https://tikz.dev/
