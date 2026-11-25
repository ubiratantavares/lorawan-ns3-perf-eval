# **Sprint 1 (23/11/2026 a 29/11/2026)**

* **Objetivo da Sprint:** Instalar e validar o ecossistema ns-3 com o módulo LoRaWAN e elaborar a estrutura base do documento de especificação (SDD) e do template SBC.

* **Backlog da Sprint:**

1. *[EP-01]* Provisionar ambiente Linux (Ubuntu LTS), instalar dependências de build (`gcc`, `g++`, `cmake`, `python3-dev`, `ninja`).

2. *[EP-01]* Clonar e compilar a distribuição do **ns-3** e integrar o módulo de simulação `lorawan`.

3. *[EP-01]* Executar e validar o cenário de exemplo padrão (`lora-packet-tracker.cc`) para confirmar a compilação e a geração de traços.

4. *[EP-02]* Criar o repositório Git com a estrutura de diretórios em Arquitetura Hexagonal (`/core`, `/ports`, `/adapters`, `/sim-ns3`, `/analysis`).

5. *[EP-03]* Configurar o template oficial da **SBC** no LaTeX e redigir o esqueleto do Relatório Parcial (Seções 1 e 2: Introdução contextualizada e Definição do Problema).

* **Entregável da Sprint:** Simulador compilado e executando; template LaTeX SBC estruturado; repositório configurado.

## [EP-01] - Tarefa 1.1: Provisionar ambiente Linux (Ubuntu LTS), instalar dependências de build (`gcc`, `g++`, `cmake`, `python3-dev`, `ninja`)

# Guia de Execução Técnica: Provisionamento do Ambiente e Dependências de Build

* **Identificador no Backlog:** `[EP-01] - Tarefa 1.1`

* **Épico:** Infraestrutura e Ambiente ns-3

* **Sprint Vinculada:** Sprint 1 (23/11/2026 a 29/11/2026)

* **Objetivo:** Estabelecer a infraestrutura de compilação C++ e o ambiente Python necessários para o suporte ao **ns-3** e ao módulo **LoRaWAN**, 
atendendo aos critérios de reprodutibilidade e à Definição de Pronto (*Definition of Done - DoD*).

## 1. Pré-Requisitos e Especificações de Plataforma

Para garantir a estabilidade do motor de eventos discretos e a compatibilidade com o sistema de build baseado em CMake/Ninja:

* **Distribuição Recomendada:** **Ubuntu 22.04 LTS (Jammy Jellyfish)** ou **Ubuntu 24.04 LTS (Noble Numbat)** de 64 bits (`x86_64`).

* **Hardware Mínimo Sugerido:**

  * **CPU:** 4 núcleos (ou 4 vCPUs).

  * **Memória RAM:** 8 GB (mínimo recomendado para compilação paralela sem esgotamento de memória).

  * **Armazenamento:** 25 GB livres em partição com sistema de arquivos EXT4.

* **Permissões:** Acesso de superusuário (`sudo`).

## 2. Passo a Passo de Execução

### Passo 1: Atualização dos Repositórios e do Sistema Base

Antes de introduzir novos pacotes, sincronize os índices de pacotes oficiais do Ubuntu e atualize os binários existentes:

```bash
# Sincroniza a lista de pacotes dos repositórios oficiais
sudo apt update

# Aplica as atualizações de segurança e do sistema
sudo apt upgrade -y

# Instala utilitários essenciais de sistema e rede
sudo apt install -y ca-certificates curl gnupg lsb-release
```

### Passo 2: Instalação das Ferramentas Essenciais de Compilação C/C++

O núcleo do ns-3 e suas extensões requerem compiladores C++ modernos 
compatíveis com o padrão C++17 ou superior.

```bash
# Instala o compilador GCC, G++, Make e utilitários da suíte build-essential
sudo apt install -y build-essential gcc g++

# Instala o sistema de build CMake e o gerador Ninja
sudo apt install -y cmake ninja-build ccache
```

* **Nota Técnica:** O `ninja-build` atua como o backend de compilação de alta performance para o CMake, 
otimizando o tempo de build através da paralelização automática. 
O `ccache` permite o cache de artefatos de compilação, acelerando recompilações incrementais.

### Passo 3: Instalação do Ambiente de Desenvolvimento Python

A plataforma analítica e a orquestração em Arquitetura Hexagonal exigem o runtime e os headers de desenvolvimento do Python 3:

```bash
# Instala o interpretador Python 3, headers de desenvolvimento e o gerenciador de pacotes pip
sudo apt install -y python3 python3-dev python3-pip python3-venv
```

### Passo 4: Instalação das Dependências de Suporte do ns-3

Para que os módulos do ns-3 (incluindo modelos de rádio, cálculos matemáticos, manipulação de arquivos PCAP e saída de dados estruturados) 
compilem com todas as funcionalidades habilitadas:

```bash
# Bibliotecas de suporte matemático, serialização e inspeção de pacotes
sudo apt install -y \
    git \
    pkg-config \
    libsqlite3-dev \
    libxml2-dev \
    gsl-bin \
    libgsl-dev \
    tcpdump
```

### Passo 5: Criação e Isolamento do Ambiente Virtual Python (`venv`)

Para assegurar isolamento estrito das dependências analíticas da Arquitetura Hexagonal, reprodutibilidade e alta performance na resolução de pacotes, utiliza-se o uv:

```bash
# 1. Instale o instalador uv no ambiente do usuário (caso ainda não esteja instalado)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Recarregue a sessão do shell para disponibilizar o comando uv no PATH
source ~/.bashrc

# atualizando o uv
uv self update

# Navegue até o diretório raiz do repositório
cd lorawan-ns3-perf-eval

# iniciando novo projeto
uv init .

# Crie o ambiente virtual isolado (.venv) fixando a versão do Python homologada
uv venv .venv --python 3.14

# Ative o ambiente virtual
source .venv/bin/activate

# instalando dependências
uv add --dev mypy ruff pytest pytest-cov mdformat numpy scipy pandas matplotlib seaborn yaml

uv sync

uv run ruff format .

uv run ruff check . --fix

uv run mypy src

uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=80

uv run mdformat docs/ README.md
```

## 3. Matriz de Verificação e Homologação de Versões

Após a execução dos comandos, execute o script de checagem abaixo para validar se todos os componentes atendem às versões mínimas exigidas:

```bash
echo "========================================"
echo "   Verificação do Ambiente de Build     "
echo "========================================"
echo "GCC:        $(gcc --version | head -n 1)"
echo "G++:        $(g++ --version | head -n 1)"
echo "CMake:      $(cmake --version | head -n 1)"
echo "Ninja:      $(ninja --version | head -n 1)"
echo "Git:        $(git --version)"
echo "uv:         $(uv --version)"
echo "Python:     $(python3 --version)"
echo "Python Venv: $(which python3)"
echo "========================================"
```

### Critérios de Aceitação das Versões:

| Ferramenta | Versão Mínima Homologada | Função no Projeto |
| :--- | :--- | :--- |
| **`gcc` / `g++`** | \\(\ge\\) 11.0 (C++17 nativo) | Compilação do motor ns-3 e modelos LoRaWAN |
| **`cmake`** | \\(\ge\\) 3.22 | Sistema de configuração de build |
| **`ninja`** | \\(\ge\\) 1.10 | Execução paralela de compilação em baixo nível |
| **`python3`** | \\(\ge\\) 3.10 | Execução do orquestrador e processamento estatístico |
| **`python3-dev`** | Headers instalados | Suporte a bindings e bibliotecas numéricas nativas |

## 4. Critério de Aceitação / Definition of Done (DoD)

A atividade **[EP-01] - Tarefa 1.1** é considerada **Concluída (Done)** quando:

1. [x] Todos os pacotes listados forem instalados sem erros ou dependências quebradas (`dpkg -l` ou `apt` com código de retorno 0).

2. [x] O comando `g++ -std=c++17` e o `cmake --version` responderem corretamente no terminal.

