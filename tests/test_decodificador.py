import tempfile
import unittest
from pathlib import Path

from decodmetar.decodificador import (
    ErroArquivo,
    adivinhar,
    decodificar,
    diagnosticar,
    ler_boletins,
    processar_arquivo,
)

RAIZ = Path(__file__).resolve().parents[1]
COMPLETO = "METAR SBBE 241200Z 09010KT 9999 -RA FEW020 SCT100 30/24 Q1011"


class TestBoletinsValidos(unittest.TestCase):
    def test_boletim_completo(self):
        r = decodificar(COMPLETO)
        self.assertTrue(r.valido, r.erros)
        self.assertEqual([g.id_er for g in r.grupos],
                         ["ER01", "ER02", "ER03", "ER04", "ER05", "ER06", "ER06", "ER07", "ER08"])
        texto = " ".join(r.traducao)
        for trecho in ["Belém", "dia 24 às 12:00 UTC", "Vento de 090°", "10 km ou mais",
                       "chuva (intensidade fraca)", "2.000 pés", "30 °C", "1.011 hPa"]:
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, texto)

    def test_campos_extraidos(self):
        c = decodificar("SPECI SBEG 241530Z 36015G25KT 3000 +TSRA BKN015CB 26/24 Q1009").campos
        self.assertEqual(c["tipo"], "SPECI")
        self.assertEqual(c["aerodromo"], "SBEG")
        self.assertEqual((c["dia"], c["hora"], c["minuto"]), (24, 15, 30))
        self.assertEqual((c["vento_direcao"], c["vento_velocidade"], c["vento_rajada"]), ("360", 15, 25))
        self.assertEqual(c["visibilidade_m"], 3000)
        self.assertEqual(c["tempo_presente"], ["+TSRA"])
        self.assertEqual(c["nuvens"], ["BKN015CB"])
        self.assertEqual((c["temperatura"], c["orvalho"], c["pressao_hpa"]), (26, 24, 1009))

    def test_cor_igual_final_e_temperatura_negativa(self):
        r = decodificar("METAR COR SBPA 240900Z VRB03KT 0800 FG VV002 M02/M04 Q1024=")
        self.assertTrue(r.valido, r.erros)
        self.assertTrue(r.campos["corrigido"])
        self.assertEqual((r.campos["temperatura"], r.campos["orvalho"]), (-2, -4))
        self.assertIn("direção variável", r.traducao[2])

    def test_cavok_e_grupos_ignorados(self):
        r = decodificar("METAR SBBR 241200Z 00000KT CAVOK 22/08 Q1018 NOSIG")
        self.assertTrue(r.valido, r.erros)
        self.assertEqual(r.ignorados, ["NOSIG"])
        self.assertIn("calmo", r.traducao[2])

    def test_rmk_ignora_o_resto(self):
        r = decodificar(COMPLETO + " RMK QUALQUER COISA 123")
        self.assertTrue(r.valido, r.erros)
        self.assertEqual(r.ignorados, ["RMK QUALQUER COISA 123"])

    def test_varios_fenomenos_e_camadas(self):
        r = decodificar("METAR SBSP 240600Z 16004KT 1500SW -DZ BR OVC004 OVC010 15/15 Q1019")
        self.assertTrue(r.valido, r.erros)
        self.assertEqual(r.campos["tempo_presente"], ["-DZ", "BR"])
        self.assertEqual(len(r.campos["nuvens"]), 2)

    def test_espacos_extras_sao_ignorados(self):
        self.assertTrue(decodificar("  METAR   SBBE 241200Z 09010KT 9999 30/24 Q1011  ").valido)


