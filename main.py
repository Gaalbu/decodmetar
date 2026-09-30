"""DecodMETAR: validador e decodificador de boletins METAR/SPECI com Expressões Regulares.

Uso:
    python main.py
        abre o menu interativo

    python main.py "METAR SBBE 241200Z 09010KT 9999 FEW020 30/24 Q1011"
        decodifica diretamente um boletim

    python main.py --arquivo dados/metar_misto.txt
        processa um arquivo com um boletim por linha

    python main.py --listar
        lista as expressões regulares utilizadas pelo programa

    python main.py --testar ER03 36015G25KT
        testa uma cadeia em uma ER usando regex e AFNε

    python main.py --testes
        executa a bateria de testes

    python main.py --gerar-diagramas
        gera novamente os diagramas dos AFNε em docs/afne/
"""

import argparse
import os
import sys

from decodmetar import mensagens as msg
from decodmetar.afne import diagramas
from decodmetar.afne.definicoes import AFNES
from decodmetar.decodificador import ErroArquivo, decodificar, processar_arquivo
from decodmetar.padroes import PADROES, normalizar_id, valida


LINHA = "-" * 72


# ----------------------------------------------------------------------- cores


class Cores:
    """Códigos ANSI, desligados quando a saída não é um terminal."""

    ativo = False

    @classmethod
    def configurar(cls):
        cls.ativo = sys.stdout.isatty() and "NO_COLOR" not in os.environ

        if cls.ativo and os.name == "nt":
            os.system("")  # habilita sequências ANSI no console do Windows

    @classmethod
    def pintar(cls, texto, codigo):
        return f"\033[{codigo}m{texto}\033[0m" if cls.ativo else texto


def verde(texto):
    return Cores.pintar(texto, "32;1")


def vermelho(texto):
    return Cores.pintar(texto, "31;1")


def amarelo(texto):
    return Cores.pintar(texto, "33")


def negrito(texto):
    return Cores.pintar(texto, "1")


def veredito(aceita):
    return verde("ACEITA") if aceita else vermelho("REJEITADA")


# --------------------------------------------------------------------- saídas


def mostrar_resultado(resultado):
    print(LINHA)
    print(f"Boletim: {resultado.entrada.strip() or '(vazio)'}")
    print(LINHA)

    for grupo in resultado.grupos:
        rotulo = PADROES[grupo.id_er].rotulo
        print(f"  {grupo.token:<15} {rotulo}  {grupo.traducao}")

    for ignorado in resultado.ignorados:
        print(
            f"  {ignorado:<15} ---    "
            "grupo ignorado (fora do escopo do programa)"
        )

    for aviso in resultado.avisos:
        print(amarelo(f"  AVISO: {aviso}"))

    for erro in resultado.erros:
        print(vermelho(f"  ERRO: {erro}"))

    if resultado.valido:
        print(verde("Resultado: boletim VÁLIDO"))
    else:
        print(
            vermelho(
                f"Resultado: boletim INVÁLIDO "
                f"({len(resultado.erros)} erro(s))"
            )
        )


def mostrar_arquivo(caminho):
    try:
        resultados = processar_arquivo(caminho)

    except ErroArquivo as erro:
        print(vermelho(f"Erro: {erro}"))
        return False

    for numero, resultado in resultados:
        print(f"\nLinha {numero}:")
        mostrar_resultado(resultado)

    validos = sum(resultado.valido for _, resultado in resultados)
    invalidos = len(resultados) - validos

    print(
        f"\n{LINHA}\n"
        f"Resumo: {len(resultados)} boletim(ns) lido(s): "
        f"{verde(f'{validos} válido(s)')}, "
        f"{vermelho(f'{invalidos} com erro')}."
    )

    for numero, resultado in resultados:
        for erro in resultado.erros:
            print(f"  linha {numero}: {erro}")

    return True


