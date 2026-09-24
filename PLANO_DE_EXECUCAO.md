# Plano de Execução — Trabalho de ER (LFA, 1º Bimestre)

> Documento de handoff para o agente que vai implementar. **Nada de código foi escrito ainda.**
> Fonte das regras: enunciado do professor + `../prova_daniel/GUIA_SINTAXE_EXPRESSOES_REGULARES_TRABALHO_LFA - FINAL.pdf`.
> Datas: **Etapa 1 (planilha) até 26/09/2026** · **Entrega final + apresentação 30/09/2026**.

---

## 0. Regra de ouro (ler antes de tudo)

Para **cada** ER, estas cinco coisas têm de representar **exatamente a mesma linguagem**:

1. ER formal (notação da disciplina: `|`, concatenação, `*`, `+`, `?`, `( )`, `ε`, `[a-z]`, `r{m}`, `r{m,n}`);
2. a sintaxe mostrada nos slides/relatório;
3. o padrão no código-fonte (copiado caractere por caractere);
4. os casos de teste;
5. o AFNε.

Divergência = erro conceitual (palavras do guia). Por isso o plano abaixo faz o **programa verificar sozinho** essa equivalência: cada cadeia de teste é avaliada pelo `re.fullmatch` **e** por um simulador de AFNε, e os dois resultados precisam coincidir.

**Proibido nas ERs avaliadas** (guia, pág. 3): retroreferências (`\1`), recursão, condicionais, lookahead/lookbehind. Evitar também `.`, `\d`, `\w`, `\s` — usar classes explícitas (`[0-9]`, `[A-Z]`) para o alfabeto ficar declarado.

---

## 1. Tema do projeto

**Título:** *DecodMETAR — Validador e decodificador de boletins meteorológicos aeronáuticos (METAR/SPECI) com Expressões Regulares*

**Problema:** o METAR é o boletim meteorológico que aeroportos emitem a cada hora, em formato codificado e compacto, por exemplo:

```
METAR SBBE 241200Z 09010KT 9999 -RA FEW020 SCT100 30/24 Q1011
```

Para um leigo (ou estudante de aviação) ele é ilegível, e um boletim com erro de digitação pode passar despercebido. O programa:

- **Entrada:** um boletim digitado pelo usuário, ou um arquivo `.txt` com vários boletins (um por linha).
- **Processamento:** separa o boletim em grupos (tokens por espaço), classifica cada grupo com uma das 8 ERs, valida a ordem dos grupos e extrai os campos.
- **Saída:** tradução em português ("Vento de 090° a 10 nós", "Visibilidade ≥ 10 km", "Chuva fraca", "Poucas nuvens a 2.000 pés", "Temperatura 30 °C, orvalho 24 °C", "Pressão 1011 hPa"), além da lista de grupos inválidos/não reconhecidos com mensagem clara. No modo arquivo, também um resumo (quantos válidos, inválidos, e quais erros).

**Por que esse tema:** é original (dificilmente outra equipe escolhe), tem dado real e estruturado, e as ERs são não triviais (intervalos numéricos como dia 01–31, hora 00–23, direção 000–360, uniões de códigos, opcionais, repetições). Contexto local: SBBE é o aeroporto de Belém.

**Linguagem:** Python 3.12 (já instalado: `Python 3.12.3`). **Zero dependências externas** (verificado: `pytest`, `graphviz`, `dot` e `pandoc` **não** estão instalados). Usar só a biblioteca padrão: `re`, `unittest`, `argparse`, `pathlib`, `dataclasses`.

> Se o usuário (Manito) quiser outro tema, a estrutura do plano (módulos, fichas, AFNε, testes) continua valendo; só trocam as ERs.

---

## 2. Estrutura da pasta (criar tudo dentro de `trabalho_er_metar/`)

