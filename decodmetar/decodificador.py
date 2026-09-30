"""Decodificação de um boletim METAR/SPECI usando as ERs de `padroes.py`.

Fluxo: limpa a linha, separa os grupos por espaço, valida o cabeçalho (ER-01) e
depois encaixa cada grupo na próxima posição esperada (ER-02 a ER-08). Os valores
são extraídos fatiando o grupo já validado, sem nenhuma ER extra.
"""

import math
from dataclasses import dataclass, field
from pathlib import Path

from decodmetar import mensagens as msg
from decodmetar.padroes import PADROES, valida


@dataclass
class Posicao:
    id_er: str
    nome: str
    minimo: int
    maximo: int


# Ordem dos grupos depois do cabeçalho. Tempo presente e nuvens podem se repetir.
ORDEM = [
    Posicao("ER02", "data e hora", 1, 1),
    Posicao("ER03", "vento", 1, 1),
    Posicao("ER04", "visibilidade", 1, 1),
    Posicao("ER05", "tempo presente", 0, 3),
    Posicao("ER06", "nuvens", 0, 4),
    Posicao("ER07", "temperatura/orvalho", 1, 1),
    Posicao("ER08", "pressão", 1, 1),
]


@dataclass
class Grupo:
    token: str
    id_er: str
    traducao: str


@dataclass
class Resultado:
    entrada: str
    grupos: list = field(default_factory=list)
    campos: dict = field(default_factory=dict)
    erros: list = field(default_factory=list)
    avisos: list = field(default_factory=list)
    ignorados: list = field(default_factory=list)

    @property
    def valido(self):
        return bool(self.grupos) and not self.erros

    @property
    def traducao(self):
        return [g.traducao for g in self.grupos]


class ErroArquivo(Exception):
    """Arquivo de boletins que não pode ser lido; a mensagem já é para o usuário."""


def nome_er(id_er):
    er = PADROES[id_er]
    return f"{er.nome[0].lower()}{er.nome[1:]} ({er.rotulo})"


# ---------------------------------------------------------------- decodificação


def decodificar(linha):
    """Valida e traduz um boletim. Nunca lança exceção por causa da entrada."""
    resultado = Resultado(entrada=linha if isinstance(linha, str) else "")
    texto = resultado.entrada.strip().rstrip("=").strip()
    if not texto:
        resultado.erros.append(msg.ENTRADA_VAZIA)
        return resultado

    tokens = texto.split()
    tamanho = 3 if len(tokens) > 1 and tokens[1] == "COR" else 2
    cabecalho, resto = tokens[:tamanho], tokens[tamanho:]
    if not _cabecalho(cabecalho, resultado):
        return resultado
    _corpo(resto, resultado)
    return resultado


def _cabecalho(tokens, resultado):
    cadeia = " ".join(tokens)
    if not valida("ER01", cadeia):
        motivo = diagnosticar_cabecalho(tokens)
        resultado.erros.append(f"Cabeçalho '{cadeia}' inválido: {motivo}.")
        return False
    resultado.grupos.append(Grupo(cadeia, "ER01", traduzir_cabecalho(tokens, resultado)))
    return True


def _corpo(tokens, resultado):
    maximos = {p.id_er: p.maximo for p in ORDEM}
    contagem = {p.id_er: 0 for p in ORDEM}
    ids = [p.id_er for p in ORDEM]
    atual = 0

    for i, token in enumerate(tokens):
        if token in msg.IGNORADOS_ATE_O_FIM:
            resultado.ignorados.append(" ".join(tokens[i:]))
            break
        if token in msg.IGNORADOS_SOZINHOS:
            resultado.ignorados.append(token)
            continue

        casam = [j for j, id_er in enumerate(ids) if valida(id_er, token)]
        livres = [j for j in casam if j >= atual and contagem[ids[j]] < maximos[ids[j]]]
        if livres:
            atual = livres[0]
            id_er = ids[atual]
            contagem[id_er] += 1
            resultado.grupos.append(Grupo(token, id_er, TRADUTORES[id_er](token, resultado)))
            if token == "CAVOK":
                maximos["ER05"] = maximos["ER06"] = 0
            continue

        if casam:
            resultado.erros.append(_mensagem_posicao(token, ids[casam[0]], ids[atual], maximos, contagem))
            continue

        palpite = adivinhar(token)
        if palpite is None:
            proximas = [j for j in range(atual, len(ids)) if contagem[ids[j]] < maximos[ids[j]]]
            esperado = nome_er(ids[proximas[0]]) if proximas else "o fim do boletim"
            resultado.erros.append(
                f"Grupo '{token}' não reconhecido: não corresponde a nenhuma ER "
                f"(nesta posição era esperado {esperado})."
            )
            continue
        resultado.erros.append(
            f"Grupo '{token}' parece ser {nome_er(palpite)}, mas é inválido: "
            f"{diagnosticar(palpite, token)}."
        )
        j = ids.index(palpite)
        if j >= atual:
            atual = j
            contagem[palpite] += 1

    faltando = [nome_er(p.id_er) for p in ORDEM if contagem[p.id_er] < p.minimo]
    if faltando:
        resultado.erros.append("Faltam grupos obrigatórios: " + ", ".join(faltando) + ".")


