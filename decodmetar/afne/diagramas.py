"""Gera os diagramas dos AFNε (Mermaid) e as tabelas de transição a partir das definições.

Uso: python -m decodmetar.afne.diagramas [pasta_de_saida]
"""

import sys
from pathlib import Path

from decodmetar.afne.automato import EPSILON
from decodmetar.afne.definicoes import AFNES
from decodmetar.padroes import PADROES

PASTA_PADRAO = Path(__file__).resolve().parents[2] / "docs" / "afne"


def exibir(rotulo):
    """Rótulo como aparece no diagrama: o espaço vira ␣ para ficar visível."""
    return "␣" if rotulo == " " else rotulo


def _arestas(afne):
    """Agrupa símbolos com mesma origem e destino (q0 --a, b--> q1).

    O ε nunca entra no grupo, para aparecer sempre como seta tracejada própria.
    """
    agrupadas = {}
    for origem in afne.estados:
        for rotulo, destino in afne.transicoes[origem]:
            chave = (origem, destino, rotulo == EPSILON)
            agrupadas.setdefault(chave, []).append(exibir(rotulo))
    return [(o, d, ", ".join(r)) for (o, d, _), r in agrupadas.items()]


def mermaid(afne):
    linhas = [
        "flowchart LR",
        "    classDef oculto fill:none,stroke:none,color:none",
        '    inicio[" "]:::oculto --> ' + afne.inicial,
    ]
    for estado in afne.estados:
        forma = f'((("{estado}")))' if estado in afne.finais else f'(("{estado}"))'
        linhas.append(f"    {estado}{forma}")
    for origem, destino, rotulo in _arestas(afne):
        seta = "-.->" if rotulo == EPSILON else "-->"
        linhas.append(f'    {origem} {seta}|"{rotulo}"| {destino}')
    return "\n".join(linhas)


def tabela_transicoes(afne):
    linhas = ["| Estado | Símbolo | Destino |", "|---|---|---|"]
    for origem in afne.estados:
        marca = ("→ " if origem == afne.inicial else "") + ("* " if origem in afne.finais else "")
        for rotulo, destino in afne.transicoes[origem]:
            linhas.append(f"| {marca}{origem} | `{exibir(rotulo)}` | {destino} |")
    return "\n".join(linhas)


def documento(afne):
    er = PADROES[afne.nome]
    vazios = [
        f"{o} → {d}" for o in afne.estados for r, d in afne.transicoes[o] if r == EPSILON
    ]
    return f"""# AFNε da {er.id[:2]}-{er.id[2:]}: {er.nome}

> Arquivo gerado por `python -m decodmetar.afne.diagramas`. Não edite à mão:
> altere `decodmetar/afne/definicoes.py` e gere de novo.

Padrão no código: `{er.padrao}`

- Estados: {len(afne.estados)} ({", ".join(afne.estados)})
- Estado inicial: {afne.inicial}
- Estados finais: {", ".join(sorted(afne.finais))}
- Movimentos vazios (ε): {", ".join(vazios) if vazios else "nenhum"}

Legenda: setas tracejadas são movimentos ε; círculo duplo é estado final.
Rótulos como `[0-9]` são classes finitas, abreviação da união dos símbolos
(ex.: `[0-2]` = `0 | 1 | 2`). O símbolo `␣` representa o espaço.

```mermaid
{mermaid(afne)}
```

O mesmo diagrama em imagem: [`{afne.nome}.svg`]({afne.nome}.svg) (exportada do Mermaid acima).

## Tabela de transições

`→` marca o estado inicial e `*` os estados finais.

{tabela_transicoes(afne)}
"""


def gerar(pasta=PASTA_PADRAO):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    gerados = []
    for nome, afne in AFNES.items():
        caminho = pasta / f"{nome}.md"
        caminho.write_text(documento(afne), encoding="utf-8")
        gerados.append(caminho)
    return gerados


if __name__ == "__main__":
    for caminho in gerar(sys.argv[1] if len(sys.argv) > 1 else PASTA_PADRAO):
        print(f"gerado: {caminho}")