```
trabalho_er_metar/
├── PLANO_DE_EXECUCAO.md          ← este arquivo (manter)
├── README.md                     ← instalação, execução, exemplos, uso de IA
├── CONTRIBUICOES.md              ← quem fez o quê (tabela preenchível)
├── requirements.txt              ← vazio com comentário "somente biblioteca padrão"
├── main.py                       ← ponto de entrada (menu interativo + CLI)
├── decodmetar/
│   ├── __init__.py
│   ├── padroes.py                ← AS 8 ERs (única fonte da verdade dos padrões)
│   ├── decodificador.py          ← tokenização, classificação, extração, tradução
│   ├── mensagens.py              ← textos de saída/erro em português
│   └── afne/
│       ├── __init__.py
│       ├── automato.py           ← classe AFNe + fecho-ε + simulação com traço
│       ├── definicoes.py         ← os 8 AFNε como dados (estados, transições, ε)
│       └── diagramas.py          ← gera Mermaid (.md) e Graphviz (.dot) a partir das definições
├── tests/
│   ├── __init__.py
│   ├── casos.py                  ← tabela de cadeias aceitas/rejeitadas por ER (seção 4)
│   ├── test_padroes.py           ← regex aceita/rejeita o esperado
│   ├── test_afne.py              ← AFNε aceita/rejeita o esperado + equivalência regex×AFNε
│   └── test_decodificador.py     ← boletins completos, entradas vazias/invalidas
├── dados/
│   ├── metar_validos.txt         ← ~10 boletins bem formados
│   ├── metar_com_erros.txt       ← ~8 boletins com erros variados
│   └── metar_misto.txt           ← mistura + linhas em branco (para demo)
└── docs/
    ├── EXPRESSOES_REGULARES.md   ← as 8 fichas completas (seção 5)
    ├── afne/                     ← ER01.md … ER08.md (Mermaid) + ER01.dot … ER08.dot
    ├── RELATORIO_TECNICO.md      ← fonte do relatório (converter para PDF)
    ├── APRESENTACAO_ROTEIRO.md   ← roteiro slide a slide (seção 8)
    └── ETAPA1_PLANILHA.md        ← texto pronto para colar na planilha do professor
```

Estilo de código: nomes em português (como nos arquivos já existentes do Manito, ex.: `roboEpsilon.py` usa `fecho`, `estados`, `funcao`, `inicial`, `aceitacao`), funções curtas, docstrings curtas, sem excesso de comentários.

---

## 3. As 8 Expressões Regulares

Todas usadas com `re.fullmatch` (correspondência completa, sem precisar de `^`/`$`). Todas escritas como string bruta `r"..."` em `padroes.py`. **Os padrões e todos os casos de teste da seção 4 já foram verificados com `re.fullmatch` no Python 3.12 — todos passaram.**

Definições de alfabeto usadas nas fichas:
- `L = {A, B, …, Z}` (letras maiúsculas ASCII), `D = {0, 1, …, 9}`, `␣` = espaço (U+0020).
- Os símbolos `/`, `+`, `-` são literais do alfabeto quando aparecem.

| ID | Nome | Padrão no código (exato) |
|----|------|--------------------------|
| ER-01 | Identificação do boletim | `r"(METAR\|SPECI) (COR )?S[BDINSW][A-Z]{2}"` |
| ER-02 | Data/hora da observação | `r"(0[1-9]\|[12][0-9]\|3[01])([01][0-9]\|2[0-3])[0-5][0-9]Z"` |
| ER-03 | Vento de superfície | `r"(VRB\|([0-2][0-9]\|3[0-6])0)[0-9]{2,3}(G[0-9]{2,3})?KT"` |
| ER-04 | Visibilidade predominante | `r"CAVOK\|[0-9]{4}(N\|NE\|E\|SE\|S\|SW\|W\|NW)?"` |
| ER-05 | Tempo presente (fenômenos) | `r"(-\|\+\|VC)?((MI\|BC\|PR\|DR\|BL\|SH\|TS\|FZ)(DZ\|RA\|SN\|SG\|PL\|GR\|GS\|BR\|FG\|FU\|HZ\|DU\|SA)*\|(DZ\|RA\|SN\|SG\|PL\|GR\|GS\|BR\|FG\|FU\|HZ\|DU\|SA)+)"` |
| ER-06 | Camada de nuvens | `r"(FEW\|SCT\|BKN\|OVC)[0-9]{3}(CB\|TCU)?\|VV[0-9]{3}\|NSC\|NCD"` |
| ER-07 | Temperatura / ponto de orvalho | `r"M?[0-9]{2}/M?[0-9]{2}"` |
| ER-08 | Pressão QNH | `r"Q(09[0-9]{2}\|10[0-9]{2})"` |

(Na tabela acima o `\|` é só escape do Markdown; no código é `|` normal.)

### Detalhamento por ER (conteúdo para as fichas)

