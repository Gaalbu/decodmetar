"""A documentação mostra exatamente o que o código faz (regra central do guia)."""

import unittest
from pathlib import Path

from decodmetar.afne.definicoes import AFNES
from decodmetar.padroes import PADROES
from tests.casos import CASOS

RAIZ = Path(__file__).resolve().parents[1]
FICHAS = RAIZ / "docs" / "EXPRESSOES_REGULARES.md"


def em_tabela(texto):
    """Como o texto aparece dentro de uma tabela Markdown (| vira \\|)."""
    return texto.replace("|", "\\|")


def secoes():
    """{'ER01': texto da ficha, ...}, separando o arquivo pelos títulos '## ER-0x'."""
    partes = FICHAS.read_text(encoding="utf-8").split("\n## ER-")[1:]
    return {"ER" + parte[:2]: parte for parte in partes}


def tracos(secao):
    """Blocos de código que começam com 'cadeia: ...': (cadeia, traço)."""
    blocos = secao.split("```")[1::2]
    for bloco in blocos:
        linhas = bloco.strip("\n").split("\n")
        if linhas[0].startswith("cadeia: "):
            yield linhas[0][len("cadeia: "):], "\n".join(linhas[1:])


class TestFichas(unittest.TestCase):
    def setUp(self):
        self.secoes = secoes()

    def test_uma_ficha_por_er(self):
        self.assertEqual(sorted(self.secoes), sorted(PADROES))

    def test_sintaxe_copiada_do_codigo(self):
        for id_er, er in PADROES.items():
            with self.subTest(er=id_er):
                self.assertIn(f'`r"{em_tabela(er.padrao)}"`', self.secoes[id_er])

    def test_er_formal_igual_a_do_codigo(self):
        for id_er, er in PADROES.items():
            formal = er.formal.split(", com ")[0]
            with self.subTest(er=id_er):
                self.assertIn(f"| ER formal | `{em_tabela(formal)}` |", self.secoes[id_er])

    def test_cadeias_de_teste_documentadas(self):
        for id_er, casos in CASOS.items():
            secao = self.secoes[id_er]
            cadeias = casos["aceitas"] + [c for c, _ in casos["rejeitadas"]]
            for cadeia in cadeias:
                with self.subTest(er=id_er, cadeia=cadeia):
                    self.assertIn(f"| `{cadeia}` |" if cadeia else '| `""` |', secao)

    def test_resumo_do_afne_confere(self):
        for id_er, afne in AFNES.items():
            vazios = sum(r == "ε" for lista in afne.transicoes.values() for r, _ in lista)
            finais = ", ".join(f"`{f}`" for f in sorted(afne.finais))
            esperado = (f"{len(afne.estados)} estados, inicial `{afne.inicial}`, "
                        f"final {finais}, {vazios} movimentos ε")
            with self.subTest(er=id_er):
                self.assertIn(esperado, self.secoes[id_er])

    def test_tracos_sao_a_saida_real_do_simulador(self):
        for id_er, secao in self.secoes.items():
            encontrados = list(tracos(secao))
            with self.subTest(er=id_er):
                self.assertGreaterEqual(len(encontrados), 2, "falta traço aceito e rejeitado")
            for cadeia, traco in encontrados:
                with self.subTest(er=id_er, cadeia=cadeia):
                    self.assertEqual(traco, AFNES[id_er].formatar_traco(cadeia))


if __name__ == "__main__":
    unittest.main()
