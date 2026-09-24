# Expressões Regulares do DecodMETAR

Uma ficha por ER, no formato do *Guia de Sintaxe para Apresentação das Expressões Regulares*.
Cada integrante escreve as fichas das próprias ERs; a versão final junta as oito.

Notação usada em todas as fichas:

- `D = (0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9)`, os algarismos.
- `ε` é a palavra vazia.
- No código, todas as ERs são aplicadas com `re.fullmatch`, que exige que a cadeia **inteira** pertença à linguagem. Por isso os padrões não usam as âncoras `^` e `$`.

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
36015G25KT
início: {q0}
--3--> {q5}
--6--> {q6}
--0--> {q7, q8}
--1--> {q9}
--5--> {q10, q11, q16}
--G--> {q12}
--2--> {q13}
--5--> {q14, q15, q16}
--K--> {q17}
--T--> {q18}
resultado: ACEITA
```

E para uma rejeitada. A direção 361° não termina em 0, então não existe transição de `q6` com o símbolo `1`:

```
36115KT
início: {q0}
--3--> {q5}
--6--> {q6}
--1--> ∅
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

- Todas as cadeias acima dão o resultado esperado no `re.fullmatch` e no AFNε. As duas implementações também concordam em milhares de cadeias geradas ao acaso (ver [Como garantimos a equivalência](EQUIVALENCIA_ER_AFNE.md)).
- A ER valida só a **forma** do grupo. Ela aceita `09020G10KT` (rajada menor que a velocidade média) e `VRB999KT` (999 nós). Checagens de sentido, como rajada menor que a média, ficam para o decodificador (plano, seção 6.2), não para a ER.
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
5000NE                               5000NNE
início: {q0, q1, q7}                 início: {q0, q1, q7}
--5--> {q8}                          --5--> {q8}
--0--> {q9}                          --0--> {q9}
--0--> {q10}                         --0--> {q10}
--0--> {q11, q15}                    --0--> {q11, q15}
--N--> {q12, q15}                    --N--> {q12, q15}
--E--> {q14, q15}                    --N--> ∅
resultado: ACEITA                    resultado: REJEITADA
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