def mostrar_teste(id_er, cadeia):
    """Testa a cadeia na regex e no AFNε, exibindo o traço passo a passo."""

    er = PADROES[id_er]
    afne = AFNES[id_er]

    regex = valida(id_er, cadeia)
    automato = afne.aceita(cadeia)

    print(LINHA)
    print(negrito(f"{er.rotulo}: {er.nome}"))

    print(f"  Alfabeto Σ  : {er.alfabeto}")
    print(f"  ER formal   : {er.formal}")
    print(f'  No código   : r"{er.padrao}"   (usada com re.fullmatch)')

    print(
        f"  Cadeia      : {cadeia!r} ({len(cadeia)} símbolo(s))"
        + ("  = palavra vazia ε" if not cadeia else "")
    )

    fora = sorted(set(cadeia) - afne.alfabeto)

    if fora:
        print(
            amarelo(
                "  Símbolos fora do alfabeto Σ: "
                + ", ".join(repr(simbolo) for simbolo in fora)
            )
        )

    print(LINHA)

    print(f"  re.fullmatch: {veredito(regex)}")
    print(f"  AFNε        : {veredito(automato)}")

    if regex != automato:
        print(
            vermelho(
                "  ATENÇÃO: a regex e o AFNε discordaram! "
                "A ER e o AFNε não representam a mesma linguagem."
            )
        )

    print(
        f"\n  Traço do AFNε "
        f"(inicial {afne.inicial}, "
        f"finais {', '.join(sorted(afne.finais))}):"
    )

    for linha in afne.formatar_traco(cadeia).splitlines():
        print(f"    {linha}")


def listar_ers():
    for er in PADROES.values():
        afne = AFNES[er.id]

        vazios = sum(
            simbolo == "ε"
            for lista in afne.transicoes.values()
            for simbolo, _ in lista
        )

        print(LINHA)
        print(negrito(f"{er.rotulo}: {er.nome}"))
        print(f"  {er.descricao}")
        print(f"  Σ         = {er.alfabeto}")
        print(f"  ER formal : {er.formal}")
        print(f'  Código    : r"{er.padrao}"')

        print(
            f"  AFNε      : {len(afne.estados)} estados, "
            f"inicial {afne.inicial}, "
            f"finais {', '.join(sorted(afne.finais))}, "
            f"{vazios} movimentos ε "
            f"(docs/afne/{er.id}.md)"
        )


def rodar_testes():
    from tests.relatorio import (
        executar_unittest,
        tabela_casos,
        tabela_equivalencia,
    )

    print("Casos fixos das fichas (regex e AFNε):\n")
    print(tabela_casos()[0])

    print("\nEquivalência regex x AFNε em cadeias geradas:\n")
    print(tabela_equivalencia()[0])

    print("\nunittest:\n")

    return executar_unittest(
        sys.stdout,
        verbosidade=1,
    ).wasSuccessful()


def gerar_diagramas():
    for caminho in diagramas.gerar():
        print(f"gerado: {caminho}")


# ----------------------------------------------------------------------- menu


def ler(pergunta):
    """input() que devolve None em Ctrl+C / Ctrl+D (fim da entrada)."""

    try:
        return input(pergunta)

    except (EOFError, KeyboardInterrupt):
        print()
        return None


def pedir_er():
    ids = ", ".join(er.id for er in PADROES.values())

    while True:
        texto = ler(
            f"Qual ER? "
            f"(1 a {len(PADROES)} ou {ids}; Enter volta): "
        )

        if texto is None or not texto.strip():
            return None

        id_er = normalizar_id(texto)

        if id_er:
            return id_er

        print(
            vermelho(
                f"ER '{texto.strip()}' inexistente. "
                f"Digite um número de 1 a {len(PADROES)}."
            )
        )


def opcao_decodificar():
    texto = ler(
        f"Digite o boletim "
        f"(ex.: {msg.EXEMPLO}):\n> "
    )

    if texto is not None:
        mostrar_resultado(decodificar(texto))


def opcao_arquivo():
    caminho = ler(
        "Caminho do arquivo "
        "(ex.: dados/metar_misto.txt): "
    )

    if caminho is None:
        return

    if not caminho.strip():
        print(vermelho("Nenhum caminho informado."))
        return

    mostrar_arquivo(caminho)


def opcao_testar():
    id_er = pedir_er()

    if id_er is None:
        return

    cadeia = ler(
        f"Cadeia para a {PADROES[id_er].rotulo} "
        "(Enter vazio testa a palavra vazia ε): "
    )

    if cadeia is None:
        return

    if not cadeia:
        print(
            amarelo(
                "Entrada vazia: será testada "
                "a palavra vazia ε."
            )
        )

    mostrar_teste(id_er, cadeia)


