"""Textos de saída e tabelas de tradução dos códigos METAR para o português."""

TIPOS = {
    "METAR": "METAR (observação regular, de hora em hora)",
    "SPECI": "SPECI (observação especial, emitida quando o tempo muda muito)",
}

AERODROMOS = {
    "SBBE": "Belém/Val-de-Cans (PA)",
    "SBSN": "Santarém (PA)",
    "SBMQ": "Macapá (AP)",
    "SBEG": "Manaus/Eduardo Gomes (AM)",
    "SBSL": "São Luís (MA)",
    "SBFZ": "Fortaleza (CE)",
    "SBRF": "Recife (PE)",
    "SBSV": "Salvador (BA)",
    "SBBR": "Brasília (DF)",
    "SBCF": "Belo Horizonte/Confins (MG)",
    "SBGL": "Rio de Janeiro/Galeão (RJ)",
    "SBRJ": "Rio de Janeiro/Santos Dumont (RJ)",
    "SBGR": "São Paulo/Guarulhos (SP)",
    "SBSP": "São Paulo/Congonhas (SP)",
    "SBKP": "Campinas/Viracopos (SP)",
    "SBCT": "Curitiba/Afonso Pena (PR)",
    "SBFL": "Florianópolis (SC)",
    "SBPA": "Porto Alegre/Salgado Filho (RS)",
}

PONTOS_CARDEAIS = {
    "N": "norte", "NE": "nordeste", "E": "leste", "SE": "sudeste",
    "S": "sul", "SW": "sudoeste", "W": "oeste", "NW": "noroeste",
}

INTENSIDADES = {
    "-": "fraca",
    "+": "forte",
    "VC": "nas vizinhanças do aeródromo",
    "": "moderada",
}

DESCRITORES = {
    "MI": "baixo(a)",
    "BC": "em bancos",
    "PR": "parcial",
    "DR": "flutuante",
    "BL": "soprado(a)",
    "SH": "pancadas",
    "TS": "trovoada",
    "FZ": "congelante",
}

FENOMENOS = {
    "DZ": "chuvisco",
    "RA": "chuva",
    "SN": "neve",
    "SG": "grãos de neve",
    "PL": "pelotas de gelo",
    "GR": "granizo",
    "GS": "granizo pequeno",
    "BR": "névoa úmida",
    "FG": "nevoeiro",
    "FU": "fumaça",
    "HZ": "névoa seca",
    "DU": "poeira",
    "SA": "areia",
}

QUANTIDADES = {
    "FEW": "Poucas nuvens (1 a 2 oitavos do céu)",
    "SCT": "Nuvens esparsas (3 a 4 oitavos)",
    "BKN": "Céu nublado (5 a 7 oitavos)",
    "OVC": "Céu encoberto (8 oitavos)",
}

TIPOS_NUVEM = {
    "CB": "cumulonimbus, nuvem de trovoada",
    "TCU": "cumulus congestus, nuvem de grande desenvolvimento",
}

# Grupos válidos no METAR que este programa não decodifica.
IGNORADOS_SOZINHOS = {"AUTO", "NOSIG"}
# Depois destes, o resto da linha é tendência ou observação: ignorado.
IGNORADOS_ATE_O_FIM = {"RMK", "BECMG", "TEMPO"}

ENTRADA_VAZIA = "Entrada vazia: digite um boletim METAR ou SPECI."
DICA_MAIUSCULAS = "os códigos METAR são sempre escritos em letras maiúsculas"
EXEMPLO = "METAR SBBE 241200Z 09010KT 9999 -RA FEW020 30/24 Q1011"


def ponto_cardeal(graus):
    """Nome do ponto cardeal/colateral mais próximo da direção (em graus)."""
    nomes = ["norte", "nordeste", "leste", "sudeste", "sul", "sudoeste", "oeste", "noroeste"]
    return nomes[round(graus / 45) % 8]


def milhar(numero):
    """1500 -> '1.500', no padrão brasileiro."""
    return f"{numero:,}".replace(",", ".")
