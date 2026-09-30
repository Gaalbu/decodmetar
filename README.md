# DecodMETAR

Validador e decodificador de boletins meteorológicos aeronáuticos (METAR/SPECI) com Expressões Regulares.

Trabalho do 1º Bimestre, Linguagens Formais e Autômatos (CESUPA). Entrega e apresentação: **30/09/2026**.

**Equipe:** Davi Maciel Corrêa, Gabriel Albuquerque Alencar, José Valdez e Alberto Acosta. Contribuições em [`CONTRIBUICOES.md`](CONTRIBUICOES.md).

## O problema

Todo aeroporto publica, de hora em hora, um boletim METAR com o tempo do momento. Ele é compacto e codificado, ilegível para quem não é da área:

```
METAR SBBE 241200Z 09010KT 9999 -RA FEW020 SCT100 30/24 Q1011
```

Além disso, um erro de digitação (dia 32, vento de 370°, pressão 1100) passa fácil despercebido.

## A solução

O programa recebe um boletim (digitado ou lido de um arquivo), separa os grupos, confere cada um com uma **Expressão Regular** e mostra o boletim traduzido para o português. Quando algum grupo está errado, aponta qual é e explica o motivo.

- **Entrada:** um boletim digitado, ou um arquivo `.txt` com um boletim por linha.
- **Processamento:** cabeçalho validado pela ER-01; cada grupo seguinte encaixado na próxima posição esperada (ER-02 a ER-08); valores extraídos do grupo já validado.
- **Saída:** tradução grupo a grupo, erros com o motivo, avisos semânticos e, no modo arquivo, um resumo.

```
$ python main.py "METAR SBBE 241200Z 09010KT 9999 -RA FEW020 30/24 Q1011"
------------------------------------------------------------------------
Boletim: METAR SBBE 241200Z 09010KT 9999 -RA FEW020 30/24 Q1011
------------------------------------------------------------------------
  METAR SBBE      ER-01  METAR (observação regular, de hora em hora) do aeródromo SBBE, Belém/Val-de-Cans (PA)
  241200Z         ER-02  Observação do dia 24 às 12:00 UTC (09:00 no horário de Brasília)
  09010KT         ER-03  Vento de 090° (vindo do leste) a 10 nós (19 km/h)
  9999            ER-04  Visibilidade de 10 km ou mais
  -RA             ER-05  Tempo presente: chuva (intensidade fraca)
  FEW020          ER-06  Poucas nuvens (1 a 2 oitavos do céu) a 2.000 pés (610 m)
  30/24           ER-07  Temperatura de 30 °C e ponto de orvalho de 24 °C (umidade relativa de cerca de 70%)
  Q1011           ER-08  Pressão ajustada ao nível do mar (QNH) de 1.011 hPa
Resultado: boletim VÁLIDO
```

```
$ python main.py "METAR SBBE 321200Z 37010KT 9999 FEW020 30/24 Q1011"
  ...
  ERRO: Grupo '321200Z' parece ser data e hora da observação (ER-02), mas é inválido: dia 32 não existe (deve estar entre 01 e 31).
  ERRO: Grupo '37010KT' parece ser vento de superfície (ER-03), mas é inválido: direção 370° acima de 360°.
Resultado: boletim INVÁLIDO (2 erro(s))
```

Cada ER também tem um **AFNε equivalente**, escrito como dados em Python e executado por um simulador próprio. Os testes rodam cada cadeia no `re.fullmatch` e no AFNε e exigem que os dois concordem.

## As 8 Expressões Regulares

| ID | Grupo | Padrão no código | AFNε |
|----|-------|------------------|------|
| ER-01 | Identificação do boletim | `(METAR\|SPECI) (COR )?S[BDINSW][A-Z]{2}` | [ER01](docs/afne/ER01.md) |
| ER-02 | Data/hora | `(0[1-9]\|[12][0-9]\|3[01])([01][0-9]\|2[0-3])[0-5][0-9]Z` | [ER02](docs/afne/ER02.md) |
| ER-03 | Vento | `(VRB\|([0-2][0-9]\|3[0-6])0)[0-9]{2,3}(G[0-9]{2,3})?KT` | [ER03](docs/afne/ER03.md) |
| ER-04 | Visibilidade | `CAVOK\|[0-9]{4}(N\|NE\|E\|SE\|S\|SW\|W\|NW)?` | [ER04](docs/afne/ER04.md) |
| ER-05 | Tempo presente | `(-\|\+\|VC)?((MI\|BC\|PR\|DR\|BL\|SH\|TS\|FZ)(DZ\|RA\|SN\|SG\|PL\|GR\|GS\|BR\|FG\|FU\|HZ\|DU\|SA)*\|(DZ\|RA\|SN\|SG\|PL\|GR\|GS\|BR\|FG\|FU\|HZ\|DU\|SA)+)` | [ER05](docs/afne/ER05.md) |
| ER-06 | Nuvens | `(FEW\|SCT\|BKN\|OVC)[0-9]{3}(CB\|TCU)?\|VV[0-9]{3}\|NSC\|NCD` | [ER06](docs/afne/ER06.md) |
| ER-07 | Temperatura/orvalho | `M?[0-9]{2}/M?[0-9]{2}` | [ER07](docs/afne/ER07.md) |
| ER-08 | Pressão QNH | `Q(09[0-9]{2}\|10[0-9]{2})` | [ER08](docs/afne/ER08.md) |