**ER-01 — Identificação do boletim**
- Função: validar o cabeçalho (tipo do boletim, correção opcional e aeródromo brasileiro).
- Σ = L ∪ {␣}.
- L: "METAR" ou "SPECI", seguido de espaço, opcionalmente "COR" + espaço, seguido de indicativo ICAO brasileiro: "S", um de {B,D,I,N,S,W}, e duas letras.
- ER formal: `(METAR | SPECI) ␣ (COR ␣ | ε) S (B | D | I | N | S | W) L L`
- Equivalências: `(COR )?` = `(COR␣ | ε)`; `[BDINSW]` = `(B|D|I|N|S|W)`; `[A-Z]{2}` = `L L`.
- Uso no programa: o cabeçalho ocupa 2 ou 3 tokens. Testar `fullmatch` em `" ".join(tokens[:3])` se `tokens[1] == "COR"`, senão em `" ".join(tokens[:2])`.
- Limitação: aceita indicativos que não existem de fato (ex.: SIZZ) — a ER valida formato, não existência.

**ER-02 — Data/hora (DDHHMMZ)**
- Σ = D ∪ {Z}.
- L: dia 01–31, hora 00–23, minuto 00–59, terminado em Z (UTC).
- ER formal: `(0(1|…|9) | (1|2)D | 3(0|1)) ((0|1)D | 2(0|1|2|3)) (0|1|2|3|4|5) D Z`
- Limitação: aceita 310000Z mesmo em mês de 30 dias (ER não conhece calendário — ótimo ponto para "limitações" na apresentação).

**ER-03 — Vento (dddffGffKT)**
- Σ = D ∪ {V, R, B, G, K, T}.
- L: direção variável "VRB" ou direção em dezenas de graus 000–360 (terceiro dígito sempre 0), velocidade com 2 ou 3 dígitos, rajada opcional "G" + 2 ou 3 dígitos, terminando em "KT".
- ER formal: `(VRB | ((0|1|2) D | 3 (0|1|2|3|4|5|6)) 0) D D (D | ε) (G D D (D | ε) | ε) K T`
- Equivalências: `[0-9]{2,3}` = `DD(D|ε)` = `DD ∪ DDD`; `(…)?` = `(… | ε)`.
- Caso-limite: `00000KT` (calmaria) aceito; `36015KT` aceito; `36115KT` rejeitado (direção não termina em 0).

**ER-04 — Visibilidade**
- Σ = D ∪ {C, A, V, O, K, N, E, S, W}.
- L: "CAVOK" ou 4 dígitos (metros; 9999 = ≥10 km) com direção opcional de 1 ou 2 letras dos 8 pontos cardeais/colaterais.
- ER formal: `CAVOK | D D D D (N | NE | E | SE | S | SW | W | NW | ε)`
- Observação para a apresentação: a união de topo é aplicada por `fullmatch` à expressão inteira (em Python, `fullmatch` equivale a `(?:CAVOK|…)` ancorado — explicar isso).
- Atenção no decodificador: se CAVOK aparecer, o boletim não deve ter grupos de tempo presente nem nuvens (regra de ordem, não de ER).

**ER-05 — Tempo presente** (a mais rica; destacar na apresentação)
- Σ = {-, +} ∪ {letras dos códigos}.
- Sejam `Desc = (MI|BC|PR|DR|BL|SH|TS|FZ)` e `Fen = (DZ|RA|SN|SG|PL|GR|GS|BR|FG|FU|HZ|DU|SA)`.
- L: intensidade/proximidade opcional (`-` fraca, `+` forte, `VC` vizinhança), seguida de **ou** um descritor com zero ou mais fenômenos, **ou** um ou mais fenômenos.
- ER formal: `(- | + | VC | ε) (Desc Fen* | Fen Fen*)`   (usa `Fen+ = Fen Fen*`)
- Casos-limite: `TS` (descritor sozinho, aceito), `RABR` (dois fenômenos, aceito), `TSTS` (dois descritores, rejeitado), `-+RA` (duas intensidades, rejeitado).
- Limitação: aceita combinações meteorologicamente estranhas (ex.: `-TS`), pois a ER só controla a forma.

**ER-06 — Nuvens**
- Σ = D ∪ {F, E, W, S, C, T, B, K, N, O, V}.
- L: quantidade (FEW/SCT/BKN/OVC) + altura em centenas de pés (3 dígitos) + tipo opcional (CB/TCU); ou céu obscurecido `VV` + 3 dígitos; ou `NSC` / `NCD`.
- ER formal: `(FEW | SCT | BKN | OVC) D D D (CB | TCU | ε) | VV D D D | NSC | NCD`
- Caso-limite: `FEW000` (nuvem no solo) aceito; `SKC` rejeitado (código não usado no Brasil — citar como limitação/escolha).