def _mensagem_posicao(token, id_er, id_atual, maximos, contagem):
    if id_er in ("ER05", "ER06") and maximos[id_er] == 0:
        return (f"Grupo '{token}', de {nome_er(id_er)}, não pode aparecer depois de CAVOK, "
                "que já indica tempo bom e ausência de nuvens significativas.")
    if contagem[id_er] >= maximos[id_er]:
        return (f"Grupo '{token}' repetido: o boletim aceita no máximo {maximos[id_er]} "
                f"grupo(s) de {nome_er(id_er)}.")
    return (f"Grupo '{token}' é de {nome_er(id_er)}, mas está fora de ordem: deve vir "
            f"antes de {nome_er(id_atual)}.")


def adivinhar(token):
    """Qual ER o grupo tentou seguir, pela aparência (só métodos de string)."""
    t = token.upper()
    if t.endswith(("KT", "MPS")):
        return "ER03"
    if "/" in t:
        return "ER07"
    if t.startswith(("Q", "A")) and t[1:].strip().isdigit():
        return "ER08"
    if t.endswith("Z") and t[:-1].isdigit() or t.isdigit() and len(t) >= 6:
        return "ER02"
    if t.isdigit() or t.startswith(("CAVOK", "KM")) or t[:4].isdigit():
        return "ER04"
    if t.startswith(("FEW", "SCT", "BKN", "OVC", "VV", "NSC", "NCD", "SKC", "CLR")):
        return "ER06"
    sem_intensidade = t.lstrip("+-")
    if sem_intensidade[:2] in msg.DESCRITORES or sem_intensidade[:2] in msg.FENOMENOS \
            or sem_intensidade.startswith("VC") or t in ("+", "-"):
        return "ER05"
    return None


# ------------------------------------------------------------------ diagnóstico


def diagnosticar_cabecalho(tokens):
    tipo = tokens[0]
    if tipo != tipo.upper() and valida("ER01", " ".join(tokens).upper()):
        return msg.DICA_MAIUSCULAS
    if tipo == "TAF":
        return "TAF é previsão de aeródromo e está fora do escopo; use METAR ou SPECI"
    if tipo not in msg.TIPOS:
        if tipo.upper().startswith(("METAR", "SPECI")) and len(tipo) > 5:
            return "falta o espaço entre o tipo do boletim e o aeródromo"
        return f"o boletim deve começar com METAR ou SPECI, e não com '{tipo}'"
    if len(tokens) < 2 or tokens[-1] == "COR":
        return "falta o indicativo ICAO do aeródromo (4 letras, ex.: SBBE)"
    estacao = tokens[-1]
    if estacao != estacao.upper():
        return msg.DICA_MAIUSCULAS
    if len(estacao) != 4:
        return f"o indicativo '{estacao}' tem {len(estacao)} caracteres; deve ter 4 letras"
    if not (estacao.isascii() and estacao.isalpha()):
        return f"o indicativo '{estacao}' deve ter só letras de A a Z"
    if estacao[0] != "S" or estacao[1] not in "BDINSW":
        return (f"'{estacao}' não é aeródromo brasileiro: os indicativos do Brasil "
                "começam com SB, SD, SI, SN, SS ou SW")
    return f"não pertence à linguagem da ER-01 ({PADROES['ER01'].padrao})"


def diagnosticar(id_er, token):
    """Motivo, em português, de o grupo não pertencer à linguagem da ER."""
    if token != token.upper() and valida(id_er, token.upper()):
        return msg.DICA_MAIUSCULAS
    motivo = DIAGNOSTICOS[id_er](token.upper())
    return motivo or f"não pertence à linguagem da {PADROES[id_er].rotulo} ({PADROES[id_er].padrao})"


