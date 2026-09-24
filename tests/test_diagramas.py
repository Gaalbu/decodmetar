import tempfile
import unittest
from pathlib import Path

from decodmetar.afne.definicoes import AFNES
from decodmetar.afne.diagramas import PASTA_PADRAO, documento, gerar, graphviz, mermaid


class TestDiagramas(unittest.TestCase):
    def test_mermaid_tem_inicial_finais_e_epsilon(self):
        afne = AFNES["ER04"]
        texto = mermaid(afne)
        self.assertIn("--> q0", texto)
        self.assertIn('q15((("q15")))', texto)
        self.assertIn('q0 -.->|"ε"| q1', texto)

    def test_graphviz_marca_finais(self):
        texto = graphviz(AFNES["ER03"])
        self.assertIn("q18 [shape=doublecircle];", texto)
        self.assertIn('q10 -> q11 [label="[0-9]"];', texto)
        self.assertIn('q10 -> q11 [label="ε", style=dashed];', texto)

    def test_toda_transicao_aparece_no_diagrama(self):
        for id_er, afne in AFNES.items():
            texto = graphviz(afne)
            for origem, lista in afne.transicoes.items():
                for _, destino in lista:
                    with self.subTest(er=id_er, aresta=(origem, destino)):
                        self.assertIn(f"{origem} -> {destino} ", texto)

    def test_gerar_escreve_arquivos(self):
        with tempfile.TemporaryDirectory() as pasta:
            gerados = gerar(pasta)
            self.assertEqual(len(gerados), 2 * len(AFNES))
            self.assertTrue(all(p.read_text(encoding="utf-8") for p in gerados))

    def test_docs_versionados_estao_atualizados(self):
        for id_er, afne in AFNES.items():
            caminho = PASTA_PADRAO / f"{id_er}.md"
            with self.subTest(er=id_er):
                self.assertTrue(caminho.exists(), f"rode python -m decodmetar.afne.diagramas")
                self.assertEqual(caminho.read_text(encoding="utf-8"), documento(afne),
                                 "diagrama desatualizado: rode python -m decodmetar.afne.diagramas")


if __name__ == "__main__":
    unittest.main()