3. [x] O ambiente virtual Python `.venv` estiver criado e inicializável sem erros de importação.

4. [x] O sistema operacional estiver pronto para receber a clonagem do código-fonte do **ns-3** e a integração do módulo **`lorawan`** (Tarefa 1.2 da Sprint 1).

## [EP-01]  - Tarefa 1.2: Clonar e compilar a distribuição do **ns-3** e integrar o módulo de simulação `lorawan`.

# Guia de Execução Técnica: Clonagem, Integração e Compilação do ns-3 com o Módulo LoRaWAN

* **Identificador no Backlog:** `[EP-01] - Tarefa 1.2`

* **Épico:** Infraestrutura e Ambiente ns-3

* **Sprint Vinculada:** Sprint 1 (23/11/2026 a 29/11/2026)

* **Objetivo:** Baixar a árvore de código-fonte estável do **ns-3**, integrar o módulo de simulação **`lorawan`** como uma biblioteca de contribuição (*contributed module*), 
configurar o sistema de build baseado em **CMake/Ninja** e realizar a compilação completa do núcleo e dos exemplos.

## 1. Visão Geral e Arquitetura de Diretórios

O ns-3 adota o **CMake** como seu sistema oficial de configuração de build e o **Ninja** como o backend de compilação em baixo nível. O subsistema modular do ns-3 permite que 
modelos de rede externos (como o módulo LoRaWAN desenvolvido pela Universidade de Pádua / Magrin et al.) sejam adicionados no diretório `contrib/` sem a necessidade de modificar 
o repositório principal do simulador.

A organização de diretórios seguirá o padrão:

```text
lorawan-ns3-perf-eval/
├── sim-ns3/
│   └── ns-3.48/          # Árvore principal do ns-3 (versão estável)
│     ├── build/             # Artefatos binários compilados (ignorado no Git)
│     ├── src/               # Módulos nativos do ns-3 (wifi, lte, core, etc.)
│     └── contrib/           # Extensões externas
│     └── lorawan/       # Código-fonte do módulo LoRaWAN
```

## 2. Passo a Passo de Execução

### Passo 1: Preparação do Diretório de Simulação

Navegue até a raiz do projeto e crie o espaço dedicado ao motor de simulação C++:

```bash
# 1. Acesse o diretório do repositório
cd ~/lorawan-ns3-perf-eval

# 2. Garanta que o diretório sim-ns3 exista
mkdir -p sim-ns3
cd sim-ns3
```

### Passo 2: Clonagem da Versão Estável do ns-3

Para assegurar estabilidade de API e evitar quebras de compatibilidade com modelos da comunidade, utiliza-se uma versão estável homologada (ex.: **ns-3.41** ou superior com suporte pleno a CMake/C++17):

```bash
# 1. Clone o repositório oficial do ns-3 (versão com tags estáveis)
git clone https://gitlab.com/nsnam/ns-3-dev.git ns-3.48

# 2. Acesse a pasta do simulador
cd ns-3.48

# 3. Fixe a compilação na tag estável da versão ns-3.48
git checkout -b ns-3.48-stable tags/ns-3.48
```

### Passo 3: Integração do Módulo LoRaWAN (`contrib/lorawan`)

O módulo LoRaWAN modela a modulação CSS (*Chirp Spread Spectrum*), a camada MAC Classe A e a lógica de canais com perdas por colisão ortogonal e desvanecimento.

```bash
# 1. Acesse o diretório de módulos externos/contribuição
cd src

# 2. Clone o repositório oficial do módulo LoRaWAN
git clone https://github.com/signetlabdei/lorawan.git lorawan

# 3. Retorne à raiz do ns-3.48
cd ..
```

* **Nota de Compatibilidade:** O módulo `lorawan` depende de bindings nativos de C++ com o núcleo do ns-3 (`core`, `network`, `mobility`, `propagation`, `energy`). 
Ao estar localizado dentro de `contrib/`, o CMake detecta automaticamente o arquivo `contrib/lorawan/CMakeLists.txt` durante o processo de escaneamento de módulos.

### Passo 4: Configuração do Build via CMake com Gerador Ninja

Execute a configuração do ambiente, ativando otimizações para execução rápida de campanhas experimentais (*optimized*) e habilitando o suporte a exemplos e testes:

```bash
# 1. Configure o ns-3 ativando exemplos, testes e usando Ninja como gerador
./ns3 configure \
    --build-profile=optimized \
    --enable-modules=lorawan \
    --enable-tests \
    --enable-examples
```

* **Validação do Output:** Na saída textual gerada pelo comando `./ns3 configure`, verifique o bloco **"Modules built to these directories"**. 
O módulo `lorawan` deve obrigatoriamente constar na lista de **módulos habilitados** (*built modules*). 
Caso apareça como *not built*, certifique-se de que a biblioteca `libgsl-dev` foi instalada no Passo 4 do guia anterior.

### Passo 5: Compilação Paralela com o ns-3 / Ninja

Dispare a compilação de toda a árvore de código-fonte. O script `./ns3` orquestra o `ninja`, alocando todos os núcleos de CPU disponíveis:

```bash
# Compila todos os módulos habilitados e os alvos executáveis
./ns3 build -j 4
```

NOTA: Neste passo foi necessário realizar a inclusão da linha abaixo ao arquivo src/lorawan/model/logical-lora-channel.cc para executar novamente o comando acima.

há uma dependência de inclusão de cabeçalho não declarada explicitamente no código do módulo.

```text
#include "ns3/log.h"
```

*(O processo de compilação costuma levar entre 3 a 8 minutos, dependendo da quantidade de núcleos do processador).*

## 3. Matriz de Verificação e Homologação da Compilação

Para validar que o simulador C++ e a extensão LoRaWAN estão operacionais e vinculados corretamente, execute os seguintes testes formais:

```bash
# 1. Testes básicos do motor do ns-3
./ns3 run hello-simulator
./ns3 run simple-network-example

# 2. Verificação dos testes unitários do módulo LoRaWAN
./test.py -s lorawan

# 3. Execução da suíte completa de testes
./test.py
```

### Critérios de Aceitação da Homologação:

| Item Verificado | Comando / Verificação | Saída Esperada |
| :--- | :--- | :--- |
| **Execução Básica** | `./ns3 run hello-simulator` | Mensagem `"Hello Simulator"` impressa no terminal sem erros de segmentação. |
| **Módulo Detectado** | `./ns3 show modules` | O módulo `lorawan` deve constar listado entre os módulos compilados. |
| **Testes do LoRaWAN** | `./test.py -s lorawan` | Todos os casos de teste do modelo de canal e MAC com status **PASS** (100% de sucesso). |
| **Binários Gerados** | `ls build/lib/libns3*-lorawan*` | Presença das bibliotecas compartilhadas (`.so`) ou estáticas (`.a`) do LoRaWAN. |

## 4. Definição de Pronto (*Definition of Done - DoD*)

A atividade **`[EP-01] - Tarefa 1.2`** é considerada **Concluída (Done)** quando:

1. [x] O repositório do **ns-3.48** estiver clonado e fixado na tag estável no diretório `sim-ns3/ns-3.48/`.
2. [x] O módulo **`lorawan`** estiver presente em `contrib/lorawan/` e integrado sem erros sintáticos de CMake.
3. [x] A compilação completa via `./ns3 build` terminar com código de retorno `0` (sem falhas de linking ou cabeçalhos ausentes).
4. [x] A suíte de testes `./test.py -m lorawan` for executada com sucesso, liberando o ambiente para a **Tarefa 1.3** (*Execução e validação do cenário de exemplo padrão `lora-packet-tracker.cc`*).

## [EP-01]  - Tarefa 1.3: Executar e validar o cenário de exemplo padrão (`complete-network-example.cc`) para confirmar a compilação e a geração de traços.

# Especificação Técnica de Execução: Validação do Cenário Padrão (`complete-network-example.cc`)