def _diag_data(t):
    if not t.endswith("Z"):
        return "falta o Z no final (o horário do METAR é sempre UTC)"
    numeros = t[:-1]
    if not numeros.isdigit() or len(numeros) != 6:
        return f"antes do Z deve haver 6 algarismos (DDHHMM), e há '{numeros}'"
    dia, hora, minuto = int(numeros[:2]), int(numeros[2:4]), int(numeros[4:])
    if not 1 <= dia <= 31:
        return f"dia {dia:02d} não existe (deve estar entre 01 e 31)"
    if hora > 23:
        return f"hora {hora:02d} fora da faixa 00 a 23"
    if minuto > 59:
        return f"minuto {minuto:02d} fora da faixa 00 a 59"
    return None


def _diag_vento(t):
    if t.endswith("MPS"):
        return "a unidade MPS (metros por segundo) não é usada no Brasil; use KT (nós)"
    if not t.endswith("KT"):
        return "falta a unidade KT (nós) no final"
    corpo = t[:-2]
    direcao, resto = corpo[:3], corpo[3:]
    if direcao != "VRB":
        if not direcao.isdigit() or len(direcao) < 3:
            return "a direção deve ter 3 algarismos (000 a 360) ou ser VRB (variável)"
        graus = int(direcao)
        if graus > 360:
            return f"direção {graus}° acima de 360°"
        if graus % 10:
            return f"direção {graus}° não é múltipla de 10 (o METAR usa dezenas de graus)"
    velocidade, tem_rajada, rajada = resto.partition("G")
    if not velocidade.isdigit() or len(velocidade) not in (2, 3):
        return "a velocidade deve ter 2 ou 3 algarismos (ex.: 09010KT)"
    if tem_rajada and (not rajada.isdigit() or len(rajada) not in (2, 3)):
        return "a rajada (depois do G) deve ter 2 ou 3 algarismos (ex.: 36015G25KT)"
    return None


def _diag_visibilidade(t):
    if t.startswith("CAVOK"):
        return "CAVOK deve aparecer sozinho, sem outros símbolos"
    numeros = ""
    for c in t:
        if not c.isdigit():
            break
        numeros += c
    if len(numeros) != 4:
        return ("a visibilidade deve ter 4 algarismos, em metros (ex.: 0800, 9999 = 10 km "
                "ou mais), ou ser CAVOK")
    direcao = t[4:]
    if direcao not in msg.PONTOS_CARDEAIS:
        return f"'{direcao}' não é direção válida (use N, NE, E, SE, S, SW, W ou NW)"
    return None


def _diag_tempo(t):
    resto = t
    if resto[:1] in "+-" and resto:
        resto = resto[1:]
    elif resto.startswith("VC"):
        resto = resto[2:]
    if resto[:1] in ("+", "-") or resto.startswith("VC"):
        return "há mais de uma indicação de intensidade ou proximidade (-, + ou VC)"
    if not resto:
        return "falta o fenômeno depois da intensidade"
    if len(resto) % 2:
        return "os códigos de tempo presente têm 2 letras cada (ex.: RA, TS, BR)"
    pares = [resto[i:i + 2] for i in range(0, len(resto), 2)]
    desconhecidos = [p for p in pares if p not in msg.DESCRITORES and p not in msg.FENOMENOS]
    if desconhecidos:
        return "código(s) desconhecido(s): " + ", ".join(desconhecidos)
    if any(p in msg.DESCRITORES for p in pares[1:]):
        return "só pode haver um descritor (TS, SH, FZ…), e ele vem antes dos fenômenos"
    return None


def _diag_nuvens(t):
    if t.startswith(("SKC", "CLR")):
        return f"'{t[:3]}' não é usado no Brasil; para céu sem nuvens use NSC ou NCD"
    prefixo = "VV" if t.startswith("VV") else t[:3]
    if prefixo not in msg.QUANTIDADES and prefixo != "VV":
        return "a quantidade deve ser FEW, SCT, BKN ou OVC (ou VV, NSC, NCD)"
    resto = t[len(prefixo):]
    altura = ""
    for c in resto:
        if not c.isdigit():
            break
        altura += c
    if len(altura) != 3:
        return "a altura deve ter 3 algarismos, em centenas de pés (ex.: 020 = 2.000 pés)"
    tipo = resto[3:]
    if prefixo == "VV" and tipo:
        return "o grupo VV (céu obscurecido) não leva tipo de nuvem"
    if tipo not in msg.TIPOS_NUVEM:
        return f"'{tipo}' não é tipo de nuvem (use CB ou TCU)"
    return None


def _diag_temperatura(t):
    if t.count("/") != 1:
        return "use uma única barra entre temperatura e ponto de orvalho (ex.: 30/24)"
    for parte, nome in zip(t.split("/"), ("temperatura", "ponto de orvalho")):
        valor = parte[1:] if parte.startswith("M") else parte
        if not valor.isdigit() or len(valor) != 2:
            return (f"{nome} '{parte}' deve ter 2 algarismos, com M na frente se for "
                    "negativa (ex.: 05, M05)")
    return None


