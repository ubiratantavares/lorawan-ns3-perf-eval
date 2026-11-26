# ADR-001: Versão fixa do ns-3 e compatibilidade com o módulo `lorawan`

- **Status:** Aceito
- **Data:** 2026-11-26
- **Relacionado:** plan.md (matriz de riscos), sprint01.md (Tarefa 1.2)

## Contexto

O módulo `lorawan` (SignetLab/DEI) v0.3.7 declara em `src/lorawan/NS3-VERSION`
compatibilidade com o **ns-3.38**. O projeto compila o módulo sobre o **ns-3.48**
(`sim-ns3/ns-3.48`), exigindo um ajuste local:
`#include "ns3/log.h"` em `model/logical-lora-channel.cc`.
Existe ainda `sim-ns3/ns-3.41`, sem uso documentado.

## Decisão

1. A única versão suportada do simulador é **ns-3.48** com **lorawan 0.3.7**.
2. O módulo reside em `sim-ns3/ns-3.48/src/lorawan` (não em `contrib/`).
3. O patch local de `logical-lora-channel.cc` deve ser mantido e documentado.
4. `sim-ns3/ns-3.41` é considerado legado: não deve ser usado em campanhas e
   pode ser removido do repositório local.

## Consequências

- Mitiga o risco "incompatibilidade de API" do plan.md.
- Resultados são reprodutíveis: a versão deve constar em `metadata.json` (CT-002).
- Atualizar o ns-3 ou o `lorawan` exige novo ADR e reexecução de `./test.py -s lorawan`.
