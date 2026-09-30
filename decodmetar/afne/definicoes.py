"""AFNε de cada ER, construídos à mão no estilo de Thompson compacto.

ε aparece onde a ER tem escolha: fim dos ramos de uma união, opcional (r? = r|ε)
e repetição limitada (r{2,3} = rr(r|ε)).
"""

from decodmetar.afne.automato import EPSILON as E
from decodmetar.afne.automato import AFNe


def _numerados(n):
    return [f"q{i}" for i in range(n)]


# ER-01: (METAR|SPECI) (COR )?S[BDINSW][A-Z]{2}
ER01 = AFNe(
    "ER01",
    _numerados(22),
    "q0",
    {"q21"},
    {
        # tipo: METAR
        "q0": [("M", "q1"), ("S", "q6")],
        "q1": [("E", "q2")],
        "q2": [("T", "q3")],
        "q3": [("A", "q4")],
        "q4": [("R", "q5")],
        "q5": [(E, "q11")],
        # tipo: SPECI
        "q6": [("P", "q7")],
        "q7": [("E", "q8")],
        "q8": [("C", "q9")],
        "q9": [("I", "q10")],
        "q10": [(E, "q11")],
        # espaço obrigatório
        "q11": [(" ", "q12")],
        # correção opcional: (COR )?
        "q12": [("C", "q13"), (E, "q17")],
        "q13": [("O", "q14")],
        "q14": [("R", "q15")],
        "q15": [(" ", "q16")],
        "q16": [(E, "q17")],
        # indicativo ICAO brasileiro
        "q17": [("S", "q18")],
        "q18": [("[BDINSW]", "q19")],
        "q19": [("[A-Z]", "q20")],
        "q20": [("[A-Z]", "q21")],
    },
)

# ER-02: (0[1-9]|[12][0-9]|3[01])([01][0-9]|2[0-3])[0-5][0-9]Z
ER02 = AFNe(
    "ER02",
    _numerados(16),
    "q0",
    {"q15"},
    {
        # dia: 01–09, 10–29 ou 30–31
        "q0": [("0", "q1"), ("[12]", "q3"), ("3", "q5")],
        "q1": [("[1-9]", "q2")],
        "q2": [(E, "q7")],
        "q3": [("[0-9]", "q4")],
        "q4": [(E, "q7")],
        "q5": [("[01]", "q6")],
        "q6": [(E, "q7")],
        # hora: 00–19 ou 20–23
        "q7": [("[01]", "q8"), ("2", "q10")],
        "q8": [("[0-9]", "q9")],
        "q9": [(E, "q12")],
        "q10": [("[0-3]", "q11")],
        "q11": [(E, "q12")],
        # minuto: 00–59
        "q12": [("[0-5]", "q13")],
        "q13": [("[0-9]", "q14")],
        # UTC
        "q14": [("Z", "q15")],
    },
)

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

# ER-05: (-|\+|VC)?((MI|BC|PR|DR|BL|SH|TS|FZ)(DZ|RA|...|SA)*|(DZ|RA|...|SA)+)
# Usa a identidade Desc Fen* | Fen Fen* = (Desc | Fen) Fen*: os dois ramos da
# união terminam em q22 e o laço q22 -ε-> q12 dá o Fen* dos dois.
ER05 = AFNe(
    "ER05",
    _numerados(23),
    "q0",
    {"q22"},
    {
        # intensidade/proximidade opcional: - , + , VC ou ε
        "q0": [("-", "q2"), ("+", "q2"), ("V", "q1"), (E, "q3")],
        "q1": [("C", "q2")],
        "q2": [(E, "q3")],
        # união: descritor ou fenômeno
        "q3": [(E, "q4"), (E, "q12")],
        # descritor: MI, BC, BL, PR, DR, SH, TS, FZ
        "q4": [("M", "q5"), ("B", "q6"), ("[PD]", "q7"), ("S", "q8"), ("T", "q9"), ("F", "q10")],
        "q5": [("I", "q11")],
        "q6": [("[CL]", "q11")],
        "q7": [("R", "q11")],
        "q8": [("H", "q11")],
        "q9": [("S", "q11")],
        "q10": [("Z", "q11")],
        "q11": [(E, "q22")],
        # fenômeno: DZ, DU, RA, SN, SG, SA, PL, GR, GS, BR, FG, FU, HZ
        "q12": [
            ("D", "q13"), ("R", "q14"), ("S", "q15"), ("P", "q16"),
            ("G", "q17"), ("B", "q18"), ("F", "q19"), ("H", "q20"),
        ],
        "q13": [("[ZU]", "q21")],
        "q14": [("A", "q21")],
        "q15": [("[NGA]", "q21")],
        "q16": [("L", "q21")],
        "q17": [("[RS]", "q21")],
        "q18": [("R", "q21")],
        "q19": [("[GU]", "q21")],
        "q20": [("Z", "q21")],
        "q21": [(E, "q22")],
        # fecho: mais fenômenos
        "q22": [(E, "q12")],
    },
)

