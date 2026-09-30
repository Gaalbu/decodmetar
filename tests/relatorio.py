"""Resumo dos testes por ER e evidência salva em docs/resultado_testes.txt.

Uso: python -m tests.relatorio
"""

import io
import platform
import random
import sys
import unittest
from datetime import datetime
from pathlib import Path

from decodmetar.afne.definicoes import AFNES
from decodmetar.padroes import PADROES, valida
from tests.casos import CASOS
from tests.test_afne import (
    CADEIAS_ALEATORIAS,
    PASSEIOS_MUTADOS,
    SEMENTE,
    cadeias_aleatorias,
    mutacoes,
    passeio_aleatorio,
)

RAIZ = Path(__file__).resolve().parents[1]
ARQUIVO = RAIZ / "docs" / "resultado_testes.txt"


def tabela_casos():
    """Uma linha por ER: quantas cadeias fixas e quantas regex e AFNε acertaram."""
    linhas = [
        f"{'ER':<6}{'aceitas':>9}{'rejeitadas':>12}{'limites':>9}{'regex ok':>10}{'AFNε ok':>9}",
    ]
    total_ok = True
    for id_er in PADROES:
        casos, afne = CASOS[id_er], AFNES[id_er]
        esperados = [(c, True) for c in casos["aceitas"]]
        esperados += [(c, False) for c, _ in casos["rejeitadas"]]
        regex_ok = sum(valida(id_er, c) == e for c, e in esperados)
        afne_ok = sum(afne.aceita(c) == e for c, e in esperados)
        total_ok &= regex_ok == afne_ok == len(esperados)
        linhas.append(
            f"{PADROES[id_er].rotulo:<6}{len(casos['aceitas']):>9}{len(casos['rejeitadas']):>12}"
            f"{len(casos['limite']):>9}{f'{regex_ok}/{len(esperados)}':>10}"
            f"{f'{afne_ok}/{len(esperados)}':>9}"
        )
    return "\n".join(linhas), total_ok


def tabela_equivalencia():
    """Quantas cadeias distintas regex e AFNε compararam, por ER, e em quantas discordaram."""
    linhas = [f"{'ER':<6}{'cadeias comparadas':>20}{'aceitas':>10}{'divergências':>14}"]
    total_ok = True
    for id_er, afne in AFNES.items():
        rng = random.Random(f"{SEMENTE}-{id_er}")
        cadeias = set(cadeias_aleatorias(afne.alfabeto, rng, CADEIAS_ALEATORIAS))
        for aceita in CASOS[id_er]["aceitas"]:
            cadeias.update(mutacoes(aceita, afne.alfabeto))
        rng = random.Random(f"{SEMENTE}-{id_er}-passeio")
        passeios = {passeio_aleatorio(afne, rng) for _ in range(CADEIAS_ALEATORIAS)} - {None}
        cadeias |= passeios
        for aceita in rng.sample(sorted(passeios), min(PASSEIOS_MUTADOS, len(passeios))):
            cadeias.update(mutacoes(aceita, afne.alfabeto))
        divergentes = sum(afne.aceita(c) != valida(id_er, c) for c in cadeias)
        aceitas = sum(valida(id_er, c) for c in cadeias)
        total_ok &= divergentes == 0
        linhas.append(f"{PADROES[id_er].rotulo:<6}{len(cadeias):>20}{aceitas:>10}{divergentes:>14}")
    return "\n".join(linhas), total_ok


def executar_unittest(saida, verbosidade=2):
    suite = unittest.TestLoader().discover(str(RAIZ / "tests"), top_level_dir=str(RAIZ))
    return unittest.TextTestRunner(stream=saida, verbosity=verbosidade).run(suite)


def gerar(caminho=ARQUIVO):
    casos, casos_ok = tabela_casos()
    equivalencia, equivalencia_ok = tabela_equivalencia()
    buffer = io.StringIO()
    resultado = executar_unittest(buffer)
    texto = f"""Resultado dos testes do DecodMETAR
Gerado por: python -m tests.relatorio
Data: {datetime.now():%d/%m/%Y %H:%M}
Python {platform.python_version()} em {platform.system()} {platform.release()}

1. Casos fixos de cada ficha (tests/casos.py)
   Cada cadeia passa pelo re.fullmatch e pelo simulador do AFNε.

{casos}

   Situação: {"todas as cadeias com o resultado esperado" if casos_ok else "HÁ FALHAS"}

2. Equivalência regex x AFNε em cadeias geradas (semente {SEMENTE})
   Aleatórias sobre o alfabeto + mutações a 1 edição + passeios pelo AFNε.

{equivalencia}

   Situação: {"nenhuma divergência" if equivalencia_ok else "HÁ DIVERGÊNCIAS"}

3. Saída completa do unittest (python -m unittest discover -s tests -v)

{buffer.getvalue()}"""
    Path(caminho).write_text(texto, encoding="utf-8")
    return resultado.wasSuccessful() and casos_ok and equivalencia_ok, texto


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ok, _ = gerar()
    print(f"gerado: {ARQUIVO}")
    print("tudo certo" if ok else "ATENÇÃO: há falhas, veja o arquivo")
    sys.exit(0 if ok else 1)