**ER-07 — Temperatura / ponto de orvalho**
- Σ = D ∪ {M, /}.
- L: dois dígitos com `M` opcional (M = negativo), barra, idem.
- ER formal: `(M | ε) D D / (M | ε) D D`
- Caso-limite: `M00/M00` aceito; `M5/M7` rejeitado (exige 2 dígitos).
- Regra semântica fora da ER (fazer no decodificador, e explicar): orvalho > temperatura gera **aviso**, não rejeição.

**ER-08 — Pressão QNH**
- Σ = D ∪ {Q}.
- L: "Q" seguido de valor 0900–1099 hPa.
- ER formal: `Q (0 9 D D | 1 0 D D)`
- Caso-limite: `Q0900` e `Q1099` (extremos) aceitos; `Q0899` e `Q1100` rejeitados.

> Por que 8 e não 5: o mínimo é 5; ter 8 dá folga caso o professor considere alguma simples demais (ER-07 e ER-08 são as mais simples — se precisar enxugar, **não** remover, apenas não destacá-las nos slides).

---

## 4. Casos de teste (já verificados — colocar em `tests/casos.py`)

Estrutura sugerida: `CASOS = {"ER01": {"aceitas": [...], "rejeitadas": [...], "limite": [...]}, ...}`. Cada lista de aceitas/rejeitadas tem **≥ 6** itens; a cadeia vazia `""` está em todas as rejeitadas (caso-limite universal), além dos limites específicos.

| ER | Aceitas | Rejeitadas |
|----|---------|------------|
| ER-01 | `METAR SBBE`, `SPECI SBGR`, `METAR COR SBBE`, `METAR SNBR`, `SPECI COR SWPI`, `METAR SIZZ`, `METAR SDAA` | `""`, `METAR SABE` (Argentina), `TAF SBBE`, `METAR  SBBE` (2 espaços), `metar SBBE`, `METAR SBB`, `METAR COR`, `METAR SBBEX`, `METARSBBE` |
| ER-02 | `241200Z`, `010000Z` (limite inferior), `312359Z` (limite superior), `152330Z`, `100630Z`, `290045Z` | `""`, `001200Z`, `321200Z`, `242400Z`, `241260Z`, `241200`, `24120Z`, `2412000Z`, `241200z` |
| ER-03 | `09010KT`, `00000KT` (calmaria), `36015G25KT`, `VRB03KT`, `270105KT`, `18012G120KT`, `35008KT` | `""`, `37010KT`, `09510KT`, `09010`, `0901KT`, `36015G5KT`, `09010MPS`, `VRBKT`, `36115KT` |
| ER-04 | `9999`, `CAVOK`, `0800`, `5000NE`, `0000` (limite), `3000SW`, `1500N` | `""`, `999`, `99999`, `CAVOk`, `5000NNE`, `5000X`, `CAVOK9999`, `KM10` |
| ER-05 | `RA`, `-RA`, `+TSRA`, `VCSH`, `BR`, `TS`, `-SHRA`, `FZDZ`, `RABR`, `+SHRAGR` | `""`, `+`, `-VC`, `XX`, `RA+`, `VCVC`, `TSTS`, `ra`, `SHXX`, `-+RA` |
| ER-06 | `FEW020`, `SCT015CB`, `BKN100TCU`, `OVC008`, `VV002`, `NSC`, `NCD`, `FEW000` | `""`, `FEW20`, `FEW0200`, `SKC`, `BKN015XB`, `OVC`, `VV02`, `NSCX`, `FEWCB` |
| ER-07 | `30/24`, `M05/M07`, `00/M01`, `09/09`, `M00/M00`, `45/30` | `""`, `30-24`, `3/24`, `30/`, `M5/M7`, `30//24`, `MM05/07`, `30/24M`, `30/245` |
| ER-08 | `Q1013`, `Q0998`, `Q0900`, `Q1099`, `Q1000`, `Q0950` | `""`, `Q101`, `Q10133`, `Q1100`, `Q0899`, `A2992`, `q1013`, `Q 1013`, `1013` |

Cada ficha deve ter uma coluna "motivo" para cada rejeitada (ex.: `242400Z` → "hora 24 fora de 00–23").

---

## 5. AFNε — como construir, verificar e desenhar