(Na tabela, `\|` é só o escape do Markdown; no código é `|`.)

As fichas completas (alfabeto, linguagem, ER formal, sintaxe, equivalência dos operadores, AFNε, testes e limitações) estão em [`docs/EXPRESSOES_REGULARES.md`](docs/EXPRESSOES_REGULARES.md).

## Instalação

Requisito: **Python 3.10 ou mais novo**. O programa usa só a biblioteca padrão; não há nada para instalar com `pip` (ver [`requirements.txt`](requirements.txt)).

```bash
git clone https://github.com/Gaalbu/decodmetar.git
cd decodmetar
python --version
```

No Linux/macOS, use `python3` no lugar de `python` se for o caso.

## Como executar

Menu interativo:

```bash
python main.py
```

```
=== DecodMETAR ===
1) Decodificar um boletim digitado
2) Processar arquivo de boletins
3) Testar uma cadeia em uma ER (regex + AFNε com traço)
4) Listar as expressões regulares do programa
5) Rodar a bateria de testes
6) Gerar de novo os diagramas dos AFNε (docs/afne/)
0) Sair
```

Direto pela linha de comando:

```bash
python main.py "METAR SBBE 241200Z 09010KT 9999 FEW020 30/24 Q1011"
```

```bash
python main.py --arquivo dados/metar_misto.txt
```

```bash
python main.py --testar ER03 36015G25KT
```

```bash
python main.py --listar
```

```bash
python main.py --gerar-diagramas
```

O `--testar` (e a opção 3 do menu) é o modo da demonstração: mostra o alfabeto, a ER formal, o padrão do código, o resultado do `re.fullmatch`, o do AFNε e o traço do AFNε símbolo a símbolo:

```
$ python main.py --testar ER08 Q1100
  ...
  re.fullmatch: REJEITADA
  AFNε        : REJEITADA

  Traço do AFNε (inicial q0, finais q12):
    início: {q0}
    lê 'Q' → {q1, q2, q7}
    lê '1' → {q8}
    lê '1' → ∅
    resultado: REJEITADA
```

Entradas vazias ou inválidas não derrubam o programa: boletim vazio, opção de menu inválida, ER inexistente, arquivo inexistente/vazio/pasta/não UTF-8 e `Ctrl+C` geram mensagens claras.

## Testes

```bash
python -m unittest discover -s tests -v
```

```bash
python -m tests.relatorio
```

O primeiro roda os 71 testes; o segundo gera [`docs/resultado_testes.txt`](docs/resultado_testes.txt) com a tabela por ER e a saída completa. Resumo da última execução:

- **129 cadeias fixas** (≥ 6 aceitas e ≥ 6 rejeitadas por ER, com casos-limite): todas com o resultado esperado na regex e no AFNε.
- **~552 mil cadeias geradas** (aleatórias, mutações a uma edição das aceitas e passeios pelo próprio AFNε): **nenhuma divergência** entre regex e AFNε.
- Testes do decodificador (boletins válidos, inválidos, avisos, arquivos), da interface (linha de comando e menu) e da documentação (a ficha tem de mostrar o mesmo padrão, ER formal, cadeias e traços do código).

Como a equivalência ER × AFNε é verificada: seção final de [`docs/EXPRESSOES_REGULARES.md`](docs/EXPRESSOES_REGULARES.md).

## Estrutura do repositório

