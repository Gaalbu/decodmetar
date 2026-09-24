"""Cadeias de teste por ER.

aceitas: cadeias que devem casar.
rejeitadas: pares (cadeia, motivo) que não devem casar.
limite: casos-limite, que também aparecem em aceitas ou rejeitadas.
"""

CASOS = {
    "ER03": {
        "aceitas": [
            "09010KT",
            "00000KT",
            "36015G25KT",
            "VRB03KT",
            "270105KT",
            "18012G120KT",
            "35008KT",
        ],
        "rejeitadas": [
            ("", "cadeia vazia"),
            ("37010KT", "direção 370° acima de 360"),
            ("09510KT", "direção não termina em 0 (não é dezena de graus)"),
            ("09010", "falta a unidade KT"),
            ("0901KT", "velocidade com 1 dígito"),
            ("36015G5KT", "rajada com 1 dígito"),
            ("09010MPS", "unidade MPS não prevista"),
            ("VRBKT", "falta a velocidade"),
            ("36115KT", "direção 361° não é dezena de graus"),
        ],
        "limite": ["00000KT", "36015G25KT", "270105KT", "36115KT", ""],
    },
    "ER04": {
        "aceitas": [
            "9999",
            "CAVOK",
            "0800",
            "5000NE",
            "0000",
            "3000SW",
            "1500N",
        ],
        "rejeitadas": [
            ("", "cadeia vazia"),
            ("999", "apenas 3 dígitos"),
            ("99999", "5 dígitos"),
            ("CAVOk", "letra minúscula"),
            ("5000NNE", "direção com 3 letras não prevista"),
            ("5000X", "X não é direção"),
            ("CAVOK9999", "CAVOK e valor numérico juntos"),
            ("KM10", "formato em km não previsto"),
        ],
        "limite": ["0000", "9999", "CAVOK9999", ""],
    },
}
