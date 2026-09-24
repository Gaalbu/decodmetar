import unittest

from decodmetar.padroes import PADROES, valida
from tests.casos import CASOS


class TestPadroes(unittest.TestCase):
    def test_quantidade_minima_de_casos(self):
        for id_er, casos in CASOS.items():
            with self.subTest(er=id_er):
                self.assertGreaterEqual(len(casos["aceitas"]), 6)
                self.assertGreaterEqual(len(casos["rejeitadas"]), 6)
                self.assertGreaterEqual(len(casos["limite"]), 1)

    def test_limites_estao_nos_casos(self):
        for id_er, casos in CASOS.items():
            todas = set(casos["aceitas"]) | {c for c, _ in casos["rejeitadas"]}
            for cadeia in casos["limite"]:
                with self.subTest(er=id_er, cadeia=cadeia):
                    self.assertIn(cadeia, todas)

    def test_todo_padrao_tem_casos(self):
        for id_er in PADROES:
            with self.subTest(er=id_er):
                self.assertIn(id_er, CASOS)

    def test_aceitas(self):
        for id_er, casos in CASOS.items():
            for cadeia in casos["aceitas"]:
                with self.subTest(er=id_er, cadeia=cadeia):
                    self.assertTrue(valida(id_er, cadeia))

    def test_rejeitadas(self):
        for id_er, casos in CASOS.items():
            for cadeia, motivo in casos["rejeitadas"]:
                with self.subTest(er=id_er, cadeia=cadeia, motivo=motivo):
                    self.assertFalse(valida(id_er, cadeia))


if __name__ == "__main__":
    unittest.main()
