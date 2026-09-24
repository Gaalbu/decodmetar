"""Equivalência entre cada padrão do código e o seu AFNε."""

import random
import unittest

from decodmetar.afne.automato import EPSILON, expandir_rotulo
from decodmetar.afne.definicoes import AFNES
from decodmetar.padroes import PADROES, valida
from tests.casos import CASOS

SEMENTE = 2026
CADEIAS_ALEATORIAS = 2000
PASSEIOS_MUTADOS = 200
SIMBOLOS_ESTRANHOS = ["x", " ", "-", "/"]


def cadeias_aleatorias(alfabeto, rng, quantidade):
    simbolos = sorted(alfabeto) + SIMBOLOS_ESTRANHOS
    for _ in range(quantidade):
        yield "".join(rng.choice(simbolos) for _ in range(rng.randint(0, 12)))


def passeio_aleatorio(afne, rng, limite=40):
    """Cadeia gerada andando ao acaso pelo AFNε até parar num estado final."""
    estado, cadeia = afne.inicial, []
    for _ in range(limite):
        saidas = afne.transicoes[estado]
        if estado in afne.finais and (not saidas or rng.random() < 0.3):
            return "".join(cadeia)
        if not saidas:
            return None
        rotulo, estado = rng.choice(saidas)
        if rotulo != EPSILON:
            cadeia.append(rng.choice(sorted(expandir_rotulo(rotulo))))
    return None


def mutacoes(cadeia, alfabeto):
    """Todas as cadeias a 1 edição (troca, remoção ou inserção) de distância."""
    simbolos = sorted(alfabeto) + SIMBOLOS_ESTRANHOS
    for i in range(len(cadeia) + 1):
        if i < len(cadeia):
            yield cadeia[:i] + cadeia[i + 1:]
            for s in simbolos:
                yield cadeia[:i] + s + cadeia[i + 1:]
        for s in simbolos:
            yield cadeia[:i] + s + cadeia[i:]


def divergencias(afne, id_er, cadeias):
    return sorted(
        repr(c) for c in set(cadeias) if afne.aceita(c) != valida(id_er, c)
    )


class TestEquivalencia(unittest.TestCase):
    def assertSemDivergencias(self, id_er, lista):
        self.assertEqual(lista, [], f"{id_er}: AFNε e regex discordam em {lista[:10]}")

    def test_todo_padrao_tem_afne(self):
        for id_er in PADROES:
            with self.subTest(er=id_er):
                self.assertIn(id_er, AFNES)

    def test_afne_nos_casos_fixos(self):
        for id_er, afne in AFNES.items():
            casos = CASOS[id_er]
            for cadeia in casos["aceitas"]:
                with self.subTest(er=id_er, cadeia=cadeia):
                    self.assertTrue(afne.aceita(cadeia))
            for cadeia, motivo in casos["rejeitadas"]:
                with self.subTest(er=id_er, cadeia=cadeia, motivo=motivo):
                    self.assertFalse(afne.aceita(cadeia))

    def test_concorda_com_regex_em_cadeias_aleatorias(self):
        for id_er, afne in AFNES.items():
            rng = random.Random(f"{SEMENTE}-{id_er}")
            cadeias = cadeias_aleatorias(afne.alfabeto, rng, CADEIAS_ALEATORIAS)
            self.assertSemDivergencias(id_er, divergencias(afne, id_er, cadeias))

    def test_concorda_com_regex_em_mutacoes_das_aceitas(self):
        for id_er, afne in AFNES.items():
            cadeias = [
                m for aceita in CASOS[id_er]["aceitas"] for m in mutacoes(aceita, afne.alfabeto)
            ]
            self.assertSemDivergencias(id_er, divergencias(afne, id_er, cadeias))

    def test_concorda_com_regex_em_passeios_pelo_afne(self):
        for id_er, afne in AFNES.items():
            rng = random.Random(f"{SEMENTE}-{id_er}-passeio")
            geradas = {passeio_aleatorio(afne, rng) for _ in range(CADEIAS_ALEATORIAS)}
            geradas.discard(None)
            self.assertGreater(len(geradas), 50, f"{id_er}: poucos passeios distintos")
            self.assertSemDivergencias(id_er, divergencias(afne, id_er, geradas))
            amostra = rng.sample(sorted(geradas), min(PASSEIOS_MUTADOS, len(geradas)))
            cadeias = [m for aceita in amostra for m in mutacoes(aceita, afne.alfabeto)]
            self.assertSemDivergencias(id_er, divergencias(afne, id_er, cadeias))


if __name__ == "__main__":
    unittest.main()