### 5.1 Representação (`afne/automato.py`)
Classe `AFNe` com:
- `estados: set[str]`, `inicial: str`, `finais: set[str]`;
- `transicoes: dict[str, list[tuple[str, str]]]` → para cada estado, lista de `(rótulo, destino)`. Rótulo é `"ε"` **ou** um símbolo **ou** uma classe finita escrita como no guia (`"[0-9]"`, `"[A-Z]"`, `"[BDINSW]"`). Uma classe é abreviação de união de símbolos (guia, pág. 2), então é legítimo como rótulo — mas documentar isso na legenda do diagrama.
- `fecho_epsilon(conjunto)` — mesmo algoritmo de pilha do `roboEpsilon.py` do Manito (reaproveitar a ideia).
- `aceita(cadeia) -> bool` e `simular(cadeia) -> list[tuple[símbolo, conjunto_de_estados]]` (traço passo a passo, usado na demonstração).
- Função auxiliar `casa_rotulo(rotulo, simbolo)`: `"[0-9]"` casa dígito, `"[A-Z]"` casa letra maiúscula, `"[XYZ]"` casa se o símbolo está no conjunto, senão compara literal. Implementar o parser de classe só para `[a-b]` e listas simples; nada de `^` negado.

### 5.2 Construção (`afne/definicoes.py`)
- Construir **à mão**, seguindo a lógica de Thompson de forma compacta: usar **ε para uniões, opcionais (`?` = `|ε`) e fechos (`*`, `+`)**, e cadeias de estados para concatenação. Não usar a construção de Thompson "pura" completa (gera dezenas de estados ilegíveis). O requisito é: estado inicial, finais, transições e **movimentos vazios visíveis**.
- Nomear estados `q0, q1, …` e comentar o grupo que cada trecho reconhece (ex.: `# dia`, `# hora`).
- Repetições `{m}` / `{m,n}` viram cadeias explícitas: `[0-9]{2,3}` → `qa -[0-9]-> qb -[0-9]-> qc`, `qc -[0-9]-> qd`, `qc -ε-> qd`.
- Tamanho esperado: 10–30 estados por ER. ER-05: modelar `Desc` e `Fen` como ramos com prefixo compartilhado quando possível (ex.: `S` → `H`/`N`/`G`/`A`); o laço `Fen*` é um ε de volta ao início do bloco de fenômenos. Se ficar grande demais para um slide, dividir o diagrama em "visão geral" (blocos Int, Desc, Fen como caixas) + "bloco Fen expandido".

### 5.3 Verificação de equivalência (obrigatório — é o que garante a "regra de ouro")
Em `tests/test_afne.py`:
1. Para cada ER e cada cadeia da seção 4: `AFNe.aceita(c) == bool(re.fullmatch(padrao, c)) == esperado`.
2. Teste de fumaça aleatório (`random` com semente fixa, ex. `random.seed(2026)`): gerar ~2000 cadeias por ER sobre o alfabeto da ER (comprimento 0–12) + mutações das cadeias aceitas (trocar/remover/inserir 1 símbolo), e afirmar que regex e AFNε concordam em **todas**. Isso pega erro de desenho do autômato.
3. Se algum teste falhar, **corrigir o AFNε** (nunca "ajustar" o teste).