* **Identificador no Backlog:** `[EP-01] - Tarefa 1.3`
* **Épico Vinculado:** EP-01 — Infraestrutura e Ambiente ns-3
* **Sprint:** Sprint 1 (23/11/2026 a 29/11/2026)
* **Status:** Pronto para Execução e Homologação
* **Objetivo:** Compilar, parametrizar via linha de comando, executar e auditar o cenário canônico `complete-network-example.cc` do módulo LoRaWAN (`src/lorawan/`), validando o acoplamento do motor de eventos discretos, o modelo de canal rádio com ortogonalidade de *Spreading Factors* (SF) e a extração quantitativa de métricas via `LoraPacketTracker`.

## 1. Identificação do Ambiente Host Homologado

A execução deste procedimento é fundamentada no diagnóstico levantado no ambiente operacional:

| Componente | Especificação Coletada no Host | Papel no Processo de Simulação |
| :--- | :--- | :--- |
| **Sistema Operacional** | Ubuntu 22.04.5 LTS (*Jammy Jellyfish*) | Plataforma base de execução |
| **Kernel Linux** | `6.8.0-149-generic` (x86_64) | Escalonamento e chamadas de baixo nível |
| **Compiladores C/C++** | GCC / G++ `11.4.0` | Suporte ao padrão moderno C++17 |
| **Sistema de Build** | CMake `3.22.1` | Configuração e orquestração do grafo de módulos |
| **Backend de Compilação** | Ninja `1.10.1` | Execução paralela multi-core de compilação |
| **Acelerador de Build** | Ccache `4.5.1` | Cache de objetos binários para recompilação instantânea |
| **Python** | Python `3.14.4` | Ambiente de suporte e scripts auxiliares |
| **Versão do Núcleo ns-3** | **ns-3.48** (conforme `cat VERSION`) | Motor de eventos discretos e escalonador temporal |
| **Versão do Módulo LoRaWAN** | **0.3.7** (conforme `src/lorawan/VERSION`) | Modelagem PHY/MAC LoRaWAN (SignetLab/DEI) |
| **Diretório Raiz de Simulação** | `~/github/projetos/lorawan-ns3-perf-eval/sim-ns3/ns-3.48` | Workspace do repositório local |

## 2. Anatomia do Cenário `complete-network-example.cc`

O arquivo `src/lorawan/examples/complete-network-example.cc` constitui a implementação de referência para redes LPWAN no ns-3. Ele instancia uma pilha de comunicação completa:

```
[End Devices (EDs)] <--- (Canal RF / Perda Log-Dist / Fading) ---> [Gateways (GWs)] <--- (P2P / Ideal) ---> [Network Server (NS)]
         │                                                                │                                          │
         └─────────────────────── LoraPacketTracker Helper ───────────────┴──────────────────────────────────────────┘
```

1. **Topologia Espacial:** Dispositivos finais (*End Devices* - EDs) com distribuição uniforme ou aleatória em uma área circular de raio \\(R\\) ao redor de um Gateway central (ou múltiplos Gateways).
2. **Camada Física e Propagação:**
   * Modulação por chirp (*Chirp Spread Spectrum* - CSS) nas larguras de banda de 125 kHz a 500 kHz.
   * Alocação de fatores de espalhamento (SF7 a SF12).
   * Modelo de interferência co-canal: avaliação de potência para decodificação concorrente ou colisão destrutiva quando dois sinais utilizam o mesmo SF e a diferença de potência não atinge o limiar de captura.
3. **Camada MAC:** Implementação da Classe A do LoRaWAN (temporização estrita de janelas de recepção RX1 e RX2 após transmissões no *uplink*).
4. **Instrumentação (`LoraPacketTracker`):** Mecanismo de rastreamento desacoplado que registra eventos em tempo de execução via *callbacks*, computando o balanço exato entre pacotes transmitidos, recebidos e descartados.

## 3. Passo a Passo de Execução

### Passo 1: Posicionamento no Diretório Raiz do ns-3

Abra o terminal e acerte o diretório de trabalho:

```bash
# 1. Navegue até o diretório do ns-3.48
cd ~/github/projetos/lorawan-ns3-perf-eval/sim-ns3/ns-3.48

# 2. Confirme o caminho absoluto ativo
pwd

# 3. Certifique-se da presença do código-fonte do exemplo
test -f src/lorawan/examples/complete-network-example.cc && echo "Código-fonte localizado com sucesso."
```

### Passo 2: Compilação Específica do Executável

O utilitário `./ns3` integra-se ao CMake e ao Ninja. Dispare a compilação direcionada apenas para o alvo do exemplo:

```bash
# Compila o alvo complete-network-example
./ns3 build complete-network-example
```

* **Comportamento Esperado:** O Ninja verificará os cabeçalhos do módulo `src/lorawan/` e compilará o binário em `build/src/lorawan/examples/ns3.48-complete-network-example-default` (ou caminho equivalente). Com o `ccache 4.5.1` ativo, recompilações subsequentes ocorrerão em frações de segundo.

### Passo 3: Inspeção dos Parâmetros via Linha de Comando (`--PrintHelp`)

Inspecione os argumentos suportados pelo executável:

```bash
./ns3 run "complete-network-example --PrintHelp"
```

Os parâmetros configuráveis expostos pelo executável e seus valores padrão na versão **0.3.7** do módulo LoRaWAN são:

* `--nDevices`: Quantidade total de nós finais (*End Devices*) incluídos na simulação.  
  * *Padrão:* `200` nós.  
  * *Uso nos ensaios:* Variado para avaliar o impacto da densidade (ex.: 50, 100, 200, 500 nós).
* `--radius`: Raio da área circular simulada em metros a partir do Gateway central.  
  * *Padrão:* `6400` metros (6,4 km).  
  * *Uso nos ensaios:* Ajustável para testar alcance e atenuação por distância (ex.: 2000 a 6400 m).
* `--simulationTime`: Tempo lógico total de simulação em segundos.  
  * *Padrão:* `600` segundos (10 minutos lógicos).  
  * *Uso nos ensaios:* Reduzido para testes rápidos (ex.: 120s ou 200s) e estendido para regimes permanentes nas campanhas completas.
* `--appPeriod`: Intervalo médio em segundos entre transmissões periódicas de pacotes por cada nó.  
  * *Padrão:* `600` segundos (1 pacote a cada 10 minutos por nó).  
  * *Uso nos ensaios:* Variável independente de carga oferecida (ex.: 60s, 300s ou 600s).
* `--realisticChannel`: Habilita um modelo de canal mais realista com perdas e sombreamento urbano.  
  * *Padrão:* `false` (utiliza propagação padrão em espaço livre/log-distância).  
  * *Uso nos ensaios:* Alternado para validar o comportamento sob desvanecimento mais severo.
* `--print`: Define se as informações de construções/edifícios (*building information*) devem ser exibidas no log.  
  * *Padrão:* `true`.

*(Nota técnica: parâmetros como `--transientPeriods` e `--nGateways` não estão expostos como argumentos diretos de linha de comando neste exemplo específico, sendo configurados internamente no código C++ ou herdados via atributos globais do ns-3).*

### Passo 4: Execução do Ensaio Controlado de Homologação

Crie um diretório para isolar os artefatos de saída e execute o ensaio com **20 dispositivos**, raio de **1.000 metros** e **60 segundos** de tempo lógico:

```bash
# 1. Cria diretório de traços para a Sprint 1
mkdir -p test_traces

# 2. Executa a simulação canalizando a saída completa para arquivo e terminal
./ns3 run "complete-network-example --nDevices=20 --radius=1000 --appPeriod=10 --simulationTime=60" | tee test_traces/complete_run_output.log
```

### Critérios de Validação Quantitativa (Metodologia de Raj Jain):