class TestEntradasInvalidas(unittest.TestCase):
    def assertErroCom(self, boletim, trecho):
        r = decodificar(boletim)
        self.assertFalse(r.valido)
        self.assertTrue(any(trecho in e for e in r.erros), f"'{trecho}' não está em {r.erros}")

    def test_vazia(self):
        for entrada in ["", "   ", "\n", "=", None]:
            with self.subTest(entrada=entrada):
                self.assertErroCom(entrada, "Entrada vazia")

    def test_minusculas(self):
        self.assertErroCom("metar SBBE 241200Z 09010KT 9999 30/24 Q1011", "maiúsculas")
        self.assertErroCom("METAR SBBE 241200z 09010KT 9999 30/24 Q1011", "maiúsculas")

    def test_cabecalho(self):
        self.assertErroCom("METAR SABE 241200Z 09010KT 9999 30/24 Q1011", "não é aeródromo brasileiro")
        self.assertErroCom("TAF SBBE 241200Z", "TAF")
        self.assertErroCom("METAR", "falta o indicativo")
        self.assertErroCom("METAR COR", "falta o indicativo")
        self.assertErroCom("METARSBBE 241200Z", "falta o espaço")
        self.assertErroCom("METAR SBB 241200Z", "tem 3 caracteres")
        self.assertErroCom("BOLETIM SBBE", "deve começar com METAR ou SPECI")

    def test_grupos_com_valor_fora_da_faixa(self):
        casos = {
            "321200Z": "dia 32",
            "242400Z": "hora 24",
            "241260Z": "minuto 60",
        }
        for data, trecho in casos.items():
            with self.subTest(data=data):
                self.assertErroCom(f"METAR SBBE {data} 09010KT 9999 30/24 Q1011", trecho)
        self.assertErroCom("METAR SBBE 241200Z 37010KT 9999 30/24 Q1011", "370° acima de 360°")
        self.assertErroCom("METAR SBBE 241200Z 09510KT 9999 30/24 Q1011", "não é múltipla de 10")
        self.assertErroCom("METAR SBBE 241200Z 09010KT 9999 30/24 Q1100", "1100 hPa")
        self.assertErroCom("METAR SBBE 241200Z 09010KT 9999 3/24 Q1011", "2 algarismos")

    def test_grupo_desconhecido(self):
        self.assertErroCom("METAR SBBE 241200Z 09010KT 9999 XYZ123 30/24 Q1011", "não reconhecido")

    def test_fora_de_ordem(self):
        self.assertErroCom("METAR SBBE 241200Z 09010KT 9999 30/24 FEW020 Q1011", "fora de ordem")

    def test_grupo_obrigatorio_faltando(self):
        self.assertErroCom("METAR SBBE 241200Z 9999 30/24 Q1011", "vento de superfície (ER-03)")
        self.assertErroCom("METAR SBBE", "Faltam grupos obrigatórios")

    def test_repetido(self):
        self.assertErroCom("METAR SBBE 241200Z 09010KT 9999 9999 30/24 Q1011", "repetido")

    def test_nuvem_depois_de_cavok(self):
        self.assertErroCom("METAR SBBR 241200Z 00000KT CAVOK FEW020 22/08 Q1018", "CAVOK")

    def test_nao_lanca_excecao_com_lixo(self):
        for lixo in ["METAR SBBE ////// ////KT", "METAR SBBE 241200Z ++ -- VC / Q", "ÁÉÍ çã", "METAR SBBE " + "X" * 500]:
            with self.subTest(lixo=lixo[:30]):
                self.assertFalse(decodificar(lixo).valido)


class TestAvisos(unittest.TestCase):
    def test_orvalho_maior_que_temperatura(self):
        r = decodificar("METAR SBBE 241200Z 09010KT 9999 30/32 Q1011")
        self.assertTrue(r.valido)
        self.assertTrue(any("orvalho" in a for a in r.avisos))

    def test_rajada_menor_que_media(self):
        r = decodificar("METAR SBBE 241200Z 09020G10KT 9999 30/24 Q1011")
        self.assertTrue(any("rajada" in a for a in r.avisos))


class TestDiagnostico(unittest.TestCase):
    def test_adivinhar(self):
        casos = {"37010KT": "ER03", "3/24": "ER07", "Q1100": "ER08", "A2992": "ER08",
                 "321200Z": "ER02", "99999": "ER04", "FEW20": "ER06", "SKC": "ER06",
                 "TSTS": "ER05", "-VC": "ER05", "XYZ123": None}
        for token, esperado in casos.items():
            with self.subTest(token=token):
                self.assertEqual(adivinhar(token), esperado)

    def test_motivos(self):
        casos = [
            ("ER03", "09010MPS", "MPS"), ("ER03", "0901KT", "velocidade"),
            ("ER03", "36015G5KT", "rajada"), ("ER04", "5000X", "não é direção"),
            ("ER04", "CAVOK9999", "sozinho"), ("ER05", "SHXX", "XX"),
            ("ER05", "-+RA", "mais de uma"), ("ER06", "BKN015XB", "XB"),
            ("ER06", "FEW0200", "3 algarismos"), ("ER07", "30//24", "única barra"),
            ("ER08", "A2992", "polegadas"), ("ER08", "Q0899", "899 hPa"),
        ]
        for id_er, token, trecho in casos:
            with self.subTest(token=token):
                self.assertIn(trecho, diagnosticar(id_er, token))


class TestArquivos(unittest.TestCase):
    def test_exemplos_do_repositorio(self):
        validos = processar_arquivo(RAIZ / "dados" / "metar_validos.txt")
        self.assertTrue(all(r.valido for _, r in validos), [r.erros for _, r in validos])
        com_erros = processar_arquivo(RAIZ / "dados" / "metar_com_erros.txt")
        self.assertTrue(com_erros)
        self.assertTrue(all(not r.valido for _, r in com_erros))

    def test_linhas_em_branco_e_comentarios(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "b.txt"
            caminho.write_text("# comentário\n\n  \n" + COMPLETO + "\n\n", encoding="utf-8")
            self.assertEqual(ler_boletins(caminho), [(4, COMPLETO)])

    def test_erros_de_arquivo(self):
        with tempfile.TemporaryDirectory() as pasta:
            vazio = Path(pasta) / "vazio.txt"
            vazio.write_text("\n\n# só comentário\n", encoding="utf-8")
            binario = Path(pasta) / "bin.txt"
            binario.write_bytes(b"\xff\xfe\x00\x81METAR")
            casos = {
                Path(pasta) / "nao_existe.txt": "não encontrado",
                Path(pasta): "é uma pasta",
                vazio: "está vazio",
                binario: "UTF-8",
                "": "Nenhum caminho",
            }
            for caminho, trecho in casos.items():
                with self.subTest(caminho=str(caminho)):
                    with self.assertRaises(ErroArquivo) as ctx:
                        ler_boletins(caminho)
                    self.assertIn(trecho, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