### 5.4 Diagramas (`afne/diagramas.py`)
- Gerar a partir das mesmas definições (assim diagrama e simulador nunca divergem):
  - `docs/afne/ERxx.md` com bloco ```` ```mermaid ```` `flowchart LR` (GitHub renderiza Mermaid nativamente — resolve "diagrama no repositório" sem instalar nada). Estado inicial com seta de entrada (nó invisível `inicio(( )) --> q0`), finais com círculo duplo (`q9(((q9)))`), arestas ε rotuladas `ε`.
  - `docs/afne/ERxx.dot` (Graphviz) como alternativa, com `rankdir=LR`, `doublecircle` nos finais.
- Comando: `python main.py --gerar-diagramas`.
- Para os slides/relatório (PDF), os diagramas podem ser exportados colando o Mermaid em https://mermaid.live ou instalando graphviz (`sudo apt install graphviz` → `dot -Tpng`). Deixar isso escrito no README; **não** instalar nada sem o Manito autorizar.

---

## 6. Aplicação (`main.py` + `decodmetar/`)

### 6.1 `padroes.py`
- Uma `dataclass` `ExpressaoRegular(id, nome, padrao, compilado, descricao)` e um dicionário `PADROES` com as 8. `compilado = re.compile(padrao)`.
- Função `valida(id_er, cadeia) -> bool` usando `fullmatch`.
- Este é o **único** lugar onde os padrões existem. Documentação e testes devem importar daqui (o gerador da ficha em Markdown pode ler `padrao` direto daqui para garantir "copiado exatamente do código").

### 6.2 `decodificador.py`
Fluxo de `decodificar(linha: str) -> Resultado`:
1. `linha.strip()`; se vazia → erro "Entrada vazia: digite um boletim METAR/SPECI."
2. Remover `=` final se houver (boletins reais terminam com `=`). Converter para **maiúsculas? NÃO** — manter como está e rejeitar minúsculas (os testes esperam `metar SBBE` rejeitado); dar dica na mensagem: "Os códigos METAR são sempre em maiúsculas."
3. Tokenizar com `str.split()` (não usar regex aqui para não criar uma 9ª ER não documentada).
4. Cabeçalho via ER-01 (lógica do COR descrita na seção 3). Falhou → erro fatal com explicação.
5. Próximo token: ER-02 obrigatório.
6. Grupos seguintes, em ordem esperada: vento (ER-03) → visibilidade (ER-04) → tempo presente (ER-05, 0..n) → nuvens (ER-06, 0..n) → temp/orvalho (ER-07) → pressão (ER-08). Implementar como máquina de estados simples de "posição esperada" (bônus conceitual: dá para comentar na apresentação que a ordem dos grupos também é uma linguagem regular sobre o alfabeto de tipos de grupo).
7. Tokens como `AUTO`, `NOSIG`, `RMK …` (e tudo depois de `RMK`): marcar como "grupo ignorado (fora do escopo)", não como erro.
8. Token que não casa com nada na posição → registrar erro com: posição, token, o que era esperado e por quê (ex.: "`37010KT`: direção 370° inválida — deve estar entre 000 e 360 em dezenas").
9. Extração dos valores via `grupos` do match (usar grupos nomeados? **Não** — `(?P<nome>…)` muda a sintaxe exibida; para extrair, fatiar a string validada: ex. vento `token[:3]`, `token[3:5/6]`, split em `G`). Mantém o padrão idêntico ao da ficha.
10. Tradução com tabelas em `mensagens.py` (ex.: `{"RA": "chuva", "TS": "trovoada", "BR": "névoa úmida", "FEW": "poucas nuvens (1–2/8)", …}`).
11. Avisos semânticos (não erros): orvalho > temperatura; rajada ≤ velocidade média; CAVOK junto de nuvens.

`Resultado` (dataclass): `valido: bool`, `campos: dict`, `traducao: list[str]`, `erros: list[str]`, `avisos: list[str]`, `ignorados: list[str]`.

### 6.3 `main.py` — interface
Sem argumentos → **menu interativo** em loop:
```
=== DecodMETAR ===
1) Decodificar um boletim digitado
2) Processar arquivo de boletins
3) Testar uma cadeia em uma ER específica (regex + AFNε com traço)
4) Listar as expressões regulares do programa
5) Rodar bateria de testes
0) Sair
```
- Opção inválida/letra/vazio → "Opção inválida. Digite um número de 0 a 5." e volta ao menu (nunca travar com exceção).
- Opção 2: pedir caminho; arquivo inexistente, diretório, vazio ou não-UTF-8 → mensagem clara. Linhas em branco são puladas e contadas. Ao final: resumo "N boletins: X válidos, Y com erro".
- Opção 3 (**essa é a da demonstração ao vivo** — o professor pode pedir cadeias novas): escolher ER (1–8), digitar cadeia, mostrar: padrão, resultado do `re.fullmatch`, resultado do AFNε, e o traço `{q0,q1,q4} --0--> {q2,…}` até o fim, com "ACEITA"/"REJEITADA". Se regex e AFNε divergirem, mostrar alerta em destaque (não deve acontecer).
- `Ctrl+C`/`EOF` → sair com "Até mais!" sem stack trace.

Com argumentos (`argparse`), para facilitar a demo:
- `python main.py "METAR SBBE 241200Z 09010KT 9999 FEW020 30/24 Q1011"`
- `python main.py --arquivo dados/metar_misto.txt`
- `python main.py --testar ER03 36015G25KT`
- `python main.py --gerar-diagramas`

Saídas coloridas são opcionais; se usar ANSI, desligar quando `not sys.stdout.isatty()`.

---

## 7. Testes (`unittest`, sem pytest)

Rodar com: `python -m unittest discover -s tests -v`

- `test_padroes.py`: um `subTest` por cadeia da seção 4 (aceitas e rejeitadas) para cada ER; teste que cada ER tem ≥ 6 aceitas e ≥ 6 rejeitadas e ao menos 1 limite.
- `test_afne.py`: seção 5.3 (equivalência determinística + aleatória).
- `test_decodificador.py`:
  - boletim completo válido → `valido=True` e tradução contém "Vento", "Pressão";
  - com `COR`, com `=` final, com `RMK`, com múltiplas camadas de nuvem e múltiplos fenômenos;
  - entrada vazia, só espaços, minúsculas, cabeçalho inválido, data inválida, grupo fora de ordem, token lixo → `valido=False` com mensagem específica;
  - avisos semânticos (orvalho > temperatura).
- Salvar a saída da execução dos testes em `docs/resultado_testes.txt` (evidência para o item "Testes e análise dos resultados").

---

## 8. Dados de exemplo (`dados/`)

Escrever boletins **sintéticos mas realistas** (declarar no README que são exemplos criados pela equipe, não dados oficiais). Usar aeródromos reais brasileiros: SBBE (Belém), SBGR (Guarulhos), SBBR (Brasília), SBEG (Manaus), SBPA (Porto Alegre, bom para temperatura negativa `M02/M04`), SBSN (Santarém). Exemplos:
```
METAR SBBE 241200Z 09010KT 9999 -RA FEW020 SCT100 30/24 Q1011
SPECI SBEG 241530Z 36015G25KT 3000 +TSRA BKN015CB 26/24 Q1009
METAR COR SBPA 240900Z VRB03KT 0800 FG VV002 M02/M04 Q1024
METAR SBBR 241200Z 00000KT CAVOK 22/08 Q1018
```
`metar_com_erros.txt`: um erro diferente por linha (data 321200Z, vento 37010KT, pressão Q1100, minúsculas, temperatura `3/24`, estação `SABE`, linha só com `METAR`, grupo desconhecido `XYZ123`).

---

## 9. Documentação e entregáveis

1. **`docs/EXPRESSOES_REGULARES.md`** — 8 fichas, cada uma com os campos do guia (pág. 4) **e** do enunciado: Identificação (ER-0x, nome, função), Alfabeto Σ, Linguagem L, ER formal, Sintaxe implementada (copiada de `padroes.py`), Explicação dos operadores/equivalências, AFNε (link/embed do Mermaid + tabela de transições + lista de ε-movimentos + inicial + finais), Testes (≥6 aceitas, ≥6 rejeitadas com motivo, limites marcados), Resultado e limitações. Sugestão: gerar a parte "sintaxe implementada" e a tabela de transições automaticamente de `padroes.py` e `definicoes.py` (`python main.py --gerar-docs`), e escrever o texto explicativo à mão.
2. **`README.md`** — descrição, requisitos (Python ≥ 3.10, nenhuma dependência), como rodar (menu, CLI, testes, diagramas), estrutura de pastas, exemplos de entrada/saída, link para as fichas, **seção "Uso de Inteligência Artificial"** (obrigatória: dizer que IA foi usada no planejamento, geração de código-base e revisão, e que a equipe revisou e entende tudo), referências (ICAO Annex 3 / manual de códigos meteorológicos do DECEA como fonte do formato METAR; docs do módulo `re` do Python; guia do professor).
3. **`CONTRIBUICOES.md`** — tabela Integrante × tarefas (deixar nomes como `[Integrante 1]` para o Manito preencher). Sugestão de divisão para 4 pessoas: (1) ER-01/02 + decodificador; (2) ER-03/04 + AFNε/simulador; (3) ER-05/06 + testes; (4) ER-07/08 + relatório/slides. Cada integrante apresenta as próprias ERs.
4. **`docs/RELATORIO_TECNICO.md`** → PDF. Seções: Capa; Introdução e problema; Fundamentação (ER, linguagens regulares, AFNε, equivalência Kleene/Thompson); Metodologia e arquitetura; As 8 fichas (resumidas, referenciando o doc completo); Testes e análise dos resultados (tabela ER × aceitas/rejeitadas × passou, resultado do teste aleatório); Limitações e melhorias (calendário, existência de aeródromos, TAF, grupos RVR/tendência, interface web); Uso de IA; Referências; Contribuições. Conversão para PDF: pandoc não está instalado — gerar no Google Docs/LibreOffice a partir do Markdown, ou pedir ao Manito para instalar pandoc. **Não inventar dados de resultado**: copiar da saída real dos testes.
5. **`docs/APRESENTACAO_ROTEIRO.md`** — 10–12 min, ~13 slides:
   1. Título + equipe · 2. Problema (o que é METAR, exemplo ilegível) · 3. Solução e arquitetura (entrada → tokens → ERs → tradução) · 4. Tabela das 8 ERs · 5–7. Fichas destacadas: ER-02 (intervalos numéricos), ER-03 (opcional + {2,3}), ER-05 (união + fecho, a mais rica) com formal × código × AFNε lado a lado · 8. Como garantimos a equivalência (regex × AFNε no mesmo teste) · 9. **Demo ao vivo**: opção 1 com boletim válido, opção 3 com uma cadeia aceita e uma rejeitada mostrando o traço do AFNε · 10. Testes e resultados · 11. Limitações e melhorias · 12. Contribuição de cada integrante · 13. Uso de IA + referências.
   Incluir no roteiro "perguntas prováveis do professor" com respostas: por que `fullmatch`; diferença entre `?` e `*`; como `{2,3}` vira união; por que não usamos `\d`; o que o AFNε faz com ε; mostrar alteração ao vivo (ex.: aceitar pressão até 1100 → mudar ER-08, AFNε e testes).
6. **`docs/ETAPA1_PLANILHA.md`** (prazo 26/09!) — texto pronto: integrantes (placeholder), título, descrição de 3–4 linhas, linguagem Python 3.12, link do GitHub (placeholder), requisitos funcionais: Python ≥ 3.10, biblioteca padrão (`re`, `unittest`, `argparse`), ambiente VS Code/terminal Linux, Git/GitHub, Mermaid para diagramas.

---

## 10. Ordem de execução para o agente implementador

1. Criar a estrutura de pastas da seção 2 e `ETAPA1_PLANILHA.md` (urgente pelo prazo).
2. `padroes.py` + `tests/casos.py` + `test_padroes.py` → rodar e ver tudo passar.
3. `afne/automato.py` (com teste unitário do fecho-ε num autômato mínimo).
4. `afne/definicoes.py`, uma ER por vez, rodando `test_afne.py` (equivalência determinística + aleatória) após cada uma. Não seguir para a próxima ER enquanto a atual divergir.
5. `afne/diagramas.py` + gerar `docs/afne/*`; conferir visualmente que o Mermaid é legível.
6. `decodificador.py` + `mensagens.py` + `test_decodificador.py`.
7. `main.py` (menu + CLI) e testar manualmente todas as entradas inválidas da seção 6.3.
8. `dados/*.txt` e rodar `--arquivo` em cada um.
9. Documentação: fichas, README, CONTRIBUICOES, relatório, roteiro. Salvar `docs/resultado_testes.txt` a partir da execução real.
10. Checklist final (seção 11). Não fazer `git init`/push nem criar repositório no GitHub sem o Manito pedir; sem trailer `Co-Authored-By` de IA em commits.

---

## 11. Checklist final (conferir item a item contra o enunciado)

- [ ] ≥ 5 ERs distintas e relevantes (temos 8), nenhuma copiada de exercício de sala
- [ ] Cada ER: nome/finalidade, Σ, L, ER formal, sintaxe exata do código, operadores explicados, AFNε (inicial, finais, transições, ε), ≥ 6 aceitas, ≥ 6 rejeitadas, ≥ 1 caso-limite
- [ ] Padrão na ficha == padrão em `padroes.py` (gerado/copiado automaticamente)
- [ ] Regex e AFNε concordam em 100% dos testes (determinísticos + aleatórios)
- [ ] Nenhum `\d`, `\w`, `\s`, `.`, lookaround ou retroreferência nas ERs
- [ ] Entradas vazias/inválidas tratadas com mensagem clara (menu, arquivo, cadeia)
- [ ] Código em módulos/funções; roda com `python main.py` sem instalar nada
- [ ] Repositório contém: código, README, dependências (`requirements.txt`), testes, dados de exemplo, diagramas AFNε, ERs documentadas, contribuições
- [ ] Relatório técnico (PDF) e apresentação (PDF/PPTX) prontos
- [ ] Uso de IA declarado (README e relatório), dizendo em quais tarefas
- [ ] Referências externas citadas (formato METAR — ICAO/DECEA; docs Python `re`)
- [ ] Ensaio da demo: boletim válido, boletim com erro, uma cadeia aceita e uma rejeitada com traço do AFNε