def _diag_pressao(t):
    if t.startswith("A"):
        return "pressão em polegadas de mercúrio (A) não é usada no Brasil; use Q + hPa"
    if not t.startswith("Q"):
        return "falta o Q antes do valor da pressão"
    valor = t[1:]
    if not valor.isdigit() or len(valor) != 4:
        return "depois do Q devem vir 4 algarismos (ex.: Q1013)"
    return f"pressão {int(valor)} hPa fora da faixa aceita (0900 a 1099 hPa)"


DIAGNOSTICOS = {
    "ER02": _diag_data,
    "ER03": _diag_vento,
    "ER04": _diag_visibilidade,
    "ER05": _diag_tempo,
    "ER06": _diag_nuvens,
    "ER07": _diag_temperatura,
    "ER08": _diag_pressao,
}


# -------------------------------------------------------------------- tradução


def traduzir_cabecalho(tokens, resultado):
    tipo, estacao = tokens[0], tokens[-1]
    corrigido = len(tokens) == 3
    resultado.campos.update(tipo=tipo, corrigido=corrigido, aerodromo=estacao)
    local = msg.AERODROMOS.get(estacao, "indicativo não cadastrado no programa")
    texto = f"{msg.TIPOS[tipo]} do aeródromo {estacao}, {local}"
    return texto + (". Boletim corrigido (COR)" if corrigido else "")


def traduzir_data(token, resultado):
    dia, hora, minuto = int(token[:2]), int(token[2:4]), int(token[4:6])
    resultado.campos.update(dia=dia, hora=hora, minuto=minuto)
    local = (hora - 3) % 24
    vespera = " do dia anterior" if hora < 3 else ""
    return (f"Observação do dia {dia:02d} às {hora:02d}:{minuto:02d} UTC "
            f"({local:02d}:{minuto:02d}{vespera} no horário de Brasília)")


def _kmh(nos):
    return round(nos * 1.852)


def traduzir_vento(token, resultado):
    corpo = token[:-2]
    direcao, (velocidade, _, rajada) = corpo[:3], corpo[3:].partition("G")
    vel = int(velocidade)
    raj = int(rajada) if rajada else None
    resultado.campos.update(vento_direcao=direcao, vento_velocidade=vel, vento_rajada=raj)
    if direcao == "000" and vel == 0 and raj is None:
        return "Vento calmo (calmaria)"
    if direcao == "VRB":
        texto = f"Vento de direção variável a {vel} nós ({_kmh(vel)} km/h)"
    else:
        graus = int(direcao)
        texto = (f"Vento de {graus:03d}° (vindo do {msg.ponto_cardeal(graus)}) a {vel} nós "
                 f"({_kmh(vel)} km/h)")
        if graus == 0:
            resultado.avisos.append("Vento com direção 000° mas velocidade maior que zero: "
                                    "000 só é usado para calmaria.")
    if raj is not None:
        texto += f", com rajadas de {raj} nós ({_kmh(raj)} km/h)"
        if raj <= vel:
            resultado.avisos.append(f"A rajada ({raj} kt) deveria ser maior que a "
                                    f"velocidade média ({vel} kt).")
    return texto


def traduzir_visibilidade(token, resultado):
    if token == "CAVOK":
        resultado.campos["visibilidade_m"] = 10000
        return ("CAVOK: visibilidade de 10 km ou mais, sem nuvens abaixo de 5.000 pés, "
                "sem CB/TCU e sem tempo significativo")
    metros, direcao = int(token[:4]), token[4:]
    resultado.campos["visibilidade_m"] = metros
    texto = ("Visibilidade de 10 km ou mais" if metros == 9999
             else f"Visibilidade de {msg.milhar(metros)} m")
    if direcao:
        texto += f" (mínima na direção {msg.PONTOS_CARDEAIS[direcao]})"
    return texto