```
decodmetar/
├── README.md                    este arquivo
├── CONTRIBUICOES.md             registro das contribuições dos integrantes
├── requirements.txt             dependências (nenhuma externa)
├── main.py                      ponto de entrada (menu + linha de comando)
├── decodmetar/                  código-fonte
│   ├── padroes.py               as 8 ERs (única fonte dos padrões)
│   ├── decodificador.py         ordem dos grupos, diagnóstico e tradução
│   ├── mensagens.py             tabelas de tradução e textos
│   └── afne/
│       ├── automato.py          classe AFNe: fecho-ε, aceitação e traço
│       ├── definicoes.py        os 8 AFNε como dados
│       └── diagramas.py         gera os diagramas Mermaid e as tabelas de transição
├── tests/                       casos de teste e testes automáticos
├── dados/                       boletins de exemplo
└── docs/
    ├── EXPRESSOES_REGULARES.md  as 8 fichas + como garantimos ER ≡ AFNε
    ├── afne/                    diagramas dos AFNε: ERxx.md (Mermaid + tabela) e ERxx.svg
    ├── resultado_testes.txt     saída real dos testes
    └── RELATORIO_TECNICO.pdf    relatório técnico
```

## Dados de exemplo

Os arquivos em [`dados/`](dados/) são **exemplos sintéticos criados pela equipe** (não são boletins oficiais), com indicativos reais de aeródromos brasileiros:

| Arquivo | Conteúdo |
|---|---|
| `metar_validos.txt` | 10 boletins bem formados (COR, CAVOK, rajada, temperatura negativa, várias camadas, RMK…) |
| `metar_com_erros.txt` | 12 boletins, cada um com um erro diferente |
| `metar_misto.txt` | mistura de válidos, inválidos, avisos e linhas em branco (para a demonstração) |

Linhas em branco e linhas começando com `#` são ignoradas.

## Escopo e limitações

- O programa cobre o METAR brasileiro "de todo dia". Grupos menos comuns (variação de direção do vento `350V040`, RVR, tempo recente `RE…`, tendência `BECMG`/`TEMPO`) não são decodificados; `AUTO` e `NOSIG` são ignorados, e tudo depois de `RMK`, `BECMG` ou `TEMPO` também.
- As ERs validam a **forma**, não o sentido: aceitam o dia 31 em qualquer mês e aeródromos que não existem (`SIZZ`). Checagens que dependem de comparar valores (orvalho > temperatura, rajada ≤ média) viram **avisos** no decodificador.
- Os testes de equivalência comparam regex e AFNε em muitas cadeias, mas não são uma prova formal.

Limitações de cada ER: seção "Resultado e limitações" de cada ficha.

## Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/EXPRESSOES_REGULARES.md`](docs/EXPRESSOES_REGULARES.md) | As 8 fichas no formato do guia e a verificação ER ≡ AFNε |
| [`docs/afne/`](docs/afne/) | Diagramas e tabelas de transição dos AFNε |
| [`docs/resultado_testes.txt`](docs/resultado_testes.txt) | Resultado real dos testes |
| [`docs/RELATORIO_TECNICO.pdf`](docs/RELATORIO_TECNICO.pdf) | Relatório técnico |
| [`CONTRIBUICOES.md`](CONTRIBUICOES.md) | Contribuições dos integrantes |

## Uso de Inteligência Artificial

Usamos IA (Claude, da Anthropic) nas seguintes tarefas:

- elaborar o plano de execução e sugerir as ERs e os casos de teste;
- escrever parte do código (ERs, AFNε, decodificador, interface) e dos testes;
- redigir parte da documentação (README, fichas e relatório);
- extrair o texto do guia da disciplina para conferir o formato das fichas.

Toda a equipe revisou o conteúdo e é responsável por entendê-lo, explicá-lo e modificá-lo. Nenhum resultado de teste foi escrito à mão: os números vêm da execução real (`python -m tests.relatorio`).

## Referências

- Guia de Sintaxe para Apresentação das Expressões Regulares (material da disciplina).
- ICAO. *Annex 3: Meteorological Service for International Air Navigation*.
- DECEA. Manual de Códigos Meteorológicos (MCA 105-10), formato METAR/SPECI no Brasil.
- HOPCROFT, J. E.; MOTWANI, R.; ULLMAN, J. D. *Introdução à Teoria de Autômatos, Linguagens e Computação*.
- Documentação do módulo `re` do Python: https://docs.python.org/3/library/re.html
- Mermaid (diagramas): https://mermaid.js.org
- WMO. *Guide to Instruments and Methods of Observation* (WMO-No. 8), fórmula de Magnus usada no cálculo da umidade relativa.
