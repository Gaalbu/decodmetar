# Como garantimos que a ER e o AFNε reconhecem a mesma linguagem

O guia da disciplina exige que a ER formal, o padrão no código, os testes e o AFNε representem **a mesma linguagem**. Divergência conta como erro conceitual. Em vez de conferir isso só no olho, o projeto confere automaticamente a cada execução dos testes.

## A ideia

Cada ER existe no projeto de duas formas independentes:

1. **O padrão** em `decodmetar/padroes.py`, executado pelo motor de regex do Python (`re.fullmatch`).
2. **O AFNε** em `decodmetar/afne/definicoes.py`, escrito à mão como dados (estados, transições, movimentos ε) e executado pelo nosso simulador em `decodmetar/afne/automato.py`.

Se as duas formas derem a mesma resposta para todas as cadeias testadas, temos forte evidência de que representam a mesma linguagem. Se discordarem em alguma, o teste falha e mostra a cadeia.

O diagrama e a tabela de transições (`docs/afne/`) são **gerados** a partir das mesmas definições do AFNε, então o desenho mostrado nos slides é exatamente o autômato que foi testado. Um teste também falha se alguém mudar o AFNε e esquecer de gerar os diagramas de novo.

## O simulador

A simulação segue o algoritmo de AFNε visto em aula:

1. Começa no **fecho-ε** do estado inicial (todos os estados alcançáveis só com movimentos vazios).
2. Para cada símbolo da cadeia, calcula para onde cada estado ativo vai com aquele símbolo (`mover`) e, depois, o fecho-ε do resultado.
3. Se o conjunto ficar vazio (∅), a cadeia já está rejeitada.
4. No fim, aceita se algum estado ativo é final.

Rótulos como `[0-9]` ou `[EW]` são classes finitas, a mesma abreviação de união do guia (`[0-2]` = `0 | 1 | 2`). O simulador expande cada classe para o conjunto de símbolos que ela representa.

## O que os testes verificam (`tests/test_afne.py`)

| Teste | O que faz | Que tipo de erro pega |
|---|---|---|
| Casos fixos | As cadeias aceitas e rejeitadas das fichas (`tests/casos.py`) passam pelo AFNε. | AFNε que não bate com os exemplos documentados. |
| Cadeias aleatórias | 2000 cadeias por ER, de 0 a 12 símbolos, sorteadas do alfabeto da ER mais alguns símbolos estranhos (`x`, espaço, `-`, `/`). | AFNε que aceita lixo. |
| Mutações | Toda cadeia a **uma edição** de distância das aceitas (trocar, remover ou inserir 1 símbolo). | Erros na fronteira da linguagem, como um intervalo trocado ou um ε faltando. |
| Passeios pelo AFNε | Anda ao acaso pelo autômato até um estado final, gerando ~1000 a 1900 cadeias aceitas por ele. Todas precisam ser aceitas pela regex. Depois, 200 delas passam pelas mutações. | AFNε que aceita **mais** do que a regex. |

Ao todo são mais de 50 mil cadeias comparadas por ER, em menos de 1 segundo. A semente do sorteio é fixa (`2026`), então a execução é sempre igual e reproduzível.

## Prova de que o teste funciona

Para verificar que o teste realmente pega erros, plantamos defeitos de propósito no AFNε e rodamos de novo. Todos foram detectados:

| Defeito plantado | Resultado do teste |
|---|---|
| ER-03: `q5 --[0-6]--> q6` trocado por `[0-7]` (aceita direção 370) | falha: `37008KT`, `37015G25KT`… |
| ER-03: removido o ε `q14 → q15` (rajada passa a exigir 3 dígitos) | falha: `18012G10KT`, `06015G25KT`… |
| ER-03: ε extra `q3 → q16` (VRB sem velocidade) | falha: `VRBKT` |
| ER-04: `q12 --[EW]--> q14` trocado por `[EWS]` (aceita "NS") | falha: `1500NS`, `5000NS` |

## Como rodar

```bash
python -m unittest discover -s tests -v      # todos os testes
python -m decodmetar.afne.diagramas          # gera docs/afne/ de novo
```

Para ver o traço de uma cadeia (útil na demonstração):

```python
from decodmetar.afne.definicoes import AFNES
print(AFNES["ER03"].formatar_traco("36015G25KT"))
```

## Para as outras ERs

Para ligar uma nova ER a essa verificação:

1. Adicione o padrão em `PADROES` (`decodmetar/padroes.py`).
2. Adicione os casos em `CASOS` (`tests/casos.py`).
3. Adicione o AFNε em `decodmetar/afne/definicoes.py` e inclua-o em `AFNES`.
4. Rode `python -m decodmetar.afne.diagramas` e os testes.

Os testes percorrem `PADROES` e `AFNES` automaticamente. Uma ER sem AFNε, ou sem casos, faz o teste falhar.

## Limitação

Testes não são uma prova matemática: comparam as duas formas numa quantidade grande, mas finita, de cadeias. A prova formal seria converter o AFNε em AFD mínimo e comparar com o AFD mínimo da ER. Como a combinação de casos fixos, fronteira (mutações) e passeios pelo próprio autômato pegou todos os defeitos plantados, consideramos a evidência suficiente para o trabalho.