# ER-06: (FEW|SCT|BKN|OVC)[0-9]{3}(CB|TCU)?|VV[0-9]{3}|NSC|NCD
ER06 = AFNe(
    "ER06",
    _numerados(30),
    "q0",
    {"q29"},
    {
        # união de topo: camada, céu obscurecido, NSC ou NCD
        "q0": [(E, "q1"), (E, "q18"), (E, "q24")],
        # quantidade: FEW, SCT, BKN, OVC
        "q1": [("F", "q2"), ("S", "q4"), ("B", "q6"), ("O", "q8")],
        "q2": [("E", "q3")],
        "q3": [("W", "q10")],
        "q4": [("C", "q5")],
        "q5": [("T", "q10")],
        "q6": [("K", "q7")],
        "q7": [("N", "q10")],
        "q8": [("V", "q9")],
        "q9": [("C", "q10")],
        # altura: [0-9]{3}
        "q10": [("[0-9]", "q11")],
        "q11": [("[0-9]", "q12")],
        "q12": [("[0-9]", "q13")],
        # tipo opcional: CB, TCU ou ε
        "q13": [("C", "q14"), ("T", "q15"), (E, "q17")],
        "q14": [("B", "q17")],
        "q15": [("C", "q16")],
        "q16": [("U", "q17")],
        "q17": [(E, "q29")],
        # céu obscurecido: VV[0-9]{3}
        "q18": [("V", "q19")],
        "q19": [("V", "q20")],
        "q20": [("[0-9]", "q21")],
        "q21": [("[0-9]", "q22")],
        "q22": [("[0-9]", "q23")],
        "q23": [(E, "q29")],
        # NSC ou NCD (prefixo N compartilhado)
        "q24": [("N", "q25")],
        "q25": [("S", "q26"), ("C", "q27")],
        "q26": [("C", "q28")],
        "q27": [("D", "q28")],
        "q28": [(E, "q29")],
    },
)

# ER-07: M?[0-9]{2}/M?[0-9]{2}
ER07 = AFNe(
    "ER07",
    _numerados(8),
    "q0",
    {"q7"},
    {
        # temperatura: M opcional e 2 dígitos
        "q0": [("M", "q1"), (E, "q1")],
        "q1": [("[0-9]", "q2")],
        "q2": [("[0-9]", "q3")],
        "q3": [("/", "q4")],
        # ponto de orvalho: M opcional e 2 dígitos
        "q4": [("M", "q5"), (E, "q5")],
        "q5": [("[0-9]", "q6")],
        "q6": [("[0-9]", "q7")],
    },
)

# ER-08: Q(09[0-9]{2}|10[0-9]{2})
ER08 = AFNe(
    "ER08",
    _numerados(13),
    "q0",
    {"q12"},
    {
        "q0": [("Q", "q1")],
        # união: 09xx ou 10xx
        "q1": [(E, "q2"), (E, "q7")],
        # 0900–0999
        "q2": [("0", "q3")],
        "q3": [("9", "q4")],
        "q4": [("[0-9]", "q5")],
        "q5": [("[0-9]", "q6")],
        "q6": [(E, "q12")],
        # 1000–1099
        "q7": [("1", "q8")],
        "q8": [("0", "q9")],
        "q9": [("[0-9]", "q10")],
        "q10": [("[0-9]", "q11")],
        "q11": [(E, "q12")],
    },
)

AFNES = {afne.nome: afne for afne in [ER01, ER02, ER03, ER04, ER05, ER06, ER07, ER08]}