1. **Equação de Conservação e Balanço de Pacotes:**
   $$\text{Sent Packets} \ge \text{Received by Gateway}$$
   $$\text{Lost Packets} = \text{Sent Packets} - \text{Received by Gateway}$$
   *O número de pacotes entregues com sucesso ao Gateway não pode exceder o total transmitido pelos nós finais, e a diferença representa as perdas agregadas (colisões co-canal no mesmo SF mais atenuação abaixo da sensibilidade).*

2. **Taxa de Entrega de Pacotes (PDR - Packet Delivery Ratio):**
   $$\text{PDR} = \left( \frac{\text{Received by Gateway}}{\text{Sent Packets}} \right) \times 100$$
   *Para uma topologia circular com 20 a 50 dispositivos em raio de 1.000 a 2.000 m sob tráfego esparso, o PDR nominal deve situar-se entre **75% e 98%**, atestando o funcionamento da quase-ortogonalidade entre fatores de espalhamento distintos (SF7 a SF12).*

3. **Validação da Camada Física (PHY) e Comportamento de Perdas:**
   * **Carga e Interferência Co-canal:** Em distâncias curtas ao Gateway, as perdas decorrem predominantemente de colisões por transmissões concorrentes no mesmo canal e mesmo SF.
   * **Atenuação por Distância:** Em distâncias limítrofes ao raio máximo, a atenuação do modelo *LogDistance* provoca perdas por potência abaixo da sensibilidade do receptor (*Under Sensitivity*).

## 5. Matriz de Verificação e Homologação

| Item | Procedimento de Teste | Critério de Aceitação |
| :--- | :--- | :--- |
| **Linking e Dependências** | `./ns3 build complete-network-example` | Retorno `0` pelo compilador/Ninja sem erros de biblioteca ausente. |
| **Mapeamento CLI** | `./ns3 run "complete-network-example --PrintHelp"` | Exibição da tabela de parâmetros (`--nDevices`, `--radius`, `--appPeriod`, etc.) sem falhas de segmentação. |
| **Execução Funcional** | Execução com 20 nós, período de 10s e 60s de simulação | Simulação conclui até $t = 60\text{ s}$ com código de saída `0`. |
| **Geração de Traços** | Inspeção do `stdout` / log da execução | Saída contendo a contagem de pacotes no formato limpo (`[enviados] [recebidos]`), ex.: `120.000000 111.000000`. |
| **Diagnóstico de Rádio (Opcional)** | Execução com `NS_LOG="LoraPhy"` | Registro detalhado de eventos `StartTx` e `EndTx` quando necessária depuração física. |

## 6. Critério de Aceitação e Definição de Pronto (Definition of Done - DoD)

A atividade **`[EP-01] - Tarefa 1.3`** e o **Épico 01** são considerados formalmente **Concluídos (Done)** quando:

1. [x] O executável `complete-network-example` for compilado com sucesso sob a árvore do **ns-3.48** e módulo **`lorawan 0.3.7`**.
2. [x] O comando responder aos parâmetros via linha de comando (`--nDevices`, `--radius`, `--appPeriod`, `--simulationTime`).
3. [x] A execução controlada for concluída sem interrupções anormais (*segmentation faults* ou *aborts*).
4. [x] A saída padrão (`stdout`) capturada registrar o par de valores numéricos de pacotes gerados e entregues, comprovando a instrumentação do `LoraPacketTracker` e um PDR coerente com a literatura (no teste: $111/120 \rightarrow 92{,}5\%$).
5. [x] A infraestrutura e o ambiente de software estiverem plenamente homologados, liberando o avanço formal para a **Sprint 2** (modelagem formal SDD, contratos CT-001/CT-003 e redação da Proposta Parcial de 10 páginas para o marco de 08/12/2026).

## [EP-02]  - Tarefa 1.4: Criar o repositório Git com a estrutura de diretórios em Arquitetura Hexagonal (`/core`, `/ports`, `/adapters`, `/sim-ns3`, `/analysis`).

# Especificação Técnica de Execução: Estruturação de Diretórios em Arquitetura Hexagonal

* **Identificador no Backlog:** `[EP-02] - Tarefa 1.4`
* **Épico Vinculado:** EP-02 — Governança SDD e Especificação Técnica
* **Sprint:** Sprint 1 (23/11/2026 a 29/11/2026)
* **Status:** Pronto para Execução e Homologação
* **Objetivo:** Estabelecer a topologia de diretórios e pacotes do projeto no repositório Git local (`/home/bira/github/projetos/lorawan-ns3-perf-eval`), materializando os conceitos de **Arquitetura Hexagonal (*Ports & Adapters*)**, **Clean Code**, **SOLID** e separação estrita de responsabilidades entre o motor de eventos discretos em C++ (`sim-ns3`) e o subsistema analítico/orquestrador em Python (`src/core`, `src/ports`, `src/adapters`).

## 1. Diagnóstico do Estado Atual do Repositório

Conforme a inspeção realizada em `/home/bira/github/projetos/lorawan-ns3-perf-eval`, o repositório já possui a infraestrutura base provisionada:

* **Controle de Versão:** Repositório Git ativo (`.git/`, `.gitignore`, `LICENSE`, `README.md`).
* **Gerenciamento Python:** Configurado via `uv` (`pyproject.toml`, `.python-version`, `uv.lock`, `.venv/`).
* **Núcleo ns-3:** Estruturado e homologado (`sim-ns3/` contendo o ns-3.48 e módulo LoRaWAN 0.3.7).
* **Documentação:** Diretório `docs/` existente.
* **Módulos Pendentes de Estruturação Interna:** 
  * O diretório `src/` precisa ser decomposto nas camadas hexagonais (`core/`, `ports/`, `adapters/`).
  * Devem ser criados os diretórios de suporte: `configs/` (para contratos YAML/JSON), `data/` (para persistência isolada de métricas brutas e processadas) e `tests/` (pirâmide de testes unitários e de integração com `pytest`).

## 2. Mapa Arquitetural de Diretórios

A distribuição seguirá o isolamento estrito de dependências:

```
lorawan-ns3-perf-eval/
│
├── docs/                               # Especificação SDD, ADRs e Artigos SBC (LaTeX)
│   ├── adr/                            # Architecture Decision Records
│   └── sbc-papers/                     # Relatórios Parcial (10 p.) e Final (14 p.)
│
├── sim-ns3/                            # Núcleo C++ (ns-3.48 + lorawan 0.3.7)
│   ├── ns-3.48/                        # Árvore do simulador
│   └── custom/                         # Extensões C++ customizadas do projeto
│
├── src/                                # Subsistema Python (Arquitetura Hexagonal)
│   ├── __init__.py
│   ├── core/                           # INSIDE: Domínio Puro e Regras de Negócio
│   │   ├── __init__.py
│   │   ├── domain/                     # Entidades, Value Objects e Enums
│   │   │   └── __init__.py
│   │   └── services/                   # Serviços de Cálculo (PDR, Throughput, Raj Jain)
│   │       └── __init__.py
│   │
│   ├── ports/                          # CONTRATOS: Interfaces Abstratas (DIP)
│   │   ├── __init__.py
│   │   ├── driving/                    # Portas de Entrada (Casos de Uso do Orquestrador)
│   │   │   └── __init__.py
│   │   └── driven/                     # Portas de Saída (Runners e Repositórios)
│   │       └── __init__.py
│   │
│   └── adapters/                       # OUTSIDE: Adaptadores Concretos (I/O, CLI, Gráficos)
│       ├── __init__.py
│       ├── driving/                    # Adaptadores de Entrada (CLI / Scripts de Execução)
│       │   └── __init__.py
│       └── driven/                     # Adaptadores de Saída (Subprocess ns-3, Filesystem, Plots SBC)
│           └── __init__.py
│
├── configs/                            # Contratos de Dados de Entrada (YAML/JSON)
│   └── campaigns/                      # Matrizes de experimentos fatoriais
│
├── data/                               # Armazenamento Isolado de Resultados Experimentais
│   ├── raw/                            # Saídas brutas de simulações (protegido contra sobrescrita)
│   └── processed/                      # Tabelas consolidadas com intervalos de confiança
│
└── tests/                              # Suíte de Testes Automatizados (pytest)
    ├── __init__.py
    ├── unit/                           # Testes unitários do domínio e cálculos
    │   └── __init__.py
    └── integration/                    # Validação de contratos e execução ponta a ponta
        └── __init__.py
```