def traduzir_tempo(token, resultado):
    intensidade, resto = "", token
    for prefixo in ("-", "+", "VC"):
        if token.startswith(prefixo):
            intensidade, resto = prefixo, token[len(prefixo):]
            break
    pares = [resto[i:i + 2] for i in range(0, len(resto), 2)]
    descritor = pares[0] if pares[0] in msg.DESCRITORES else ""
    fenomenos = [msg.FENOMENOS[p] for p in pares if p in msg.FENOMENOS]
    lista = " e ".join(fenomenos)
    if descritor == "TS":
        texto = "trovoada" + (f" com {lista}" if lista else "")
    elif descritor == "SH":
        texto = "pancadas" + (f" de {lista}" if lista else "")
    elif descritor:
        texto = f"{lista} {msg.DESCRITORES[descritor]}" if lista else msg.DESCRITORES[descritor]
    else:
        texto = lista
    if intensidade == "VC":
        texto += " nas vizinhanças do aeródromo"
    elif intensidade:
        texto += f" (intensidade {msg.INTENSIDADES[intensidade]})"
    resultado.campos.setdefault("tempo_presente", []).append(token)
    return "Tempo presente: " + texto


def traduzir_nuvens(token, resultado):
    resultado.campos.setdefault("nuvens", []).append(token)
    if token == "NSC":
        return "Nenhuma nuvem significativa (NSC)"
    if token == "NCD":
        return "Nenhuma nuvem detectada pela estação automática (NCD)"
    if token.startswith("VV"):
        pes = int(token[2:]) * 100
        return f"Céu obscurecido; visibilidade vertical de {msg.milhar(pes)} pés"
    quantidade, altura, tipo = token[:3], int(token[3:6]) * 100, token[6:]
    onde = ("junto ao solo (menos de 100 pés)" if altura == 0
            else f"a {msg.milhar(altura)} pés ({msg.milhar(round(altura * 0.3048))} m)")
    texto = f"{msg.QUANTIDADES[quantidade]} {onde}"
    if tipo:
        texto += f", do tipo {msg.TIPOS_NUVEM[tipo]}"
    return texto


def _celsius(parte):
    return -int(parte[1:]) if parte.startswith("M") else int(parte)


def _umidade(temperatura, orvalho):
    """Umidade relativa pela fórmula de Magnus."""
    def pressao_vapor(t):
        return 6.112 * math.exp(17.62 * t / (243.12 + t))
    return round(100 * pressao_vapor(orvalho) / pressao_vapor(temperatura))


def traduzir_temperatura(token, resultado):
    temp, orv = (_celsius(p) for p in token.split("/"))
    resultado.campos.update(temperatura=temp, orvalho=orv)
    texto = f"Temperatura de {temp} °C e ponto de orvalho de {orv} °C"
    if orv > temp:
        resultado.avisos.append(f"Ponto de orvalho ({orv} °C) maior que a temperatura "
                                f"({temp} °C): fisicamente impossível, confira o boletim.")
    else:
        texto += f" (umidade relativa de cerca de {_umidade(temp, orv)}%)"
    return texto


def traduzir_pressao(token, resultado):
    hpa = int(token[1:])
    resultado.campos["pressao_hpa"] = hpa
    return f"Pressão ajustada ao nível do mar (QNH) de {msg.milhar(hpa)} hPa"


TRADUTORES = {
    "ER02": traduzir_data,
    "ER03": traduzir_vento,
    "ER04": traduzir_visibilidade,
    "ER05": traduzir_tempo,
    "ER06": traduzir_nuvens,
    "ER07": traduzir_temperatura,
    "ER08": traduzir_pressao,
}


# ------------------------------------------------------------------- arquivos


def ler_boletins(caminho):
    """Linhas não vazias do arquivo, como pares (número da linha, texto).

    Linhas em branco e comentários (começando com #) são pulados.
    Lança ErroArquivo com mensagem clara se o arquivo não puder ser usado.
    """
    caminho = Path(str(caminho).strip().strip('"'))
    if not str(caminho).strip() or str(caminho) == ".":
        raise ErroArquivo("Nenhum caminho informado.")
    if not caminho.exists():
        raise ErroArquivo(f"Arquivo '{caminho}' não encontrado.")
    if caminho.is_dir():
        raise ErroArquivo(f"'{caminho}' é uma pasta, não um arquivo.")
    try:
        conteudo = caminho.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise ErroArquivo(f"'{caminho}' não é um arquivo de texto UTF-8.") from None
    except OSError as erro:
        raise ErroArquivo(f"Não foi possível ler '{caminho}': {erro.strerror}.") from None
    linhas = [
        (numero, linha.strip())
        for numero, linha in enumerate(conteudo.splitlines(), start=1)
        if linha.strip() and not linha.lstrip().startswith("#")
    ]
    if not linhas:
        raise ErroArquivo(f"'{caminho}' está vazio (nenhum boletim encontrado).")
    return linhas


def processar_arquivo(caminho):
    """Decodifica cada boletim do arquivo: lista de (número da linha, Resultado)."""
    return [(numero, decodificar(linha)) for numero, linha in ler_boletins(caminho)]
