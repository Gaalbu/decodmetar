"""AFNε de cada ER, construídos à mão no estilo de Thompson compacto.

ε aparece onde a ER tem escolha: fim dos ramos de uma união, opcional (r? = r|ε)
e repetição limitada (r{2,3} = rr(r|ε)).
"""

from decodmetar.afne.automato import EPSILON as E
from decodmetar.afne.automato import AFNe


def _numerados(n):
    return [f"q{i}" for i in range(n)]


# ER-03: (VRB|([0-2][0-9]|3[0-6])0)[0-9]{2,3}(G[0-9]{2,3})?KT
ER03 = AFNe(
    "ER03",
    _numerados(19),
    "q0",
    {"q18"},
    {
        # direção: VRB
        "q0": [("V", "q1"), ("[0-2]", "q4"), ("3", "q5")],
        "q1": [("R", "q2")],
        "q2": [("B", "q3")],
        "q3": [(E, "q8")],
        # direção: 000–290 ou 300–360, sempre terminando em 0
        "q4": [("[0-9]", "q6")],
        "q5": [("[0-6]", "q6")],
        "q6": [("0", "q7")],
        "q7": [(E, "q8")],
        # velocidade: [0-9]{2,3}
        "q8": [("[0-9]", "q9")],
        "q9": [("[0-9]", "q10")],
        "q10": [("[0-9]", "q11"), (E, "q11")],
        # rajada opcional: (G[0-9]{2,3})?
        "q11": [("G", "q12"), (E, "q16")],
        "q12": [("[0-9]", "q13")],
        "q13": [("[0-9]", "q14")],
        "q14": [("[0-9]", "q15"), (E, "q15")],
        "q15": [(E, "q16")],
        # unidade
        "q16": [("K", "q17")],
        "q17": [("T", "q18")],
    },
)

# ER-04: CAVOK|[0-9]{4}(N|NE|E|SE|S|SW|W|NW)?
ER04 = AFNe(
    "ER04",
    _numerados(16),
    "q0",
    {"q15"},
    {
        # união de topo
        "q0": [(E, "q1"), (E, "q7")],
        # ramo CAVOK
        "q1": [("C", "q2")],
        "q2": [("A", "q3")],
        "q3": [("V", "q4")],
        "q4": [("O", "q5")],
        "q5": [("K", "q6")],
        "q6": [(E, "q15")],
        # ramo numérico: [0-9]{4}
        "q7": [("[0-9]", "q8")],
        "q8": [("[0-9]", "q9")],
        "q9": [("[0-9]", "q10")],
        "q10": [("[0-9]", "q11")],
        # direção opcional; N e S são prefixos de NE/NW e SE/SW
        "q11": [(E, "q15"), ("N", "q12"), ("S", "q13"), ("[EW]", "q14")],
        "q12": [(E, "q15"), ("[EW]", "q14")],
        "q13": [(E, "q15"), ("[EW]", "q14")],
        "q14": [(E, "q15")],
    },
)

AFNES = {afne.nome: afne for afne in [ER03, ER04]}