## 3. Passo a Passo de Execução

Execute os comandos a partir da raiz do projeto:

```bash
cd /home/bira/github/projetos/lorawan-ns3-perf-eval
```

### Passo 1: Criação da Estrutura Hexagonal em `src/`

Crie as divisões das camadas *Inside* (`core`), *Interfaces* (`ports`) e *Outside* (`adapters`), incluindo os arquivos `__init__.py` para que sejam reconhecidos como pacotes regulares de importação:

```bash
# 1. Cria os diretórios da camada de Domínio e Serviços (Core)
mkdir -p src/core/domain src/core/services

# 2. Cria os diretórios das Portas Abstratas (Ports)
mkdir -p src/ports/driving src/ports/driven

# 3. Cria os diretórios dos Adaptadores Concretos (Adapters)
mkdir -p src/adapters/driving src/adapters/driven

# 4. Cria arquivos __init__.py em toda a hierarquia de src
touch src/__init__.py \
      src/core/__init__.py src/core/domain/__init__.py src/core/services/__init__.py \
      src/ports/__init__.py src/ports/driving/__init__.py src/ports/driven/__init__.py \
      src/adapters/__init__.py src/adapters/driving/__init__.py src/adapters/driven/__init__.py
```

### Passo 2: Criação dos Diretórios de Governança, Configurações e Dados

Estruture os diretórios responsáveis por suportar os experimentos, contratos YAML e a persistência de métricas:

```bash
# 1. Cria diretórios de configurações de entrada
mkdir -p configs/campaigns

# 2. Cria diretórios de dados experimentais
mkdir -p data/raw data/processed

# 3. Garante rastreabilidade no Git sem comitar arquivos binários ou dumps pesados
touch data/raw/.gitkeep data/processed/.gitkeep configs/campaigns/.gitkeep
```

### Passo 3: Criação da Estrutura de Testes Automatizados

Prepare a suíte de testes unitários e de integração alinhada com o `pytest`:

```bash
# 1. Cria pastas para testes unitários e de integração
mkdir -p tests/unit tests/integration

# 2. Inicializa os pacotes de teste
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py
```

### Passo 4: Atualização e Blindagem do `.gitignore`

Para assegurar que dados brutos volumosos de simulações extensas, arquivos de build temporários do ns-3 e caches não poluam o repositório Git, adicione as seguintes regras ao seu arquivo `.gitignore`:

```bash
cat << 'EOF' >> .gitignore

# ==========================================
# Isolamento de Dados Experimentais e Builds
# ==========================================
# Permite rastrear pastas de dados, mas ignora arquivos gerados
data/raw/*
!data/raw/.gitkeep
data/processed/*
!data/processed/.gitkeep

# Ignora saídas temporárias de ensaios e logs
sim-ns3/ns-3.48/test_traces/
*.log
*.pcap
*.tr
buildings.txt

# Arquivos temporários e artefatos de zip
zip/
*.zip
*.tar.gz

# Ambientes virtuais e caches Python
__pycache__/
*.py[cod]
.pytest_cache/
EOF
```

### Passo 5: Criação do Teste de Fumaça (*Smoke Test*) do Subsistema Hexagonal

Para validar que o Python (resolvido via `uv`) reconhece a estrutura de pacotes e importa os módulos do `core` sem erros de path, crie um teste unitário mínimo em `tests/unit/test_smoke.py`:

```bash
cat << 'EOF' > tests/unit/test_smoke.py
"""Teste de fumaça para validação da estrutura hexagonal."""

def test_hexagonal_packages_importable():
    import src.core
    import src.ports
    import src.adapters
    assert src.core is not None
    assert src.ports is not None
    assert src.adapters is not None
EOF
```

Execute o teste com o interpretador ativo do ambiente virtual:

```bash
uv run pytest
```

* **Resultado Esperado:** O `pytest` deve localizar o arquivo e emitir `1 passed in X.XXs`.

### Passo 6: Registro e Versionamento no Git

Com a árvore de diretórios concluída e testada, registre as alterações no Git formalizando a entrega da tarefa:

```bash
# 1. Verifica os arquivos criados
git status

# 2. Adiciona os arquivos estruturais ao stage
git add src/ configs/ data/ tests/ .gitignore

# 3. Realiza o commit formal alinhado ao Scrum
git commit -m "feat(arch): estrutura diretorios em arquitetura hexagonal (EP-02 Tarefa 1.4)"
```

## 4. Matriz de Verificação e Homologação

| Verificação | Procedimento | Critério de Aceitação |
| :--- | :--- | :--- |
| **Hierarquia de Pastas** | `ls -R src/` | Presença confirmada de `core/`, `ports/` e `adapters/`. |
| **Isolamento de Dados** | `git check-ignore data/raw/teste.csv` | Deve retornar o arquivo como ignorado pelo `.gitignore`. |
| **Resolução de Módulos** | `uv run pytest` | Teste de fumaça executando com 100% de sucesso. |
| **Histórico Git** | `git log -1 --oneline` | Commit formal registrado com mensagem descritiva. |

## 5. Definição de Pronto (*Definition of Done - DoD*)

A atividade **`[EP-02] - Tarefa 1.4`** é considerada **Concluída (Done)** quando:

1. [x] A estrutura de diretórios em Arquitetura Hexagonal estiver materializada sob `src/`.
2. [x] Os diretórios de configuração (`configs/`), persistência (`data/`) e testes (`tests/`) estiverem criados com seus respectivos marcadores `.gitkeep`.
3. [x] O arquivo `.gitignore` estiver configurado para blindar o repositório contra dados brutos e traços pesados de simulação.
4. [x] O comando `uv run pytest` validar a importabilidade dos pacotes.
5. [x] O commit estiver efetuado no branch de trabalho, finalizando a parte de infraestrutura e abrindo caminho para a **Tarefa 1.5** (*Configuração do template oficial SBC no LaTeX e redação do Relatório Parcial*).

## [EP-03]  - Tarefa 1.5: Configurar o template oficial da **SBC** no LaTeX e redigir o esqueleto do Relatório Parcial (Seções 1 e 2: Introdução contextualizada e Definição do Problema).

# Especificação Técnica de Execução: Template Oficial SBC e Redação do Esqueleto do Relatório Parcial

* **Identificador no Backlog:** `[EP-03] - Tarefa 1.5`
* **Épico Vinculado:** EP-03 — Proposta / Relatório Parcial (10 págs SBC)
* **Sprint Vinculada:** Sprint 1 (23/11/2026 a 29/11/2026)
* **Marco Acadêmico:** Entrega do Relatório Parcial em **08/12/2026** (Fim da Sprint 2)
* **Restrição Normativa:** **Exatamente 10 páginas** no formato da Sociedade Brasileira de Computação (SBC), em conformidade com as diretrizes da fonte `trcsf26-2v1.pdf`.
* **Objetivo da Tarefa:** Configurar o pacote oficial da SBC no ambiente LaTeX local (`docs/sbc-papers/proposta-parcial/`), estabelecer a folha de estilo e a bibliografia BibTeX, e redigir o texto das **Seções 1 e 2** (Introdução contextualizada e Definição formal do Problema com hipóteses experimentais), preparando o documento para a complementação das Seções 3, 4 e 5 durante a Sprint 2.

## 1. Distribuição de Páginas e Metas Editoriais da Proposta (10 Páginas SBC)

Para assegurar o cumprimento rigoroso do limite de 10 páginas exigido na disciplina, o documento da Proposta Parcial é orçado conforme a matriz abaixo:

