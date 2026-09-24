import unittest

from decodmetar.afne.automato import EPSILON, AFNe, expandir_rotulo


def afne_ab_estrela_ou_c():
    """AFNε para (ab)* | c."""
    return AFNe(
        "teste",
        ["q0", "q1", "q2", "q3", "q4"],
        "q0",
        {"q2", "q4"},
        {
            "q0": [(EPSILON, "q2"), ("c", "q3")],
            "q2": [("a", "q1")],
            "q1": [("b", "q2")],
            "q3": [(EPSILON, "q4")],
        },
    )


class TestRotulo(unittest.TestCase):
    def test_literal(self):
        self.assertEqual(expandir_rotulo("K"), {"K"})

    def test_intervalo(self):
        self.assertEqual(expandir_rotulo("[0-2]"), {"0", "1", "2"})

    def test_lista(self):
        self.assertEqual(expandir_rotulo("[BDN]"), {"B", "D", "N"})

    def test_intervalo_misturado(self):
        self.assertEqual(expandir_rotulo("[A-CZ]"), {"A", "B", "C", "Z"})

    def test_intervalo_invertido(self):
        with self.assertRaises(ValueError):
            expandir_rotulo("[9-0]")


class TestAFNe(unittest.TestCase):
    def setUp(self):
        self.afne = afne_ab_estrela_ou_c()

    def test_fecho_epsilon(self):
        self.assertEqual(self.afne.fecho_epsilon({"q0"}), {"q0", "q2"})
        self.assertEqual(self.afne.fecho_epsilon({"q3"}), {"q3", "q4"})

    def test_aceita(self):
        for cadeia in ["", "ab", "abab", "c"]:
            with self.subTest(cadeia=cadeia):
                self.assertTrue(self.afne.aceita(cadeia))

    def test_rejeita(self):
        for cadeia in ["a", "ba", "abc", "cc", "x"]:
            with self.subTest(cadeia=cadeia):
                self.assertFalse(self.afne.aceita(cadeia))

    def test_simulacao_para_no_conjunto_vazio(self):
        passos = self.afne.simular("xab")
        self.assertEqual(len(passos), 2)
        self.assertEqual(passos[-1], ("x", set()))

    def test_traco(self):
        traco = self.afne.formatar_traco("ab")
        self.assertIn("início: {q0, q2}", traco)
        self.assertTrue(traco.endswith("resultado: ACEITA"))

    def test_estado_inexistente(self):
        with self.assertRaises(ValueError):
            AFNe("ruim", ["q0"], "q0", {"q0"}, {"q0": [("a", "q9")]})

    def test_alfabeto(self):
        self.assertEqual(self.afne.alfabeto, {"a", "b", "c"})


if __name__ == "__main__":
    unittest.main()
