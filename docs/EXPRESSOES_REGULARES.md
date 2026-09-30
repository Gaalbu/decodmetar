# Expressões Regulares do DecodMETAR

Uma ficha por ER, no formato do *Guia de Sintaxe para Apresentação das Expressões Regulares*.

Notação usada em todas as fichas:

- `D = (0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9)`, os algarismos.
- `L = (A | B | … | Z)`, as letras maiúsculas (ASCII, sem acento).
- `␣` é o caractere espaço (U+0020).
- `ε` é a palavra vazia (comprimento zero; não é o caractere "ε").
- Uma palavra como `KT` é a concatenação dos símbolos `K T`.
- No código, todas as ERs são aplicadas com `re.fullmatch`, que exige que a cadeia **inteira** pertença à linguagem. Por isso os padrões não usam as âncoras `^` e `$`.
- Nenhuma ER usa `\d`, `\w`, `\s`, `.`, retroreferências ou lookaround: todas as classes são explícitas (`[0-9]`, `[A-Z]`), para o alfabeto ficar declarado.

Os padrões abaixo foram copiados de [`decodmetar/padroes.py`](../decodmetar/padroes.py). Um teste automático (`tests/test_documentacao.py`) confere que cada ficha tem o padrão, a ER formal e as cadeias de teste iguais às do código, e que os traços mostrados são a saída real do simulador.

## Resumo

| ER | Grupo do METAR | Padrão no código | AFNε |
|---|---|---|---|
| ER-01 | Identificação do boletim | `(METAR\|SPECI) (COR )?S[BDINSW][A-Z]{2}` | 22 estados, 4 ε |
| ER-02 | Data e hora | `(0[1-9]\|[12][0-9]\|3[01])([01][0-9]\|2[0-3])[0-5][0-9]Z` | 16 estados, 5 ε |
| ER-03 | Vento | `(VRB\|([0-2][0-9]\|3[0-6])0)[0-9]{2,3}(G[0-9]{2,3})?KT` | 19 estados, 6 ε |
| ER-04 | Visibilidade | `CAVOK\|[0-9]{4}(N\|NE\|E\|SE\|S\|SW\|W\|NW)?` | 16 estados, 7 ε |
| ER-05 | Tempo presente | `(-\|\+\|VC)?((MI\|BC\|…\|FZ)(DZ\|RA\|…\|SA)*\|(DZ\|RA\|…\|SA)+)` | 23 estados, 7 ε |
| ER-06 | Nuvens | `(FEW\|SCT\|BKN\|OVC)[0-9]{3}(CB\|TCU)?\|VV[0-9]{3}\|NSC\|NCD` | 30 estados, 7 ε |
| ER-07 | Temperatura e orvalho | `M?[0-9]{2}/M?[0-9]{2}` | 8 estados, 2 ε |
| ER-08 | Pressão QNH | `Q(09[0-9]{2}\|10[0-9]{2})` | 13 estados, 4 ε |

(Nas tabelas, `\|` é só o escape do Markdown; no código é `|`.)

---

## ER-01: Identificação do boletim

| Campo | Conteúdo |
|---|---|
| Identificação | ER-01, cabeçalho do boletim. O decodificador junta os 2 primeiros grupos (ou 3, quando o segundo é `COR`) e testa a cadeia com essa ER. Se falhar, o boletim é rejeitado logo no início. |
| Alfabeto (Σ) | `L ∪ {␣}` |
| Linguagem L | A palavra `METAR` ou `SPECI`, um espaço, opcionalmente a palavra `COR` seguida de espaço (boletim corrigido), e o indicativo ICAO de 4 letras de um aeródromo brasileiro: `S`, uma letra entre B, D, I, N, S e W, e mais duas letras quaisquer. |
| ER formal | `(METAR \| SPECI) ␣ (COR ␣ \| ε) S (B \| D \| I \| N \| S \| W) L L` |
| Sintaxe implementada | `r"(METAR\|SPECI) (COR )?S[BDINSW][A-Z]{2}"` |
| AFNε | [`docs/afne/ER01.md`](afne/ER01.md): 22 estados, inicial `q0`, final `q21`, 4 movimentos ε. |

### Equivalência entre o código e a notação formal

| No código | Na notação formal | Explicação |
|---|---|---|
| `(METAR\|SPECI)` | `(METAR \| SPECI)` | União de duas palavras; cada palavra é concatenação de literais (`M E T A R`). |
| ` ` (espaço) | `␣` | O espaço é um símbolo do alfabeto como outro qualquer. Escrevemos `␣` para ele ficar visível. |
| `(COR )?` | `(COR ␣ \| ε)` | Opcionalidade: `r? = (r \| ε)`. |
| `S` | `S` | Literal: todo indicativo brasileiro começa com S. |
| `[BDINSW]` | `(B \| D \| I \| N \| S \| W)` | Classe finita = união dos símbolos listados. |
| `[A-Z]{2}` | `L L` | Intervalo `[A-Z]` = `L`, e repetição exata `r{2}` = `r r`. |

### AFNε

- `q5 → q11` e `q10 → q11` juntam os dois ramos da união `METAR | SPECI`.
- `q12 → q17` pula o `COR ␣` inteiro (o `?`).
- `q16 → q17` fecha o ramo do `COR ␣`.

Diagrama e tabela de transições completos: [`docs/afne/ER01.md`](afne/ER01.md).

Traço real do simulador para uma cadeia aceita (repare nos dois `␣`):

```
cadeia: METAR COR SBBE
início: {q0}
lê 'M' → {q1}
lê 'E' → {q2}
lê 'T' → {q3}
lê 'A' → {q4}
lê 'R' → {q5, q11}
lê '␣' → {q12, q17}
lê 'C' → {q13}
lê 'O' → {q14}
lê 'R' → {q15}
lê '␣' → {q16, q17}
lê 'S' → {q18}
lê 'B' → {q19}
lê 'B' → {q20}
lê 'E' → {q21}
resultado: ACEITA
```

E para uma rejeitada. `SA` é prefixo da Argentina: de `q18` só se sai com B, D, I, N, S ou W.

```
cadeia: METAR SABE
início: {q0}
lê 'M' → {q1}
lê 'E' → {q2}
lê 'T' → {q3}
lê 'A' → {q4}
lê 'R' → {q5, q11}
lê '␣' → {q12, q17}
lê 'S' → {q18}
lê 'A' → ∅
resultado: REJEITADA
```