| Seção do Artigo SBC | Escopo Temático | Meta de Extensão | Sprint Alocada |
| :--- | :--- | :---: | :---: |
| **Cabeçalho & Resumo / Abstract** | Título, identificação institucional (UERJ/PEL), resumo e *abstract* com palavras-chave. | **0,5 pág.** | **Sprint 1 (Tarefa 1.5)** |
| **1. Introdução e Justificativa** | Cenário LPWAN/IoT, modulação LoRa, arquitetura LoRaWAN e motivação. | **1,5 págs.** | **Sprint 1 (Tarefa 1.5)** |
| **2. O Problema de Pesquisa** | Gargalo de escalabilidade do ALOHA, colisões co-canal, ortogonalidade imperfeita e hipóteses. | **1,5 págs.** | **Sprint 1 (Tarefa 1.5)** |
| **3. Revisão Bibliográfica e Soluções** | Estado da arte em ADR, modelos de interferência e simulação no ns-3. | **2,5 págs.** | Sprint 2 (Tarefa 2.2) |
| **4. Metodologia de Avaliação Proposta** | Projeto experimental (Raj Jain), variáveis, métricas HB/LB e matriz fatorial. | **2,5 págs.** | Sprint 2 (Tarefa 2.3) |
| **5. Referências Bibliográficas** | Fontes científicas formatadas estritamente nas normas da SBC. | **1,5 págs.** | Sprint 2 (Tarefa 2.5) |
| **TOTAL RIGOROSO DA PROPOSTA** | — | **10,0 págs.** | — |

## 2. Passo a Passo de Execução

### Passo 1: Posicionamento no Diretório e Download dos Arquivos Oficiais da SBC

Navegue até a pasta de relatórios do projeto e configure os arquivos do pacote da SBC recomendados na fonte `trcsf26-2v1.pdf`:

```bash
# 1. Acesse a pasta de relatórios parciais no repositório local
cd /home/bira/github/projetos/lorawan-ns3-perf-eval/docs/sbc-papers/proposta-parcial

# 2. Baixe o pacote oficial de publicação da SBC
wget https://www.sbc.org.br/wp-content/uploads/2024/07/modelosparapublicaodeartigos.zip -O sbc_template.zip

# 3. Descompacte o pacote e extraia a classe de estilo (sbc.bst e sbc-template.sty)
unzip -q sbc_template.zip
cp modelosparapublicaodeartigos/LaTeX/sbc.bst .
cp modelosparapublicaodeartigos/LaTeX/sbc-template.sty .

# 4. Limpe os temporários do zip
rm -rf sbc_template.zip modelosparapublicaodeartigos

# 5. Crie a pasta para receber as figuras dos diagramas da proposta
mkdir -p figures
```

### Passo 2: Estruturação do Arquivo de Bibliografia (`referencias.bib`)

Crie o arquivo `referencias.bib` contendo as fontes científicas e metodológicas essenciais para ancorar a introdução, o problema e a metodologia (incluindo Raj Jain, Stallings, Tanenbaum e a literatura clássica de LoRaWAN):

```bibtex
@book{jain1991art,
  author    = {Raj Jain},
  title     = {The Art of Computer Systems Performance Analysis: Techniques for Experimental Design, Measurement, Simulation, and Modeling},
  publisher = {John Wiley \& Sons},
  address   = {New York, USA},
  year      = {1991}
}

@book{stallings2005wireless,
  author    = {William Stallings},
  title     = {Wireless Communications \& Networks},
  edition   = {2nd},
  publisher = {Pearson Prentice Hall},
  year      = {2005}
}

@book{tanenbaum2021redes,
  author    = {Andrew S. Tanenbaum and Nick Feamster and David J. Wetherall},
  title     = {Redes de Computadores},
  edition   = {6ª},
  publisher = {Pearson},
  address   = {São Paulo, Brasil},
  year      = {2021}
}

@article{magrin2017performance,
  author    = {Davide Magrin and Marco Centenaro and Andrea Zanella},
  title     = {Performance Evaluation of {LoRa} Networks in a Smart City Scenario},
  journal   = {IEEE Transactions on Wireless Communications},
  volume    = {16},
  number    = {12},
  pages     = {8147--8159},
  year      = {2017},
  publisher = {IEEE}
}

@article{adelantado2017understanding,
  author    = {Ferran Adelantado and Xavier Vilajosana and Pere Tuset-Peiro and Borja Martinez and Joan Meli{\a}-Segu{\'\i} and Thomas Watteyne},
  title     = {Understanding the Limits of {LoRaWAN}},
  journal   = {IEEE Communications Magazine},
  volume    = {55},
  number    = {9},
  pages     = {34--40},
  year      = {2017},
  publisher = {IEEE}
}

@article{bor2016lora,
  author    = {Martin Bor and Utz Roedig and Thiemo Voigt and Juan M. Alonso},
  title     = {Do {LoRa} Low-Power Wide-Area Networks Scale?},
  booktitle = {Proceedings of the 19th ACM International Conference on Modeling, Analysis and Simulation of Wireless and Mobile Systems (MSWiM)},
  pages     = {59--67},
  year      = {2016}
}

@manual{lorawan_spec_v103,
  title        = {{LoRaWAN} 1.0.3 Specification},
  organization = {LoRa Alliance},
  year         = {2018},
  note         = {Standard Document}
}
```

### Passo 3: Criação do Documento Mestre `proposta.tex` (Seções 1 e 2)

Crie o arquivo principal `proposta.tex` estruturado rigorosamente com base no template da SBC, implementando a contextualização institucional da UERJ/PEL e a redação integral das Seções 1 e 2:

