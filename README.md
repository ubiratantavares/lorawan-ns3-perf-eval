# lorawan-ns3-perf-eval

Avaliação de desempenho de redes LoRaWAN em ns-3 (C++) e Python. Implementação orientada por especificação (SDD), Arquitetura Hexagonal, SOLID e análise estatística baseada na metodologia de Raj Jain. Projeto prático da disciplina Redes de Computadores Sem Fio (UERJ/PEL 2026.2).

## Estrutura

```text
docs/        Especificação, ADRs (docs/adr) e artigos SBC (docs/sbc-papers)
sim-ns3/     ns-3.48 + módulo lorawan 0.3.7 (ver ADR-001)
src/         Plataforma Python hexagonal: core/, ports/, adapters/
configs/     Contratos de entrada (CT-001) e campanhas
data/        Resultados brutos (raw/) e processados (processed/)
tests/       Testes unitários e de integração (pytest)
```

## Requisitos

- Ubuntu 22.04/24.04, gcc/g++ >= 11, cmake >= 3.22, ninja >= 1.10
- Python >= 3.14 e [uv](https://docs.astral.sh/uv/)

## Ambiente Python

```bash
uv sync
uv run ruff format . && uv run ruff check . --fix
uv run mypy src
uv run pytest --cov=src --cov-report=term-missing
```

## Simulador ns-3

```bash
cd sim-ns3/ns-3.48
./ns3 configure --build-profile=optimized --enable-modules=lorawan --enable-tests --enable-examples
./ns3 build -j 4
./test.py -s lorawan
./ns3 run "complete-network-example --nDevices=20 --radius=1000 --appPeriod=10 --simulationTime=60"
```

Nota: o módulo exige `#include "ns3/log.h"` em `src/lorawan/model/logical-lora-channel.cc`.

## Relatório parcial (SBC)

```bash
cd docs/sbc-papers/proposta-parcial && ./build_paper.sh
```

## Status

Sprint 1 concluída (ambiente, ns-3, estrutura hexagonal, esqueleto do relatório). Próximo marco: relatório parcial de 10 páginas em 08/12/2026.
