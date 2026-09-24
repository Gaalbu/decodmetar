"""Expressões Regulares do DecodMETAR: única fonte da verdade dos padrões."""

import re
from dataclasses import dataclass, field


@dataclass
class ExpressaoRegular:
    id: str
    nome: str
    padrao: str
    descricao: str
    compilado: re.Pattern = field(init=False, repr=False)

    def __post_init__(self):
        self.compilado = re.compile(self.padrao)


PADROES = {
    er.id: er
    for er in [
        ExpressaoRegular(
            "ER03",
            "Vento de superfície",
            r"(VRB|([0-2][0-9]|3[0-6])0)[0-9]{2,3}(G[0-9]{2,3})?KT",
            "Direção VRB ou 000–360 em dezenas, velocidade com 2 ou 3 dígitos, "
            "rajada opcional (G + 2 ou 3 dígitos) e unidade KT.",
        ),
        ExpressaoRegular(
            "ER04",
            "Visibilidade predominante",
            r"CAVOK|[0-9]{4}(N|NE|E|SE|S|SW|W|NW)?",
            "CAVOK ou 4 dígitos (metros) com direção cardeal/colateral opcional.",
        ),
    ]
}


def valida(id_er, cadeia):
    """Retorna True se a cadeia inteira pertence à linguagem da ER."""
    return PADROES[id_er].compilado.fullmatch(cadeia) is not None