```latex
\documentclass[12pt]{article}

\usepackage{sbc-template}
\usepackage{graphicx}
\usepackage{url}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{microtype}

\sloppy

\title{Avaliação de Desempenho e Limites de Escalabilidade de Redes LoRaWAN sob Condições de Interferência no Simulador ns-3}

\author{Ubirajara A. Silva\inst{1}}

\address{Programa de Pós-Graduação em Engenharia Eletrônica (PEL/DETEL/FEN)\\
  Universidade do Estado do Rio de Janeiro (UERJ) -- Rio de Janeiro, RJ -- Brasil
  \email{ubirajara@eng.uerj.br}
}

\begin{document}

\maketitle

\begin{abstract}
This paper presents the research proposal for performance evaluation and scalability analysis of LoRaWAN networks using discrete-event simulation in ns-3. As Internet of Things (IoT) deployments grow in smart cities, the ALOHA-based medium access control encounters severe packet collisions and co-channel interference. This work investigates the impact of network density, spreading factor allocation, and regulatory duty cycles on packet delivery ratio (PDR) and throughput. A rigorous performance evaluation methodology based on Raj Jain's framework is established, integrating a Hexagonal Architecture orchestrator in Python and C++ engine extensions under Specification-Driven Development (SDD).
\end{abstract}

\begin{resumo}
Este documento apresenta a proposta de pesquisa para avaliação de desempenho e análise dos limites de escalabilidade de redes LoRaWAN utilizando simulação de eventos discretos no ns-3. Com a massificação de dispositivos na Internet das Coisas (IoT), o mecanismo de acesso ao meio desprovido de detecção de portadora (ALOHA puro) sofre degradação acentuada devido a colisões e interferência co-canal. Este trabalho investiga o impacto da densidade de dispositivos, da estratégia de alocação de Fatores de Espalhamento (SF) e do controle de duty cycle sobre a taxa de entrega de pacotes (PDR) e a vazão agregada. Define-se uma metodologia estrita baseada no arcabouço de Raj Jain, associada a uma plataforma orquestradora em Arquitetura Hexagonal (Python/C++) governada por Specification-Driven Development (SDD).
\end{resumo}

% =========================================================================
% SEÇÃO 1: INTRODUÇÃO E JUSTIFICATIVA
% =========================================================================
\section{Introdução e Justificativa}
\label{sec:introducao}

A consolidação do paradigma da Internet das Coisas (\textit{Internet of Things} -- IoT) impôs demandas arquiteturais singulares sobre a infraestrutura de telecomunicações sem fio \cite{tanenbaum2021redes}. Diferentemente das redes locais sem fio convencionais voltadas para taxas elevadas de transmissão em curtas distâncias (como a família IEEE 802.11) ou das redes móveis celulares orientadas à mobilidade contínua, uma vasta gama de aplicações urbanas e industriais requer a transmissão esparsa de pequenos volumes de dados por nós de baixíssimo custo energeticamente autônomos por anos \cite{stallings2005wireless, adelantado2017understanding}.

Nesse contexto emergiram as tecnologias de redes de longa distância e baixa potência (\textit{Low Power Wide Area Networks} -- LPWAN). Dentre os padrões abertos consolidados no mercado e na academia, destaca-se o \textbf{LoRaWAN}, concebido pela \textit{LoRa Alliance} \cite{lorawan_spec_v103}. O LoRaWAN adota na camada física a modulação proprietária LoRa (\textit{Long Range}), baseada no espalhamento espectral por chaveamento de frequência contínuo (\textit{Chirp Spread Spectrum} -- CSS). Essa técnica permite robustez contra atenuação severa e desvanecimento multitrajeto, operando tipicamente nas faixas não licenciadas \textit{Industrial, Scientific and Medical} (ISM) em frequências sub-GHz (868~MHz na Europa e 915~MHz nas Américas) \cite{magrin2017performance}.

A camada de controle de acesso ao meio (MAC) do LoRaWAN opera segundo uma topologia em estrela de estrelas (\textit{star-of-stars}), na qual nós finais (\textit{End Devices} -- EDs) comunicam-se em salto único diretamente com um ou múltiplos \textit{Gateways} (GWs). Os gateways, por sua vez, atuam como pontes bidirecionais transparentes, reencaminhando os quadros de rádio encapsulados em conexões de alta capacidade (IP/Ethernet) para um Servidor de Rede centralizado (\textit{Network Server} -- NS) \cite{lorawan_spec_v103}. Na classe fundamental de operação (Classe A), o acesso ao canal de subida (\textit{uplink}) ocorre sob o princípio de contenção assíncrona do protocolo ALOHA puro: o dispositivo transmite imediatamente no instante em que sua carga útil é gerada, abrindo em seguida duas janelas temporais estritas de recepção (RX1 e RX2) para eventuais confirmações ou comandos descendentes (\textit{downlink}) \cite{adelantado2017understanding}.

A relevância e justificativa deste trabalho residem no fato de que, embora a modulação LoRa ofereça quase-ortogonalidade entre seus seis fatores de espalhamento (\textit{Spreading Factors} -- SF7 a SF12), a ausência de mecanismos de escuta de portadora (como o CSMA/CA) torna o sistema extremamente vulnerável à saturação à medida que a densidade de transmissores se aproxima de dezenas de milhares de dispositivos por gateway \cite{bor2016lora}. Além disso, regulamentações governamentais de espectro impõem restrições de tempo de ocupação no ar (\textit{duty cycle} máximo de 1\% por sub-banda), o que constrange severamente a capacidade do canal e os algoritmos de adaptação de taxa (\textit{Adaptive Data Rate} -- ADR) \cite{magrin2017performance}.

Conforme as diretrizes da disciplina Redes de Computadores Sem Fio (PEL/DETEL/FEN -- UERJ, período 2026/2), este projeto atende formalmente à categoria de projetos de avaliação de desempenho por simulação computacional. A pesquisa apoia-se no simulador de eventos discretos \textbf{ns-3} (versão 3.48), acoplado ao módulo oficial aberto \texttt{lorawan} (SignetLab/DEI). O desenvolvimento de extensões de protocolo não implementadas segue os padrões da engenharia de software de qualidade, empregando Desenvolvimento Orientado por Especificação (\textit{Specification-Driven Development} -- SDD), princípios SOLID, Clean Code e Arquitetura Hexagonal (\textit{Ports \& Adapters}) para desacoplamento entre o motor C++ e a plataforma analítica em Python.

% =========================================================================
% SEÇÃO 2: O PROBLEMA DE PESQUISA
% =========================================================================
\section{O Problema de Pesquisa}
\label{sec:problema}

O desafio central enfrentado em redes LPWAN diz respeito aos \textbf{limites de escalabilidade e confiabilidade da entrega de pacotes} em cenários massivos. A premissa de acesso aleatório do ALOHA puro, associada à longa duração dos pacotes no ar (\textit{Time-on-Air} -- ToA), gera uma probabilidade crescente de sobreposição temporal e espectral de sinais \cite{adelantado2017understanding, bor2016lora}. 

\subsection{Degradação da Ortogonalidade e Colisões Co-Canal}
A teoria de modulação LoRa postula que sinais transmitidos simultaneamente em uma mesma frequência central não sofrem interferência destrutiva mútua se modulados com Fatores de Espalhamento distintos ($SF_i \neq SF_j$). Contudo, em condições empíricas e simulações com modelos de rádio de alta fidelidade, os SFs exibem apenas uma \textit{quase-ortogonalidade}. A presença de um sinal concorrente de alta potência em $SF_{12}$ pode despolarizar e degradar a relação sinal-ruído-interferência (SINR) de uma transmissão próxima em $SF_7$, violando a premissa de isolamento perfeito \cite{bor2016lora}.

Além disso, transmissões concorrentes no mesmo canal e no mesmo SF colidem fatalmente, a menos que a diferença de potência de recepção entre os sinais exceda o limiar do chamado \textbf{efeito de captura} (\textit{capture effect}). Nesse cenário, o pacote mais fraco é destruído, enquanto o mais forte pode, eventualmente, ser demodulado pelo gateway. Nós situados distantes da estação rádio-base operam historicamente com SFs mais elevados (maior tempo de integração e sensibilidade aumentada), resultando em tempos no ar de até dez vezes superiores aos nós próximos (operando em SF7), amplificando exponencialmente a janela de colisão global da rede \cite{magrin2017performance}.

\subsection{Questões de Pesquisa (QP)}
A formulação do problema traduz-se nas seguintes questões científicas investigadas neste estudo:
\begin{itemize}
    \item \textbf{QP-01:} Em que ponto de densidade de dispositivos (100 a 2000 nós) o mecanismo ALOHA do LoRaWAN atinge o colapso de vazão e degradação crítica da Taxa de Entrega de Pacotes (PDR)?
    \item \textbf{QP-02:} De que maneira a alocação dinâmica de SF através de algoritmos de ADR atenua ou agrava o número de colisões co-canal em comparação com uma distribuição uniforme estática de SFs?
    \item \textbf{QP-03:} Qual é o impacto isolado da restrição regulatória de \textit{duty cycle} (1\%) na ocorrência de descartes locais na fila MAC dos transmissores sob tráfego periódico contínuo?
    \item \textbf{QP-04:} Como se comportam os índices de equidade de acesso à rede (\textit{Jain's Fairness Index}) entre nós localizados no raio interno da célula frente aos nós de borda?
\end{itemize}

\subsection{Hipóteses Experimentais}
Com base no arcabouço quantitativo de Raj Jain \cite{jain1991art}, este estudo formula as seguintes hipóteses de trabalho a serem validadas experimentalmente no ns-3:
\begin{itemize}
    \item \textbf{Hipótese $H_1$:} A taxa de entrega de pacotes ($\mathrm{PDR}$) decresce de forma exponencial com o aumento linear da densidade de dispositivos finais sob alocação aleatória de SF, estabilizando-se em patamares inferiores a 40\% para populações superiores a 1000 nós em raio de 2~km.
    \item \textbf{Hipótese $H_2$:} A utilização de estratégias dinâmicas de alocação baseadas na intensidade do sinal recebido (RSSI/ADR) promove um ganho estatisticamente significativo ($\alpha = 0{,}05$) de ao menos 20 pontos percentuais no PDR agregado em relação à alocação uniforme, decorrente do confinamento da maioria dos nós em fatores de espalhamento de baixo tempo no ar (SF7 e SF8).
    \item \textbf{Hipótese $H_3$:} A conformidade estrita com o limite de 1\% de \textit{duty cycle} introduz uma taxa de descarte determinística por esgotamento de janela de tempo que mascara as perdas puramente atribuídas a colisões no canal de rádio.
\end{itemize}

% =========================================================================
% SEÇÕES SUBSEQUENTES (ESTRUTURAÇÃO PREPARATÓRIA DA SPRINT 2)
% =========================================================================
\section{Revisão Bibliográfica e Levantamento das Soluções}
\label{sec:revisao}
\textit{[Seção a ser desenvolvida na Sprint 2 -- Meta: 2,5 páginas. Abordará os mecanismos de adaptação de taxa (ADR), modelagem de interferência co-canal em LPWAN e os recursos do módulo lorawan do ns-3].}

\section{Metodologia Proposta para Avaliação de Desempenho}
\label{sec:metodologia}
\textit{[Seção a ser desenvolvida na Sprint 2 -- Meta: 2,5 páginas. Detalhará o desenho experimental segundo Raj Jain: variáveis independentes, métricas HB e LB, modelo de propagação urbana, controle de sementes e Arquitetura Hexagonal].}

% =========================================================================
% REFERÊNCIAS BIBLIOGRÁFICAS
% =========================================================================
\bibliographystyle{sbc}
\bibliography{referencias}

\end{document}
```