### Testes

| Aceitas | Observação |
|---|---|
| `METAR SBBE` | Belém, forma mais comum |
| `SPECI SBGR` | boletim especial, Guarulhos |
| `METAR COR SBBE` | **caso-limite**: forma mais longa, com correção |
| `METAR SNBR` | prefixo SN |
| `SPECI COR SWPI` | SPECI corrigido, prefixo SW |
| `METAR SIZZ` | **caso-limite**: formato válido, mas o aeródromo não existe |
| `METAR SDAA` | prefixo SD |

| Rejeitadas | Motivo |
|---|---|
| `""` | **caso-limite**: cadeia vazia |
| `METAR SABE` | SA é prefixo da Argentina, não do Brasil |
| `TAF SBBE` | TAF é previsão, não observação |
| `METAR  SBBE` | **caso-limite**: dois espaços entre os grupos |
| `metar SBBE` | letras minúsculas |
| `METAR SBB` | indicativo com 3 letras |
| `METAR COR` | falta o indicativo do aeródromo |
| `METAR SBBEX` | indicativo com 5 letras |
| `METARSBBE` | falta o espaço |

### Resultado e limitações

- Todas as cadeias acima dão o resultado esperado no `re.fullmatch` e no AFNε, que também concordam em milhares de cadeias geradas ao acaso.
- A ER valida o **formato**, não a existência: `METAR SIZZ` é aceito (falso positivo). Saber se o aeródromo existe exigiria uma lista, e não uma ER.
- O bloco `SJ`, também usado no Brasil para aeródromos mais novos, ficou de fora. Para incluí-lo, bastaria acrescentar `J` à classe (`[BDIJNSW]`) e uma transição no AFNε.
- A ER rejeita dois espaços seguidos, mas o decodificador separa os grupos com `split()` e junta o cabeçalho com um único espaço. Por isso um boletim com espaços extras é aceito pelo programa.

---

## ER-02: Data e hora da observação

| Campo | Conteúdo |
|---|---|
| Identificação | ER-02, grupo de data e hora (`DDHHMMZ`). O decodificador usa essa ER no 1º grupo depois do cabeçalho e extrai dia, hora e minuto. |
| Alfabeto (Σ) | `D ∪ {Z}` |
| Linguagem L | Dia de 01 a 31, hora de 00 a 23 e minuto de 00 a 59, sempre com 2 algarismos cada, seguidos da letra `Z` (horário UTC). |
| ER formal | `(0 (1 \| … \| 9) \| (1 \| 2) D \| 3 (0 \| 1)) ((0 \| 1) D \| 2 (0 \| 1 \| 2 \| 3)) (0 \| 1 \| 2 \| 3 \| 4 \| 5) D Z` |
| Sintaxe implementada | `r"(0[1-9]\|[12][0-9]\|3[01])([01][0-9]\|2[0-3])[0-5][0-9]Z"` |
| AFNε | [`docs/afne/ER02.md`](afne/ER02.md): 16 estados, inicial `q0`, final `q15`, 5 movimentos ε. |

### Equivalência entre o código e a notação formal

ER não compara números: um intervalo como "01 a 31" precisa ser escrito como união de padrões de algarismos. É a ideia central desta ficha.

| No código | Na notação formal | Explicação |
|---|---|---|
| `0[1-9]` | `0 (1 \| … \| 9)` | Dias 01 a 09 (o dia 00 fica de fora). |
| `[12][0-9]` | `(1 \| 2) D` | Dias 10 a 29. |
| `3[01]` | `3 (0 \| 1)` | Dias 30 e 31. |
| `(…\|…\|…)` | `(… \| … \| …)` | União das três faixas do dia. |
| `[01][0-9]\|2[0-3]` | `(0 \| 1) D \| 2 (0 \| 1 \| 2 \| 3)` | Horas 00 a 19 ou 20 a 23. |
| `[0-5][0-9]` | `(0 \| 1 \| 2 \| 3 \| 4 \| 5) D` | Minutos 00 a 59. |
| `Z` | `Z` | Literal: "Zulu", o horário UTC. |

### AFNε

- `q2 → q7`, `q4 → q7` e `q6 → q7` juntam as três faixas do dia (01–09, 10–29, 30–31).
- `q9 → q12` e `q11 → q12` juntam as duas faixas da hora (00–19, 20–23).
- O minuto e o `Z` são uma cadeia simples de estados: `q12 → q13 → q14 → q15`.

Diagrama e tabela de transições completos: [`docs/afne/ER02.md`](afne/ER02.md).

Traço real do simulador para uma cadeia aceita:

```
cadeia: 241200Z
início: {q0}
lê '2' → {q3}
lê '4' → {q4, q7}
lê '1' → {q8}
lê '2' → {q9, q12}
lê '0' → {q13}
lê '0' → {q14}
lê 'Z' → {q15}
resultado: ACEITA
```

E para uma rejeitada. Depois de `2` na hora (estado `q10`), só se aceita `0` a `3`:

```
cadeia: 242400Z
início: {q0}
lê '2' → {q3}
lê '4' → {q4, q7}
lê '2' → {q10}
lê '4' → ∅
resultado: REJEITADA
```

### Testes

| Aceitas | Observação |
|---|---|
| `241200Z` | dia 24, 12:00 UTC |
| `010000Z` | **caso-limite**: menor valor possível |
| `312359Z` | **caso-limite**: maior valor possível |
| `152330Z` | hora na faixa 20–23 |
| `100630Z` | dia na faixa 10–29 |
| `290045Z` | meia-noite e 45 |

| Rejeitadas | Motivo |
|---|---|
| `""` | **caso-limite**: cadeia vazia |
| `001200Z` | dia 00 não existe |
| `321200Z` | dia 32 não existe |
| `242400Z` | **caso-limite**: hora 24 fora de 00–23 |
| `241260Z` | **caso-limite**: minuto 60 fora de 00–59 |
| `241200` | falta o Z (UTC) |
| `24120Z` | só 5 dígitos |
| `2412000Z` | 7 dígitos |
| `241200z` | z minúsculo |

### Resultado e limitações

