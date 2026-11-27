# ADR-002: Desenho experimental unificado

- **Status:** Aceito
- **Data:** 2026-11-26
- **Fontes alinhadas:** `docs/md/plan.md` (§2.2, §5), `docs/md/backlog.md` (Sprints 3, 5–7), `docs/sbc-papers/proposta-parcial/proposta.tex` (QP/H)

## Contexto

Os três documentos divergiam em densidades (50–1000 vs. 100–2000), estratégias de SF
(SF12 fixo / aleatório / ADR vs. fixo-uniforme / ADR), raio (fator 2/6 km vs. faixa 1–6 km),
carga (ausente vs. 60/300/600 s) e no tratamento do duty cycle. A inspeção do módulo
`lorawan` 0.3.7 mostrou que o duty cycle por sub-banda e as alocações de SF fixa, aleatória,
por distância e ADR já são nativas.

## Decisão

### Fatorial completo principal (30 pontos)

| Fator | Níveis |
|---|---|
| A — Densidade | 100, 250, 500, 1000, 2000 |
| B — Estratégia de SF | `RANDOM` (uniforme SF7–12), `DISTANCE` (estática por link budget), `ADR` (dinâmica) |
| C — Período de envio | 60 s, 600 s |

**Fixos:** raio de 2 km, 1 gateway, EU868 com 3 canais, payload de 20 B, duty cycle de 1% ligado.

### Experimentos complementares (15 pontos)

- **E-DC:** duty cycle off, com B = ADR, C = 60 s, para todo A (5 pontos; comparado ao ponto equivalente do fatorial).
- **E-R:** raio de 6 km, com B ∈ {DISTANCE, ADR}, C = 600 s, para todo A (10 pontos).

### Validação (testes degenerados)

SF12 fixo para todos; 1 nó (PDR ≈ 100%); 5 nós a 100 m.

### Controle estatístico

- `RngSeed = 1`; `RngRun = 1..30`.
- Warm-up de 10 min descartado; medição ≥ 1 h simulada.
- IC 95% (t-Student); teste t pareado ADR × RANDOM (H2) e DC on × off (H3), com α = 0,05.

### Métricas

PDR, throughput, atraso, energia por pacote útil, taxa de colisão, descartes por duty cycle e JFI.

## Consequências

- Custo: 45 pontos × 30 = **1350 execuções** (paralelizáveis).
- O `DutyCycleEnforcer` (Sprint 3) é instrumentação e configuração, não reimplementação.
- `ISpreadingFactorAllocationStrategy` encapsula os helpers nativos.
- As hipóteses H1 e H2 deixam de fixar limiares numéricos sem fonte (40% e 20 p.p.).
- A matriz executável está em `configs/campaigns/main_factorial.yaml` (formato preliminar do CT-001).