### Passo 4: Script de Compilação Automatizada e Auditoria de Páginas

Crie o script de automação `build_paper.sh` no diretório da proposta para compilar o documento LaTeX via terminal, gerando o PDF e auditando a contagem de páginas gerada:

```bash
cat << 'EOF' > build_paper.sh
#!/bin/bash
set -e

echo "=== Compilando Documento SBC (LaTeX + BibTeX) ==="
pdflatex -interaction=nonstopmode proposta.tex > /dev/null
bibtex proposta > /dev/null
pdflatex -interaction=nonstopmode proposta.tex > /dev/null
pdflatex -interaction=nonstopmode proposta.tex > /dev/null

echo "=== Compilação Concluída com Sucesso ==="
TOTAL_PAGES=$(pdfinfo proposta.pdf | grep Pages | awk '{print $2}')
echo "PDF Gerado: proposta.pdf"
echo "Total Atual de Páginas: $TOTAL_PAGES páginas (Meta Parcial: Seções 1 e 2 estruturadas)"
EOF

# Concede permissão de execução ao script
chmod +x build_paper.sh
```

Execute a compilação:

```bash
./build_paper.sh
```

### Passo 5: Registro e Versionamento no Repositório Git

Com os arquivos do template SBC configurados, o código LaTeX redigido e a compilação gerando o PDF sem erros de referências ou estilos, registre as alterações no branch principal:

```bash
# 1. Navegue até a raiz do projeto
cd /home/bira/github/projetos/lorawan-ns3-perf-eval

# 2. Adicione os arquivos gerados em docs/sbc-papers/proposta-parcial
git add docs/sbc-papers/proposta-parcial/

# 3. Realize o commit formal da Tarefa 1.5
git commit -m "docs(sbc): configura template oficial e redige secoes 1 e 2 do relatorio parcial (EP-03 Tarefa 1.5)"
```

## 3. Matriz de Verificação e Homologação da Tarefa 1.5

| Item Avaliado | Procedimento de Verificação | Critério de Aceitação |
| :--- | :--- | :--- |
| **Folha de Estilo SBC** | Verificação dos arquivos `sbc-template.sty` e `sbc.bst` | Arquivos presentes no mesmo diretório do arquivo `.tex` fonte. |
| **Cabeçalho Institucional** | Inspeção visual da primeira página do PDF | Título do trabalho, identificação do autor, afiliação (PEL/DETEL/FEN - UERJ) e e-mail. |
| **Texto da Seção 1** | Leitura de `sec:introducao` | Contextualização de LPWAN, modulação LoRa (CSS), topologia estrela de estrelas, classes A/B/C e justificativa UERJ/ns-3. |
| **Texto da Seção 2** | Leitura de `sec:problema` | Detalhamento do ALOHA puro, efeito de captura, perda de ortogonalidade de SF, Questões QP-01 a QP-04 e Hipóteses H1 a H3. |
| **Citações e BibTeX** | Verificação de `referencias.bib` | Citações compilando sem referências com interrogação `[?]` e formatadas no padrão alfabético da SBC. |
| **Compilação sem Alertas** | Execução de `./build_paper.sh` | Retorno `0` com geração do artefato `proposta.pdf`. |

## 4. Definição de Pronto (*Definition of Done - DoD*) da Tarefa 1.5 e Fechamento da Sprint 1

A atividade **`[EP-03] - Tarefa 1.5`** e a **Sprint 1 (23/11 a 29/11/2026)** estão consideradas formalmente **Concluídas (Done)**:

1. [x] **[EP-01]** Ambiente Linux Ubuntu 22.04 LTS provisionado, compiladores C++17 e `uv` ativos.
2. [x] **[EP-01]** ns-3.48 e módulo LoRaWAN 0.3.7 compilados com sucesso.
3. [x] **[EP-01]** Cenário canônico executado (`120.000000 111.000000` pacotes, PDR de 92,5%) e mecanismo de saída dissecado.
4. [x] **[EP-02]** Repositório Git estruturado nas camadas de Arquitetura Hexagonal (`core/`, `ports/`, `adapters/`, `configs/`, `data/`, `tests/`) com teste de fumaça aprovado no `pytest`.
5. [x] **[EP-03]** Template oficial da SBC configurado em LaTeX, com o arquivo BibTeX populado e as **Seções 1 e 2 integralmente redigidas e compiladas no PDF**.

Com isso, a **Sprint 1 está 100% finalizada**. Na **Sprint 2 (30/11 a 07/12/2026)**, os próximos passos consistem em:

1. Formalizar a especificação técnica central (`docs/sdd-lorawan.md`) com os contratos CT-001 e CT-003.

2. Redigir a Seção 3 (Revisão Bibliográfica) e a Seção 4 (Metodologia segundo Raj Jain) no LaTeX.

3. Ajustar a densidade de texto e figuras para fechar **rigorosamente as 10 páginas do Relatório Parcial** para a entrega de **08/12/2026**.

* **Entregável da Sprint:** Simulador compilado e executando; template LaTeX SBC estruturado; repositório configurado.



Links úteis

https://github.com/signetlabdei/lorawan

https://github.com/signetlabdei/lorawan/releases

https://github.com/signetlabdei/lorawan/releases/tag/v0.3.7

https://apps.nsnam.org/app/lorawan/

Configuração do ambiente de desenvolvimento

```bash
lsb_release -a
```

No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 22.04.5 LTS
Release:	22.04
Codename:	jammy

```bash
uname -r
```

6.8.0-149-generic

```bash
gcc --version
```

gcc (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0
Copyright (C) 2021 Free Software Foundation, Inc. This is free software; see the source for copying conditions.  There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

```bash
g++ --version
```

g++ (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0
Copyright (C) 2021 Free Software Foundation, Inc. This is free software; see the source for copying conditions.  There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.


```bash
cmake --version
```

cmake version 3.22.1
CMake suite maintained and supported by Kitware (kitware.com/cmake).

```bash
python3.14 --version
```

Python 3.14.4

```bash
ninja --version
```

1.10.1

```bash
ccache --version
```

ccache version 4.5.1
Features: file-storage http-storage redis-storage

Copyright (C) 2002-2007 Andrew Tridgell
Copyright (C) 2009-2021 Joel Rosdahl and other contributors

See <https://ccache.dev/credits.html> for a complete list of contributors.

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later
version.


```bash
cat VERSION
```

3.48

```bash
cat src/lorawan/VERSION
```

0.3.7

```bash
cat src/lorawan/NS3-VERSION
```

release ns-3.38