- Todas as cadeias acima dão o resultado esperado no `re.fullmatch` e no AFNε.
- A ER não conhece o calendário: aceita `310000Z` mesmo que o mês tenha 30 dias, e `300000Z` em fevereiro. O METAR não informa o mês, então nem o programa inteiro conseguiria checar isso.
- Não verifica se a data está no futuro nem se o minuto é compatível com o horário de emissão (os METAR saem na hora cheia; o SPECI, a qualquer minuto).

---

## ER-03: Vento de superfície

| Campo | Conteúdo |
|---|---|
| Identificação | ER-03, grupo de vento do METAR. O decodificador usa essa ER para reconhecer e extrair direção, velocidade e rajada. |
| Alfabeto (Σ) | `D ∪ {V, R, B, G, K, T}` |
| Linguagem L | Direção variável `VRB` ou direção em dezenas de graus de 000 a 360 (o terceiro dígito é sempre 0), seguida da velocidade com 2 ou 3 dígitos, de uma rajada opcional (`G` + 2 ou 3 dígitos) e da unidade `KT` (nós). |
| ER formal | `(VRB \| ((0 \| 1 \| 2) D \| 3 (0 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6)) 0) D D (D \| ε) (G D D (D \| ε) \| ε) K T` |
| Sintaxe implementada | `r"(VRB\|([0-2][0-9]\|3[0-6])0)[0-9]{2,3}(G[0-9]{2,3})?KT"` |
| AFNε | [`docs/afne/ER03.md`](afne/ER03.md): 19 estados, inicial `q0`, final `q18`, 6 movimentos ε. |

### Equivalência entre o código e a notação formal

| No código | Na notação formal | Explicação |
|---|---|---|
| `VRB\|…` | `VRB \| …` | União: ou o vento é variável, ou tem direção numérica. |
| `[0-2][0-9]` | `(0 \| 1 \| 2) D` | Classes e intervalos são abreviações de união. Cobre as dezenas 00 a 29. |
| `3[0-6]` | `3 (0 \| 1 \| … \| 6)` | Cobre as dezenas 30 a 36, ou seja, direções 300 a 360. |
| `(…)0` | `(…) 0` | Concatenação com o literal 0: a direção sempre termina em 0. |
| `[0-9]{2,3}` | `D D (D \| ε)` | Repetição limitada: `r{2,3} = rr ∪ rrr = rr(r \| ε)`. |
| `(G[0-9]{2,3})?` | `(G D D (D \| ε) \| ε)` | Opcionalidade: `r? = (r \| ε)`. |
| `KT` | `K T` | Concatenação de dois literais. |

### AFNε

Construído no estilo de Thompson, compactado. Cada escolha da ER vira um movimento ε no autômato:

- `q3 → q8` e `q7 → q8` juntam os dois ramos da união (VRB ou direção numérica);
- `q10 → q11` pula o 3º dígito da velocidade (`{2,3}`);
- `q11 → q16` pula a rajada inteira (`?`);
- `q14 → q15` pula o 3º dígito da rajada;
- `q15 → q16` fecha o ramo da rajada.

Diagrama e tabela de transições completos: [`docs/afne/ER03.md`](afne/ER03.md).

Traço real do simulador para uma cadeia aceita:

```
cadeia: 36015G25KT
início: {q0}
lê '3' → {q5}
lê '6' → {q6}
lê '0' → {q7, q8}
lê '1' → {q9}
lê '5' → {q10, q11, q16}
lê 'G' → {q12}
lê '2' → {q13}
lê '5' → {q14, q15, q16}
lê 'K' → {q17}
lê 'T' → {q18}
resultado: ACEITA
```

E para uma rejeitada. A direção 361° não termina em 0, então não existe transição de `q6` com o símbolo `1`:

```
cadeia: 36115KT
início: {q0}
lê '3' → {q5}
lê '6' → {q6}
lê '1' → ∅
resultado: REJEITADA
```

### Testes

| Aceitas | Observação |
|---|---|
| `09010KT` | vento de 090° a 10 nós |
| `00000KT` | **caso-limite**: calmaria (direção e velocidade zero) |
| `36015G25KT` | **caso-limite**: direção máxima (360) e rajada |
| `VRB03KT` | direção variável |
| `270105KT` | **caso-limite**: velocidade com 3 dígitos |
| `18012G120KT` | rajada com 3 dígitos |
| `35008KT` | direção 350 |

| Rejeitadas | Motivo |
|---|---|
| `""` | **caso-limite**: cadeia vazia |
| `37010KT` | direção 370° acima de 360 |
| `09510KT` | direção não termina em 0 (não é dezena de graus) |
| `09010` | falta a unidade KT |
| `0901KT` | velocidade com 1 dígito |
| `36015G5KT` | rajada com 1 dígito |
| `09010MPS` | unidade MPS não prevista |
| `VRBKT` | falta a velocidade |
| `36115KT` | **caso-limite**: direção 361° não é dezena de graus |

### Resultado e limitações

