"""Testes da interface (linha de comando e menu), sem abrir terminal."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import main

RAIZ = Path(__file__).resolve().parents[1]


def executar(args=None, entradas=()):
    """Roda main.main e devolve (código de saída, texto impresso)."""
    respostas = iter(entradas)

    def falso_input(pergunta=""):
        print(pergunta, end="")
        try:
            return next(respostas)
        except StopIteration:
            raise EOFError from None

    saida = io.StringIO()
    with redirect_stdout(saida), mock.patch("builtins.input", falso_input):
        codigo = main.main(args if args is not None else [])
    return codigo, saida.getvalue()


class TestLinhaDeComando(unittest.TestCase):
    def test_boletim_valido(self):
        codigo, texto = executar(["METAR SBBE 241200Z 09010KT 9999 30/24 Q1011"])
        self.assertEqual(codigo, 0)
        self.assertIn("boletim VÁLIDO", texto)

    def test_boletim_invalido(self):
        codigo, texto = executar(["METAR SBBE 241200Z 37010KT 9999 30/24 Q1011"])
        self.assertEqual(codigo, 1)
        self.assertIn("370°", texto)

    def test_boletim_vazio(self):
        codigo, texto = executar([""])
        self.assertEqual(codigo, 1)
        self.assertIn("Entrada vazia", texto)

    def test_testar(self):
        codigo, texto = executar(["--testar", "ER03", "36015G25KT"])
        self.assertEqual(codigo, 0)
        self.assertIn("re.fullmatch: ACEITA", texto)
        self.assertIn("AFNε        : ACEITA", texto)
        self.assertIn("lê 'G' → {q12}", texto)

    def test_testar_rejeitada_e_palavra_vazia(self):
        _, texto = executar(["--testar", "8", ""])
        self.assertIn("palavra vazia ε", texto)
        self.assertIn("re.fullmatch: REJEITADA", texto)

    def test_testar_er_inexistente(self):
        codigo, texto = executar(["--testar", "ER99", "x"])
        self.assertEqual(codigo, 2)
        self.assertIn("inexistente", texto)

    def test_arquivo(self):
        codigo, texto = executar(["--arquivo", str(RAIZ / "dados" / "metar_misto.txt")])
        self.assertEqual(codigo, 0)
        self.assertIn("Resumo: 7 boletim(ns) lido(s)", texto)

    def test_arquivo_inexistente(self):
        codigo, texto = executar(["--arquivo", "nao_existe.txt"])
        self.assertEqual(codigo, 1)
        self.assertIn("não encontrado", texto)

    def test_listar(self):
        _, texto = executar(["--listar"])
        for n in range(1, 9):
            self.assertIn(f"ER-0{n}", texto)


class TestMenu(unittest.TestCase):
    def test_opcoes_invalidas_nao_travam(self):
        _, texto = executar(entradas=["9", "abc", "", "0"])
        self.assertEqual(texto.count("Opção inválida"), 3)
        self.assertIn("Até mais!", texto)

    def test_fim_da_entrada_sai_sem_erro(self):
        codigo, texto = executar(entradas=[])
        self.assertEqual(codigo, 0)
        self.assertIn("Até mais!", texto)

    def test_decodificar_pelo_menu(self):
        _, texto = executar(entradas=["1", "METAR SBBE 241200Z 09010KT 9999 30/24 Q1011", "0"])
        self.assertIn("boletim VÁLIDO", texto)

    def test_testar_pelo_menu(self):
        _, texto = executar(entradas=["3", "x", "7", "M05/M07", "0"])
        self.assertIn("inexistente", texto)
        self.assertIn("re.fullmatch: ACEITA", texto)

    def test_arquivo_pelo_menu(self):
        _, texto = executar(entradas=["2", "", "2", "pasta_que_nao_existe/x.txt", "0"])
        self.assertIn("Nenhum caminho informado", texto)
        self.assertIn("não encontrado", texto)


if __name__ == "__main__":
    unittest.main()
