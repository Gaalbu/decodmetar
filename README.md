# DecodMETAR

Validador e decodificador de boletins meteorológicos aeronáuticos (METAR/SPECI) com Expressões Regulares.

Trabalho do 1º Bimestre, Linguagens Formais e Autômatos (CESUPA). Entrega e apresentação: **30/09/2026**.

> **Status:** planejamento. Este repositório ainda não tem código. O plano completo está em [`PLANO_DE_EXECUCAO.md`](PLANO_DE_EXECUCAO.md).

## A ideia

Todo aeroporto publica, de hora em hora, um boletim METAR com o tempo do momento:

```
METAR SBBE 241200Z 09010KT 9999 -RA FEW020 30/24 Q1011
```

O programa recebe um boletim (digitado ou lido de um arquivo), confere cada grupo com uma Expressão Regular e mostra o boletim traduzido para o português ("vento de 090° a 10 nós", "chuva fraca", "pressão 1011 hPa"…). Quando algum grupo está errado, aponta qual é e explica o motivo.

Cada ER tem um AFNε equivalente, escrito como dados em Python. Os testes rodam cada cadeia no `re.fullmatch` e no simulador do AFNε e exigem que os dois resultados sejam iguais.

## As 8 Expressões Regulares

| ID | Grupo | Padrão no código |
|----|-------|------------------|
| ER-01 | Identificação do boletim | `(METAR\|SPECI) (COR )?S[BDINSW][A-Z]{2}` |
| ER-02 | Data/hora | `(0[1-9]\|[12][0-9]\|3[01])([01][0-9]\|2[0-3])[0-5][0-9]Z` |
| ER-03 | Vento | `(VRB\|([0-2][0-9]\|3[0-6])0)[0-9]{2,3}(G[0-9]{2,3})?KT` |
| ER-04 | Visibilidade | `CAVOK\|[0-9]{4}(N\|NE\|E\|SE\|S\|SW\|W\|NW)?` |
| ER-05 | Tempo presente | `(-\|\+\|VC)?((MI\|BC\|PR\|DR\|BL\|SH\|TS\|FZ)(DZ\|RA\|SN\|SG\|PL\|GR\|GS\|BR\|FG\|FU\|HZ\|DU\|SA)*\|(DZ\|RA\|SN\|SG\|PL\|GR\|GS\|BR\|FG\|FU\|HZ\|DU\|SA)+)` |
| ER-06 | Nuvens | `(FEW\|SCT\|BKN\|OVC)[0-9]{3}(CB\|TCU)?\|VV[0-9]{3}\|NSC\|NCD` |
| ER-07 | Temperatura/orvalho | `M?[0-9]{2}/M?[0-9]{2}` |
| ER-08 | Pressão QNH | `Q(09[0-9]{2}\|10[0-9]{2})` |

A ficha de cada ER (alfabeto, linguagem, ER formal, testes) está na seção 3 do plano.

## Divisão de tarefas

Cada integrante é dono de **duas ERs**, do começo ao fim: padrão no código, ficha, AFNε, testes e a parte dessas ERs nos slides. Na apresentação, cada um explica as próprias ERs. Além disso, cada um fica com uma parte da aplicação ou da documentação.

Os nomes estão como marcadores. Troquem pelos nomes completos antes da entrega.

### [Integrante 1]: ER-01 e ER-02 + decodificador

- **ERs:** ER-01 (identificação do boletim) e ER-02 (data/hora).
- **Arquivos:** `decodmetar/decodificador.py`, `decodmetar/mensagens.py`, `tests/test_decodificador.py`.
- **Tarefas:**
  - fluxo de decodificação: tokenização, ordem dos grupos, extração dos valores e tradução (plano, seção 6.2);
  - tratamento de `COR`, `=` final e grupos ignorados (`AUTO`, `NOSIG`, `RMK`);
  - avisos semânticos, como orvalho maior que a temperatura.
- **Na apresentação:** problema, solução e arquitetura.

### [Integrante 2]: ER-03 e ER-04 + AFNε e simulador