# ---------------------------------------------------------------- opções menu


OPCOES = {
    "1": (
        "Decodificar um boletim digitado",
        opcao_decodificar,
    ),
    "2": (
        "Processar arquivo de boletins",
        opcao_arquivo,
    ),
    "3": (
        "Listar expressões regulares",
        listar_ers,
    ),
    "4": (
        "Testar uma cadeia em uma expressão regular",
        opcao_testar,
    ),
    "5": (
        "Executar bateria de testes",
        rodar_testes,
    ),
    "6": (
        "Gerar diagramas dos autômatos",
        gerar_diagramas,
    ),
}


def menu():
    while True:
        print()
        print(negrito("=== DecodMETAR ==="))
        print("Validador e decodificador de boletins METAR/SPECI")
        print()

        for chave, (descricao, _) in OPCOES.items():
            print(f"{chave}) {descricao}")

        print("0) Sair")

        escolha = ler("\nEscolha uma opção: ")

        if escolha is None:
            print("\nAté mais!")
            return

        escolha = escolha.strip()

        if escolha == "0":
            print("\nAté mais!")
            return

        acao = OPCOES.get(escolha)

        if acao is None:
            print(
                vermelho(
                    f"Opção inválida. "
                    f"Digite um número entre 0 e {len(OPCOES)}."
                )
            )
            continue

        _, funcao = acao
        funcao()


# ------------------------------------------------------------------------ CLI


def argumentos(args):
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description=(
            "DecodMETAR — valida e decodifica boletins METAR/SPECI "
            "utilizando Expressões Regulares e AFNε."
        ),
    )

    parser.add_argument(
        "boletim",
        nargs="?",
        help=(
            "boletim METAR/SPECI entre aspas; "
            "sem argumentos abre o menu"
        ),
    )

    parser.add_argument(
        "--arquivo",
        metavar="CAMINHO",
        help="processa um arquivo contendo um boletim por linha",
    )

    parser.add_argument(
        "--listar",
        action="store_true",
        help="lista as expressões regulares utilizadas pelo programa",
    )

    parser.add_argument(
        "--testar",
        nargs=2,
        metavar=("ER", "CADEIA"),
        help="testa uma cadeia em uma ER usando regex e AFNε",
    )

    parser.add_argument(
        "--testes",
        action="store_true",
        help="executa a bateria de testes do programa",
    )

    parser.add_argument(
        "--gerar-diagramas",
        action="store_true",
        help="gera novamente os diagramas dos AFNε em docs/afne/",
    )

    return parser.parse_args(args)


def main(args=None):
    # Configuração da codificação do terminal
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(
                encoding="utf-8",
                errors="replace",
            )

    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(
            encoding="utf-8",
            errors="replace",
        )

    Cores.configurar()

    opcoes = argumentos(args)

    # 1. Decodificação direta de um boletim
    if opcoes.boletim is not None:
        resultado = decodificar(opcoes.boletim)

        mostrar_resultado(resultado)

        return 0 if resultado.valido else 1

    # 2. Processamento de arquivo
    if opcoes.arquivo is not None:
        return 0 if mostrar_arquivo(opcoes.arquivo) else 1

    # 3. Listagem das expressões regulares
    if opcoes.listar:
        listar_ers()
        return 0

    # 4. Teste individual de uma ER
    if opcoes.testar:
        nome_er = opcoes.testar[0]
        cadeia = opcoes.testar[1]

        id_er = normalizar_id(nome_er)

        if id_er is None:
            print(
                vermelho(
                    f"ER '{nome_er}' inexistente. "
                    f"Use ER01 a ER{len(PADROES):02d}."
                )
            )
            return 2

        mostrar_teste(id_er, cadeia)

        return 0

    # 5. Bateria de testes
    if opcoes.testes:
        return 0 if rodar_testes() else 1

    # 6. Geração dos diagramas
    if opcoes.gerar_diagramas:
        gerar_diagramas()
        return 0

    # Nenhum argumento: abre o menu interativo
    try:
        menu()

    except KeyboardInterrupt:
        print("\nAté mais!")

    return 0


if __name__ == "__main__":
    sys.exit(main())