- Todas as cadeias acima dão o resultado esperado no `re.fullmatch` e no AFNε. As duas implementações também concordam em milhares de cadeias geradas ao acaso (ver [Como garantimos a equivalência](#como-garantimos-que-a-er-e-o-afnε-reconhecem-a-mesma-linguagem), no fim deste documento).
- A ER valida só a **forma** do grupo. Ela aceita `09020G10KT` (rajada menor que a velocidade média) e `VRB999KT` (999 nós). O decodificador emite um **aviso** quando a rajada não é maior que a média, mas essa checagem não faz parte da ER.
- A unidade `MPS` (metros por segundo) e o grupo de variação de direção (`350V040`) ficaram fora do escopo: o primeiro não é usado no Brasil e o segundo é um grupo à parte no METAR.
- A linguagem é finita: há um número limitado de combinações de direção, velocidade e rajada. Ainda assim, a ER é muito mais compacta do que listar todas.

---

## ER-04: Visibilidade predominante

| Campo | Conteúdo |
|---|---|
| Identificação | ER-04, grupo de visibilidade do METAR. O decodificador usa essa ER para reconhecer a visibilidade em metros ou a condição CAVOK. |
| Alfabeto (Σ) | `D ∪ {C, A, V, O, K, N, E, S, W}` |
| Linguagem L | A palavra `CAVOK` (teto e visibilidade OK) ou 4 algarismos (visibilidade em metros; `9999` = 10 km ou mais), opcionalmente seguidos de uma das 8 direções: N, NE, E, SE, S, SW, W, NW. |
| ER formal | `CAVOK \| D D D D (N \| NE \| E \| SE \| S \| SW \| W \| NW \| ε)` |
| Sintaxe implementada | `r"CAVOK\|[0-9]{4}(N\|NE\|E\|SE\|S\|SW\|W\|NW)?"` |
| AFNε | [`docs/afne/ER04.md`](afne/ER04.md): 16 estados, inicial `q0`, final `q15`, 7 movimentos ε. |

### Equivalência entre o código e a notação formal

| No código | Na notação formal | Explicação |
|---|---|---|
| `CAVOK\|…` | `CAVOK \| …` | União no nível mais externo da ER. Com `re.fullmatch`, a cadeia inteira precisa ser `CAVOK` **ou** a cadeia inteira precisa ser o ramo numérico. |
| `[0-9]{4}` | `D D D D` | Repetição exata: `r{4}` = 4 cópias de `r` concatenadas. |
| `(N\|NE\|…\|NW)?` | `(N \| NE \| … \| NW \| ε)` | União das 8 direções mais a opcionalidade (`\| ε`). |

### AFNε

- `q0 → q1` e `q0 → q7` abrem os dois ramos da união de topo (CAVOK ou numérico).
- `q6 → q15` fecha o ramo CAVOK.
- `q11 → q15` é a opcionalidade: termina sem direção.
- Na parte das direções, `N` e `S` são prefixos de `NE`/`NW` e `SE`/`SW`. Por isso o autômato compartilha esses prefixos: `q11 -N→ q12 -[EW]→ q14`. Os movimentos `q12 → q15` e `q13 → q15` permitem parar só em `N` ou só em `S`.

Diagrama e tabela de transições completos: [`docs/afne/ER04.md`](afne/ER04.md).

Traço real do simulador. Repare que o fecho-ε do estado inicial já contém os dois ramos:

```
cadeia: 5000NE
início: {q0, q1, q7}
lê '5' → {q8}
lê '0' → {q9}
lê '0' → {q10}
lê '0' → {q11, q15}
lê 'N' → {q12, q15}
lê 'E' → {q14, q15}
resultado: ACEITA
```

```
cadeia: 5000NNE
início: {q0, q1, q7}
lê '5' → {q8}
lê '0' → {q9}
lê '0' → {q10}
lê '0' → {q11, q15}
lê 'N' → {q12, q15}
lê 'N' → ∅
resultado: REJEITADA
```

### Testes

| Aceitas | Observação |
|---|---|
| `9999` | **caso-limite**: maior valor, 10 km ou mais |
| `CAVOK` | teto e visibilidade OK |
| `0800` | 800 metros |
| `5000NE` | direção com 2 letras |
| `0000` | **caso-limite**: visibilidade zero |
| `3000SW` | direção com 2 letras |
| `1500N` | direção com 1 letra |

| Rejeitadas | Motivo |
|---|---|
| `""` | **caso-limite**: cadeia vazia |
| `999` | apenas 3 dígitos |
| `99999` | 5 dígitos |
| `CAVOk` | letra minúscula |
| `5000NNE` | direção com 3 letras não prevista |
| `5000X` | X não é direção |
| `CAVOK9999` | **caso-limite**: CAVOK e valor numérico juntos |
| `KM10` | formato em km não previsto |

### Resultado e limitações

- Todas as cadeias acima dão o resultado esperado no `re.fullmatch` e no AFNε, que também concordam nas cadeias aleatórias.
- A ER aceita qualquer valor de 4 dígitos, como `0001`, embora os boletins reais usem degraus fixos (50 m, 100 m, 1000 m…).
- Aceita direção junto de `9999` (`9999N`), o que não faz sentido meteorológico.
- `NDV` (sem variação direcional, usado por estações automáticas) não foi incluído.
- A regra "depois de `CAVOK` não pode haver tempo presente nem nuvens" não é da ER: é checada pelo decodificador.

---

## ER-05: Tempo presente

| Campo | Conteúdo |
|---|---|
| Identificação | ER-05, grupo de tempo presente (chuva, trovoada, névoa…). É a ER mais rica do projeto: a única com fecho de Kleene e fecho positivo, e a única cuja linguagem é **infinita**. O decodificador aceita até 3 grupos desses por boletim. |
| Alfabeto (Σ) | `{-, +, A, B, C, D, F, G, H, I, L, M, N, P, R, S, T, U, V, Z}` |
| Definições | `Desc = (MI \| BC \| PR \| DR \| BL \| SH \| TS \| FZ)` (descritores) e `Fen = (DZ \| RA \| SN \| SG \| PL \| GR \| GS \| BR \| FG \| FU \| HZ \| DU \| SA)` (fenômenos) |
| Linguagem L | Uma indicação opcional de intensidade ou proximidade (`-` fraca, `+` forte, `VC` nas vizinhanças), seguida **ou** de um descritor com zero ou mais fenômenos, **ou** de um ou mais fenômenos. |
| ER formal | `('-' \| '+' \| VC \| ε) (Desc Fen* \| Fen Fen*)` |
| Sintaxe implementada | `r"(-\|\+\|VC)?((MI\|BC\|PR\|DR\|BL\|SH\|TS\|FZ)(DZ\|RA\|SN\|SG\|PL\|GR\|GS\|BR\|FG\|FU\|HZ\|DU\|SA)*\|(DZ\|RA\|SN\|SG\|PL\|GR\|GS\|BR\|FG\|FU\|HZ\|DU\|SA)+)"` |
| AFNε | [`docs/afne/ER05.md`](afne/ER05.md): 23 estados, inicial `q0`, final `q22`, 7 movimentos ε. |

Na ER formal, `'+'` e `'-'` entre aspas são os **símbolos** mais e menos do alfabeto, para não confundir com o operador de fecho positivo `r+`.

| Descritor | Significado | Fenômeno | Significado |
|---|---|---|---|
| `MI` | baixo | `DZ` | chuvisco |
| `BC` | em bancos | `RA` | chuva |
| `PR` | parcial | `SN` / `SG` | neve / grãos de neve |
| `DR` | flutuante | `PL` | pelotas de gelo |
| `BL` | soprado | `GR` / `GS` | granizo / granizo pequeno |
| `SH` | pancadas | `BR` / `FG` | névoa úmida / nevoeiro |
| `TS` | trovoada | `FU` / `HZ` | fumaça / névoa seca |
| `FZ` | congelante | `DU` / `SA` | poeira / areia |

### Equivalência entre o código e a notação formal

| No código | Na notação formal | Explicação |
|---|---|---|
| `(-\|\+\|VC)?` | `('-' \| '+' \| VC \| ε)` | No código o `+` precisa de escape (`\+`), porque sozinho é o operador "uma ou mais vezes". O `-` fora de colchetes é literal. O `?` vira `\| ε`. |
| `(MI\|BC\|…\|FZ)` | `Desc` | União das 8 palavras de descritor. |
| `(DZ\|RA\|…\|SA)*` | `Fen*` | Fecho de Kleene: zero ou mais fenômenos (inclui ε). |
| `(DZ\|RA\|…\|SA)+` | `Fen Fen*` | Fecho positivo: `r+ = r r*`, um ou mais fenômenos. |
| `(…\|…)` externo | `(Desc Fen* \| Fen Fen*)` | União dos dois formatos. |

### AFNε

- `q0 → q3` pula a intensidade (o `?`); `q2 → q3` fecha o ramo da intensidade (`-`, `+` ou `VC`).
- `q3 → q4` e `q3 → q12` abrem a união: descritor (bloco `q4`–`q11`) ou fenômeno (bloco `q12`–`q21`).
- `q11 → q22`: depois do descritor, o `Fen*` pode ter zero repetições.
- `q21 → q22`: depois de um fenômeno, chega ao estado final.
- `q22 → q12`: o laço que volta para ler **mais um** fenômeno. É ele que torna a linguagem infinita.

O AFNε usa a propriedade distributiva da concatenação sobre a união:

```
Desc Fen* | Fen Fen*  =  (Desc | Fen) Fen*
```

Os dois ramos terminam em `Fen*`, então o autômato lê um descritor **ou** um fenômeno e, depois, usa um único laço para os fenômenos seguintes. Assim o bloco dos 13 fenômenos aparece uma vez só, em vez de duas. A linguagem é a mesma, e os testes de equivalência confirmam isso.

Dentro dos blocos, palavras com a mesma letra inicial compartilham o primeiro estado: `PR` e `DR` saem de `q4` pela classe `[PD]` e depois leem `R`; `BC` e `BL` leem `B` e depois `[CL]`; `SN`, `SG` e `SA` leem `S` e depois `[NGA]`.

Diagrama e tabela de transições completos: [`docs/afne/ER05.md`](afne/ER05.md).

Traço real do simulador para uma cadeia aceita. Depois de `TS` o autômato já está em `q22` (final) e também em `q12`, pronto para mais um fenômeno:

```
cadeia: +TSRA
início: {q0, q3, q4, q12}
lê '+' → {q2, q3, q4, q12}
lê 'T' → {q9}
lê 'S' → {q11, q12, q22}
lê 'R' → {q14}
lê 'A' → {q12, q21, q22}
resultado: ACEITA
```

E para uma rejeitada. Depois do descritor `TS`, só se pode ler fenômeno (`q12`); não existe transição com `T` a partir dele:

```
cadeia: TSTS
início: {q0, q3, q4, q12}
lê 'T' → {q9}
lê 'S' → {q11, q12, q22}
lê 'T' → ∅
resultado: REJEITADA
```

### Testes

| Aceitas | Observação |
|---|---|
| `RA` | chuva moderada, forma mínima com fenômeno |
| `-RA` | chuva fraca |
| `+TSRA` | trovoada com chuva forte |
| `VCSH` | pancadas nas vizinhanças (descritor sem fenômeno) |
| `BR` | névoa úmida |
| `TS` | **caso-limite**: descritor sozinho (`Fen*` com zero repetições) |
| `-SHRA` | pancadas de chuva fraca |
| `FZDZ` | chuvisco congelante |
| `RABR` | **caso-limite**: dois fenômenos (`Fen+` com duas repetições) |
| `+SHRAGR` | descritor e dois fenômenos |

| Rejeitadas | Motivo |
|---|---|
| `""` | **caso-limite**: cadeia vazia |
| `+` | só a intensidade, sem fenômeno |
| `-VC` | duas indicações de intensidade/proximidade |
| `XX` | código inexistente |
| `RA+` | intensidade depois do fenômeno |
| `VCVC` | VC repetido |
| `TSTS` | **caso-limite**: dois descritores |
| `ra` | letras minúsculas |
| `SHXX` | XX não é fenômeno |
| `-+RA` | **caso-limite**: duas intensidades |

### Resultado e limitações

- Todas as cadeias acima dão o resultado esperado no `re.fullmatch` e no AFNε, e os dois concordam nas cadeias aleatórias e nos passeios pelo laço `q22 → q12`.
- A ER controla só a forma. Aceita combinações sem sentido meteorológico, como `-TS` (trovoada "fraca") ou `RARARA` (o mesmo fenômeno repetido).
- Códigos menos comuns ficaram fora: `UP` (precipitação desconhecida), `SQ` (tempestade de vento), `FC` (funil), `SS`/`DS` (tempestade de areia/poeira) e o prefixo `RE` (tempo recente).

---

## ER-06: Camada de nuvens

| Campo | Conteúdo |
|---|---|
| Identificação | ER-06, grupo de nuvens. O decodificador aceita até 4 grupos desses por boletim, cada um com quantidade, altura e tipo. |
| Alfabeto (Σ) | `D ∪ {B, C, D, E, F, K, N, O, S, T, U, V, W}` |
| Linguagem L | Quantidade (`FEW`, `SCT`, `BKN` ou `OVC`) + altura da base com 3 algarismos (centenas de pés) + tipo opcional (`CB` ou `TCU`); **ou** céu obscurecido `VV` + 3 algarismos (visibilidade vertical); **ou** `NSC` (nenhuma nuvem significativa); **ou** `NCD` (nenhuma nuvem detectada). |
| ER formal | `(FEW \| SCT \| BKN \| OVC) D D D (CB \| TCU \| ε) \| VV D D D \| NSC \| NCD` |
| Sintaxe implementada | `r"(FEW\|SCT\|BKN\|OVC)[0-9]{3}(CB\|TCU)?\|VV[0-9]{3}\|NSC\|NCD"` |
| AFNε | [`docs/afne/ER06.md`](afne/ER06.md): 30 estados, inicial `q0`, final `q29`, 7 movimentos ε. |

### Equivalência entre o código e a notação formal

| No código | Na notação formal | Explicação |
|---|---|---|
| `A…\|VV…\|NSC\|NCD` | `… \| VV D D D \| NSC \| NCD` | Pela precedência (concatenação antes da união), cada `\|` de fora separa uma alternativa **inteira**. Não é preciso parênteses em volta de cada ramo. |
| `(FEW\|SCT\|BKN\|OVC)` | `(FEW \| SCT \| BKN \| OVC)` | União das 4 quantidades. Aqui os parênteses são necessários, senão o `[0-9]{3}` só se ligaria ao `OVC`. |
| `[0-9]{3}` | `D D D` | Repetição exata. |
| `(CB\|TCU)?` | `(CB \| TCU \| ε)` | Tipo de nuvem opcional. |

### AFNε

- `q0 → q1`, `q0 → q18` e `q0 → q24` abrem as alternativas: camada, `VV` e `NSC`/`NCD`.
- `NSC` e `NCD` começam com `N`, então compartilham o estado `q25` e só se separam na 2ª letra (`N(SC | CD)`, que é a mesma linguagem de `NSC | NCD`).
- `q13 → q17` pula o tipo de nuvem (o `?`).
- `q17 → q29`, `q23 → q29` e `q28 → q29` fecham as alternativas no único estado final.

Diagrama e tabela de transições completos: [`docs/afne/ER06.md`](afne/ER06.md).

Traço real do simulador para uma cadeia aceita. Depois da altura, `q29` (final) já está ativo, mas o autômato continua para ler o tipo `CB`:

```
cadeia: BKN015CB
início: {q0, q1, q18, q24}
lê 'B' → {q6}
lê 'K' → {q7}
lê 'N' → {q10}
lê '0' → {q11}
lê '1' → {q12}
lê '5' → {q13, q17, q29}
lê 'C' → {q14}
lê 'B' → {q17, q29}
resultado: ACEITA
```

E para uma rejeitada. `SKC` ("céu claro", usado em outros países) não é aceito: depois de `S` só vem `C` (de `SCT`):

```
cadeia: SKC
início: {q0, q1, q18, q24}
lê 'S' → {q4}
lê 'K' → ∅
resultado: REJEITADA
```

### Testes

| Aceitas | Observação |
|---|---|
| `FEW020` | poucas nuvens a 2.000 pés |
| `SCT015CB` | nuvens esparsas com cumulonimbus |
| `BKN100TCU` | céu nublado com cumulus congestus |
| `OVC008` | céu encoberto a 800 pés |
| `VV002` | céu obscurecido, visibilidade vertical de 200 pés |
| `NSC` | **caso-limite**: alternativa de 3 símbolos, sem altura |
| `NCD` | nenhuma nuvem detectada |
| `FEW000` | **caso-limite**: nuvem junto ao solo (altura 000) |

| Rejeitadas | Motivo |
|---|---|
| `""` | **caso-limite**: cadeia vazia |
| `FEW20` | altura com 2 dígitos |
| `FEW0200` | **caso-limite**: altura com 4 dígitos |
| `SKC` | código SKC não é usado no Brasil |
| `BKN015XB` | XB não é tipo de nuvem |
| `OVC` | falta a altura |
| `VV02` | visibilidade vertical com 2 dígitos |
| `NSCX` | símbolo sobrando depois de NSC |
| `FEWCB` | falta a altura antes do tipo |

### Resultado e limitações

- Todas as cadeias acima dão o resultado esperado no `re.fullmatch` e no AFNε.
- `SKC` e `CLR` foram deixados de fora de propósito: o Brasil usa `NSC` e `NCD`. O programa explica isso na mensagem de erro.
- Estações automáticas às vezes escrevem `///` no lugar do tipo (`FEW020///`); isso não é aceito.
- A ER não verifica se as camadas estão em ordem crescente de altura; essa seria uma melhoria no decodificador.

---

## ER-07: Temperatura e ponto de orvalho

| Campo | Conteúdo |
|---|---|
| Identificação | ER-07, grupo de temperatura e ponto de orvalho em graus Celsius. O decodificador extrai os dois valores, calcula a umidade relativa e avisa quando o orvalho é maior que a temperatura. |
| Alfabeto (Σ) | `D ∪ {M, /}` |
| Linguagem L | Dois algarismos (temperatura), opcionalmente precedidos de `M` (menos, valor negativo), uma barra `/` e mais dois algarismos (ponto de orvalho), também com `M` opcional. |
| ER formal | `(M \| ε) D D / (M \| ε) D D` |
| Sintaxe implementada | `r"M?[0-9]{2}/M?[0-9]{2}"` |
| AFNε | [`docs/afne/ER07.md`](afne/ER07.md): 8 estados, inicial `q0`, final `q7`, 2 movimentos ε. |

### Equivalência entre o código e a notação formal

| No código | Na notação formal | Explicação |
|---|---|---|
| `M?` | `(M \| ε)` | Opcionalidade. O METAR usa `M` porque o `-` já tem outro uso (intensidade fraca). |
| `[0-9]{2}` | `D D` | Repetição exata. |
| `/` | `/` | Literal. Em Python a barra não é metacaractere, então não precisa de escape. |

### AFNε

É o menor autômato do projeto: uma cadeia de estados com dois atalhos.

- `q0 → q1` pula o `M` da temperatura.
- `q4 → q5` pula o `M` do ponto de orvalho.

Diagrama e tabela de transições completos: [`docs/afne/ER07.md`](afne/ER07.md).

Traço real do simulador para uma cadeia aceita:

```
cadeia: M05/M07
início: {q0, q1}
lê 'M' → {q1}
lê '0' → {q2}
lê '5' → {q3}
lê '/' → {q4, q5}
lê 'M' → {q5}
lê '0' → {q6}
lê '7' → {q7}
resultado: ACEITA
```

E para uma rejeitada. Depois do primeiro algarismo o autômato está em `q2`, que exige um segundo algarismo:

```
cadeia: M5/M7
início: {q0, q1}
lê 'M' → {q1}
lê '5' → {q2}
lê '/' → ∅
resultado: REJEITADA
```

### Testes

| Aceitas | Observação |
|---|---|
| `30/24` | típico de Belém |
| `M05/M07` | dois valores negativos |
| `00/M01` | **caso-limite**: zero e negativo |
| `09/09` | temperatura igual ao orvalho (ar saturado) |
| `M00/M00` | **caso-limite**: "menos zero" (entre -0,5 °C e 0 °C) |
| `45/30` | temperatura alta |

| Rejeitadas | Motivo |
|---|---|
| `""` | **caso-limite**: cadeia vazia |
| `30-24` | separador - no lugar de / |
| `3/24` | temperatura com 1 dígito |
| `30/` | falta o ponto de orvalho |
| `M5/M7` | **caso-limite**: valores com 1 dígito |
| `30//24` | barra repetida |
| `MM05/07` | M repetido |
| `30/24M` | M depois do valor |
| `30/245` | orvalho com 3 dígitos |

### Resultado e limitações

- Todas as cadeias acima dão o resultado esperado no `re.fullmatch` e no AFNε.
- A ER aceita `20/25` (orvalho maior que a temperatura), o que é fisicamente impossível. Comparar dois números não é tarefa de ER; o decodificador faz essa checagem e emite um **aviso**.
- Aceita valores extremos como `99/99`.
- Temperaturas com 3 algarismos (acima de 99 °C) não existem na prática e não são aceitas.

---

## ER-08: Pressão QNH

| Campo | Conteúdo |
|---|---|
| Identificação | ER-08, grupo de pressão atmosférica ajustada ao nível do mar (QNH), em hectopascais. É o último grupo obrigatório do boletim. |
| Alfabeto (Σ) | `D ∪ {Q}` |
| Linguagem L | A letra `Q` seguida de 4 algarismos que formam um valor de 0900 a 1099 hPa. |
| ER formal | `Q (0 9 D D \| 1 0 D D)` |
| Sintaxe implementada | `r"Q(09[0-9]{2}\|10[0-9]{2})"` |
| AFNε | [`docs/afne/ER08.md`](afne/ER08.md): 13 estados, inicial `q0`, final `q12`, 4 movimentos ε. |

### Equivalência entre o código e a notação formal

| No código | Na notação formal | Explicação |
|---|---|---|
| `Q` | `Q` | Literal. |
| `09[0-9]{2}` | `0 9 D D` | Valores de 0900 a 0999. |
| `10[0-9]{2}` | `1 0 D D` | Valores de 1000 a 1099. |
| `(…\|…)` | `(… \| …)` | União das duas faixas: é assim que se escreve um intervalo numérico com ER. |

### AFNε

É a construção de Thompson quase sem compactar:

- `q1 → q2` e `q1 → q7` abrem a união das duas faixas.
- `q6 → q12` e `q11 → q12` fecham a união.

Diagrama e tabela de transições completos: [`docs/afne/ER08.md`](afne/ER08.md).

Traço real do simulador para uma cadeia aceita. Depois do `Q`, o fecho-ε já contém os dois ramos (`q2` e `q7`):

```
cadeia: Q1013
início: {q0}
lê 'Q' → {q1, q2, q7}
lê '1' → {q8}
lê '0' → {q9}
lê '1' → {q10}
lê '3' → {q11, q12}
resultado: ACEITA
```

E para uma rejeitada. Depois de `Q1`, a ER só aceita `0` (faixa 10xx):

```
cadeia: Q1100
início: {q0}
lê 'Q' → {q1, q2, q7}
lê '1' → {q8}
lê '1' → ∅
resultado: REJEITADA
```

### Testes

| Aceitas | Observação |
|---|---|
| `Q1013` | pressão padrão |
| `Q0998` | faixa 09xx |
| `Q0900` | **caso-limite**: menor valor aceito |
| `Q1099` | **caso-limite**: maior valor aceito |
| `Q1000` | início da faixa 10xx |
| `Q0950` | pressão baixa |

| Rejeitadas | Motivo |
|---|---|
| `""` | **caso-limite**: cadeia vazia |
| `Q101` | só 3 dígitos |
| `Q10133` | 5 dígitos |
| `Q1100` | **caso-limite**: acima de 1099 hPa |
| `Q0899` | **caso-limite**: abaixo de 0900 hPa |
| `A2992` | pressão em polegadas (A) não prevista |
| `q1013` | q minúsculo |
| `Q 1013` | espaço depois do Q |
| `1013` | falta o Q |

### Resultado e limitações

- Todas as cadeias acima dão o resultado esperado no `re.fullmatch` e no AFNε.
- A faixa 900–1099 hPa cobre as pressões observadas no Brasil. Valores extremos registrados no mundo (abaixo de 900 hPa em furacões) seriam rejeitados.
- O formato em polegadas de mercúrio (`A2992`), usado nos EUA, não é aceito.
- **Exemplo de alteração ao vivo:** para aceitar até 1100 hPa, a ER vira `Q(09[0-9]{2}|10[0-9]{2}|1100)`, e o AFNε ganha um terceiro ramo `q1 -ε→ 1 → 1 → 0 → 0 -ε→ q12`. Os testes de equivalência mostram na hora se as duas mudanças ficaram coerentes.

---

## Como garantimos que a ER e o AFNε reconhecem a mesma linguagem

O guia da disciplina exige que a ER formal, o padrão no código, os testes e o AFNε representem **a mesma linguagem**. Divergência conta como erro conceitual. Em vez de conferir isso só no olho, o projeto confere automaticamente a cada execução dos testes.

### A ideia

Cada ER existe no projeto de duas formas independentes:

1. **O padrão** em `decodmetar/padroes.py`, executado pelo motor de regex do Python (`re.fullmatch`).
2. **O AFNε** em `decodmetar/afne/definicoes.py`, escrito à mão como dados (estados, transições, movimentos ε) e executado pelo nosso simulador em `decodmetar/afne/automato.py`.

Se as duas formas derem a mesma resposta para todas as cadeias testadas, temos forte evidência de que representam a mesma linguagem. Se discordarem em alguma, o teste falha e mostra a cadeia.

O diagrama e a tabela de transições (`docs/afne/`) são **gerados** a partir das mesmas definições do AFNε, então o desenho mostrado é exatamente o autômato que foi testado. Um teste também falha se alguém mudar o AFNε e esquecer de gerar os diagramas de novo.

### O simulador

A simulação segue o algoritmo de AFNε visto em aula:

1. Começa no **fecho-ε** do estado inicial (todos os estados alcançáveis só com movimentos vazios).
2. Para cada símbolo da cadeia, calcula para onde cada estado ativo vai com aquele símbolo (`mover`) e, depois, o fecho-ε do resultado.
3. Se o conjunto ficar vazio (∅), a cadeia já está rejeitada.
4. No fim, aceita se algum estado ativo é final.

Rótulos como `[0-9]` ou `[EW]` são classes finitas, a mesma abreviação de união do guia (`[0-2]` = `0 | 1 | 2`). O simulador expande cada classe para o conjunto de símbolos que ela representa.

### O que os testes verificam (`tests/test_afne.py`)

| Teste | O que faz | Que tipo de erro pega |
|---|---|---|
| Casos fixos | As cadeias aceitas e rejeitadas das fichas (`tests/casos.py`) passam pelo AFNε. | AFNε que não bate com os exemplos documentados. |
| Cadeias aleatórias | 2000 cadeias por ER, de 0 a 12 símbolos, sorteadas do alfabeto da ER mais alguns símbolos estranhos (`x`, espaço, `-`, `/`). | AFNε que aceita lixo. |
| Mutações | Toda cadeia a **uma edição** de distância das aceitas (trocar, remover ou inserir 1 símbolo). | Erros na fronteira da linguagem, como um intervalo trocado ou um ε faltando. |
| Passeios pelo AFNε | Anda ao acaso pelo autômato até um estado final, gerando ~1000 a 1900 cadeias aceitas por ele. Todas precisam ser aceitas pela regex. Depois, 200 delas passam pelas mutações. | AFNε que aceita **mais** do que a regex. |

Ao todo são de 24 mil a 147 mil cadeias distintas comparadas por ER (cerca de 550 mil nas 8 ERs), em poucos segundos. Os números exatos estão em [`resultado_testes.txt`](resultado_testes.txt). Na ER-08, cuja linguagem é finita e tem exatamente 200 cadeias (`Q0900` a `Q1099`), os passeios pelo AFNε encontraram todas elas. A semente do sorteio é fixa (`2026`), então a execução é sempre igual e reproduzível.

### Prova de que o teste funciona

Para verificar que o teste realmente pega erros, plantamos defeitos de propósito no AFNε e rodamos de novo. Todos foram detectados:

| Defeito plantado | Resultado do teste |
|---|---|
| ER-03: `q5 --[0-6]--> q6` trocado por `[0-7]` (aceita direção 370) | falha: `37008KT`, `37015G25KT`… |
| ER-03: removido o ε `q14 → q15` (rajada passa a exigir 3 dígitos) | falha: `18012G10KT`, `06015G25KT`… |
| ER-03: ε extra `q3 → q16` (VRB sem velocidade) | falha: `VRBKT` |
| ER-04: `q12 --[EW]--> q14` trocado por `[EWS]` (aceita "NS") | falha: `1500NS`, `5000NS` |
| ER-01: `q18 --[BDINSW]--> q19` trocado por `[ABDINSW]` (aceita Argentina) | falha: `METAR COR SAAE`, `METAR COR SAAF`… |
| ER-01: removido o ε `q12 → q17` (COR vira obrigatório) | falha: `METAR SBAA`, `METAR SBAE`… |
| ER-02: `q10 --[0-3]--> q11` trocado por `[0-4]` (aceita hora 24) | falha: `012402Z`, `012404Z`… |
| ER-02: `q1 --[1-9]--> q2` trocado por `[0-9]` (aceita dia 00) | falha: `000000Z`, `000019Z`… |
| ER-05: removido o laço ε `q22 → q12` (só 1 fenômeno) | falha: `+FZDZ`, `+GSRA`… |
| ER-05: laço ε extra `q22 → q4` (aceita 2 descritores) | falha: `+BCDR`, `+BCBLBRHZRA`… |
| ER-05: ε extra `q2 → q0` (aceita intensidade repetida) | falha: `+++DR`, `+++--+BLSN`… |
| ER-06: removido o ε `q13 → q17` (tipo de nuvem vira obrigatório) | falha: `FEW000`, `FEW001`… |
| ER-07: removido o ε `q4 → q5` (orvalho passa a exigir M) | falha: `00/01`, `00/09`… |
| ER-08: `q3 --9--> q4` trocado por `[89]` (aceita 08xx) | falha: `Q0800`, `Q0801`… |

### Como rodar

```bash
python -m unittest discover -s tests -v      # todos os testes
python -m tests.relatorio                    # gera docs/resultado_testes.txt
python main.py --gerar-diagramas             # gera docs/afne/ de novo
python main.py --testar ER05 +TSRA           # regex x AFNε com o traço
```

### Para acrescentar ou alterar uma ER

1. Altere o padrão em `PADROES` (`decodmetar/padroes.py`), incluindo a ER formal e o alfabeto.
2. Altere os casos em `CASOS` (`tests/casos.py`).
3. Altere o AFNε em `decodmetar/afne/definicoes.py` (e inclua-o em `AFNES`, se for novo).
4. Rode `python main.py --gerar-diagramas` e os testes.
5. Atualize a ficha em `docs/EXPRESSOES_REGULARES.md`: o teste `tests/test_documentacao.py` falha se o padrão, a ER formal, as cadeias ou os traços da ficha não baterem com o código.

Os testes percorrem `PADROES` e `AFNES` automaticamente. Uma ER sem AFNε, ou sem casos, faz o teste falhar.

### Limitação

Testes não são uma prova matemática: comparam as duas formas numa quantidade grande, mas finita, de cadeias. A prova formal seria converter o AFNε em AFD mínimo e comparar com o AFD mínimo da ER. Como a combinação de casos fixos, fronteira (mutações) e passeios pelo próprio autômato pegou todos os defeitos plantados, consideramos a evidência suficiente para o trabalho.
