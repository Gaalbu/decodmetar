"""Expressões Regulares do DecodMETAR: única fonte da verdade dos padrões.

Notação das fichas: D = (0 | 1 | … | 9), L = (A | B | … | Z), ␣ = espaço e ε = palavra vazia.
Na ER-05, '+' e '-' entre aspas são os símbolos literais, não o operador de fecho positivo.
"""

import re
from dataclasses import dataclass, field


@dataclass
class ExpressaoRegular:
    id: str
    nome: str
    padrao: str
    descricao: str
    formal: str = ""
    alfabeto: str = ""
    compilado: re.Pattern = field(init=False, repr=False)

    def __post_init__(self):
        self.compilado = re.compile(self.padrao)

    @property
    def rotulo(self):
        """ER03 -> ER-03, como nas fichas e nos slides."""
        return f"{self.id[:2]}-{self.id[2:]}"


PADROES = {
    er.id: er
    for er in [
        ExpressaoRegular(
            "ER01",
            "Identificação do boletim",
            r"(METAR|SPECI) (COR )?S[BDINSW][A-Z]{2}",
            "Tipo METAR ou SPECI, espaço, correção COR opcional e indicativo "
            "ICAO de aeródromo brasileiro (S + B/D/I/N/S/W + 2 letras).",
            formal="(METAR | SPECI) ␣ (COR ␣ | ε) S (B | D | I | N | S | W) L L",
            alfabeto="L ∪ {␣}",
        ),
        ExpressaoRegular(
            "ER02",
            "Data e hora da observação",
            r"(0[1-9]|[12][0-9]|3[01])([01][0-9]|2[0-3])[0-5][0-9]Z",
            "Dia 01–31, hora 00–23 e minuto 00–59, terminado em Z (UTC).",
            formal="(0 (1 | … | 9) | (1 | 2) D | 3 (0 | 1)) ((0 | 1) D | 2 (0 | 1 | 2 | 3)) "
                   "(0 | 1 | 2 | 3 | 4 | 5) D Z",
            alfabeto="D ∪ {Z}",
        ),
        ExpressaoRegular(
            "ER03",
            "Vento de superfície",
            r"(VRB|([0-2][0-9]|3[0-6])0)[0-9]{2,3}(G[0-9]{2,3})?KT",
            "Direção VRB ou 000–360 em dezenas, velocidade com 2 ou 3 dígitos, "
            "rajada opcional (G + 2 ou 3 dígitos) e unidade KT.",
            formal="(VRB | ((0 | 1 | 2) D | 3 (0 | 1 | 2 | 3 | 4 | 5 | 6)) 0) D D (D | ε) "
                   "(G D D (D | ε) | ε) K T",
            alfabeto="D ∪ {V, R, B, G, K, T}",
        ),
        ExpressaoRegular(
            "ER04",
            "Visibilidade predominante",
            r"CAVOK|[0-9]{4}(N|NE|E|SE|S|SW|W|NW)?",
            "CAVOK ou 4 dígitos (metros) com direção cardeal/colateral opcional.",
            formal="CAVOK | D D D D (N | NE | E | SE | S | SW | W | NW | ε)",
            alfabeto="D ∪ {C, A, V, O, K, N, E, S, W}",
        ),
        ExpressaoRegular(
            "ER05",
            "Tempo presente",
            r"(-|\+|VC)?((MI|BC|PR|DR|BL|SH|TS|FZ)(DZ|RA|SN|SG|PL|GR|GS|BR|FG|FU|HZ|DU|SA)*|(DZ|RA|SN|SG|PL|GR|GS|BR|FG|FU|HZ|DU|SA)+)",
            "Intensidade opcional (-, + ou VC) seguida de um descritor com zero ou "
            "mais fenômenos, ou de um ou mais fenômenos.",
            formal="('-' | '+' | VC | ε) (Desc Fen* | Fen Fen*), com "
                   "Desc = (MI | BC | PR | DR | BL | SH | TS | FZ) e "
                   "Fen = (DZ | RA | SN | SG | PL | GR | GS | BR | FG | FU | HZ | DU | SA)",
            alfabeto="{-, +, A, B, C, D, F, G, H, I, L, M, N, P, R, S, T, U, V, Z}",
        ),
        ExpressaoRegular(
            "ER06",
            "Camada de nuvens",
            r"(FEW|SCT|BKN|OVC)[0-9]{3}(CB|TCU)?|VV[0-9]{3}|NSC|NCD",
            "Quantidade (FEW/SCT/BKN/OVC) + altura em centenas de pés + tipo "
            "opcional (CB/TCU); ou VV + 3 dígitos; ou NSC; ou NCD.",
            formal="(FEW | SCT | BKN | OVC) D D D (CB | TCU | ε) | VV D D D | NSC | NCD",
            alfabeto="D ∪ {B, C, D, E, F, K, N, O, S, T, U, V, W}",
        ),
        ExpressaoRegular(
            "ER07",
            "Temperatura e ponto de orvalho",
            r"M?[0-9]{2}/M?[0-9]{2}",
            "Dois dígitos com M opcional (negativo), barra, dois dígitos com M opcional.",
            formal="(M | ε) D D / (M | ε) D D",
            alfabeto="D ∪ {M, /}",
        ),
        ExpressaoRegular(
            "ER08",
            "Pressão QNH",
            r"Q(09[0-9]{2}|10[0-9]{2})",
            "Q seguido da pressão em hPa, de 0900 a 1099.",
            formal="Q (0 9 D D | 1 0 D D)",
            alfabeto="D ∪ {Q}",
        ),
    ]
}


def valida(id_er, cadeia):
    """Retorna True se a cadeia inteira pertence à linguagem da ER."""
    return PADROES[id_er].compilado.fullmatch(cadeia) is not None


def normalizar_id(texto):
    """Aceita '3', '03', 'ER3', 'ER03' ou 'ER-03' e devolve 'ER03' (ou None)."""
    texto = texto.strip().upper().replace("-", "").replace(" ", "")
    if texto.startswith("ER"):
        texto = texto[2:]
    if not texto.isdigit():
        return None
    id_er = f"ER{int(texto):02d}"
    return id_er if id_er in PADROES else None