- **ERs:** ER-03 (vento) e ER-04 (visibilidade).
- **Arquivos:** `decodmetar/afne/automato.py`, `decodmetar/afne/diagramas.py`, `tests/test_afne.py`.
- **Tarefas:**
  - classe `AFNe` com fecho-ε, aceitação e traço passo a passo (plano, seção 5.1);
  - geração dos diagramas em Mermaid e Graphviz em `docs/afne/` (seção 5.4);
  - teste de equivalência regex × AFNε, com as cadeias fixas e as aleatórias (seção 5.3);
  - revisar os AFNε dos colegas, rodando os testes.
- **Na apresentação:** como a equivalência entre ER e AFNε é garantida.

### [Integrante 3]: ER-05 e ER-06 + interface e testes

- **ERs:** ER-05 (tempo presente, a mais complexa) e ER-06 (nuvens).
- **Arquivos:** `main.py`, `decodmetar/padroes.py`, `tests/casos.py`, `tests/test_padroes.py`, `dados/`.
- **Tarefas:**
  - menu interativo e argumentos de linha de comando (plano, seção 6.3);
  - tratamento de entrada vazia, opção inválida, arquivo inexistente e `Ctrl+C`;
  - tabela de casos de teste de todas as ERs (seção 4);
  - arquivos de exemplo em `dados/` (seção 8);
  - salvar a saída dos testes em `docs/resultado_testes.txt`.
- **Na apresentação:** demonstração ao vivo, com uma cadeia aceita e uma rejeitada.

### [Integrante 4]: ER-07 e ER-08 + documentação

- **ERs:** ER-07 (temperatura/orvalho) e ER-08 (pressão).
- **Arquivos:** `docs/EXPRESSOES_REGULARES.md`, `docs/RELATORIO_TECNICO.md`, `docs/APRESENTACAO_ROTEIRO.md`, `CONTRIBUICOES.md`.
- **Tarefas:**
  - juntar as 8 fichas no formato do guia do professor (plano, seção 9);
  - relatório técnico em PDF e slides;
  - seção de uso de IA e referências;
  - checklist final (seção 11).
- **Na apresentação:** testes e resultados, limitações, melhorias e contribuições.

### Tarefas de todos

- [ ] **Até 26/09:** preencher a planilha da Etapa 1 (texto sugerido na seção 9.6 do plano).
- [ ] Escrever a ficha e o AFNε das suas duas ERs e conferir se os testes passam.
- [ ] Entender todas as 8 ERs: o professor pode perguntar sobre qualquer uma e pedir alterações ao vivo.
- [ ] Ensaiar a apresentação (10 a 12 minutos).

## Cronograma

| Data | Entrega |
|------|---------|
| 26/09 | Planilha da Etapa 1 preenchida |
| 27/09 | `padroes.py` + casos de teste + `automato.py` prontos |
| 28/09 | AFNε das 8 ERs passando no teste de equivalência; decodificador e menu funcionando |
| 29/09 | Documentação, relatório (PDF), slides e ensaio |
| 30/09 | Entrega no Classroom antes da aula e apresentação |

## Como executar (quando o código existir)

Requisitos: Python ≥ 3.10. Só usa a biblioteca padrão, sem dependências externas.

```bash
python main.py                                   # menu interativo
python main.py "METAR SBBE 241200Z 09010KT 9999 FEW020 30/24 Q1011"
python main.py --arquivo dados/metar_misto.txt
python main.py --testar ER03 36015G25KT          # regex + traço do AFNε
python -m unittest discover -s tests -v          # testes
```

## Uso de Inteligência Artificial

Usamos IA (Claude) para elaborar o plano de execução, sugerir as ERs e os casos de teste e redigir este README. Toda a equipe revisou o conteúdo e é responsável por entendê-lo, explicá-lo e modificá-lo. Esta seção será atualizada com as tarefas em que a IA também for usada na implementação.

## Referências

- Guia de Sintaxe para Apresentação das Expressões Regulares (material da disciplina).
- ICAO, Annex 3: Meteorological Service for International Air Navigation, e manuais de códigos meteorológicos do DECEA (formato METAR).
- Documentação do módulo `re` do Python: https://docs.python.org/3/library/re.html
