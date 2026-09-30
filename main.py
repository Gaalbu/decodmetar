"""DecodMETAR: validador e decodificador de boletins METAR/SPECI com Expressões Regulares.

Uso:
    python main.py                                  menu interativo
    python main.py "METAR SBBE 241200Z 09010KT 9999 FEW020 30/24 Q1011"
    python main.py --arquivo dados/metar_misto.txt
    python main.py --testar ER03 36015G25KT         regex + traço do AFNε
    python main.py --listar                         as 8 ERs do programa
    python main.py --gerar-diagramas                refaz docs/afne/
    python main.py --testes                         bateria de testes
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


class Cores:
    """Códigos ANSI, desligados quando a saída não é um terminal."""

    ativo = False

    @classmethod
    def configurar(cls):
        cls.ativo = sys.stdout.isatty() and "NO_COLOR" not in os.environ
        if cls.ativo and os.name == "nt":
            os.system("")  # liga as sequências ANSI no console do Windows

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
        print(f"  {ignorado:<15} ---    grupo ignorado (fora do escopo do programa)")
    for aviso in resultado.avisos:
        print(amarelo(f"  AVISO: {aviso}"))
    for erro in resultado.erros:
        print(vermelho(f"  ERRO: {erro}"))
    if resultado.valido:
        print(verde("Resultado: boletim VÁLIDO"))
    else:
        print(vermelho(f"Resultado: boletim INVÁLIDO ({len(resultado.erros)} erro(s))"))


def mostrar_arquivo(caminho):
    try:
        resultados = processar_arquivo(caminho)
    except ErroArquivo as erro:
        print(vermelho(f"Erro: {erro}"))
        return False
    for numero, resultado in resultados:
        print(f"\nLinha {numero}:")
        mostrar_resultado(resultado)
    validos = sum(r.valido for _, r in resultados)
    print(f"\n{LINHA}\nResumo: {len(resultados)} boletim(ns) lido(s): "
          f"{verde(f'{validos} válido(s)')}, {vermelho(f'{len(resultados) - validos} com erro')}.")
    for numero, resultado in resultados:
        for erro in resultado.erros:
            print(f"  linha {numero}: {erro}")
    return True


def mostrar_teste(id_er, cadeia):
    """Testa a cadeia na regex e no AFNε, com o traço passo a passo."""
    er, afne = PADROES[id_er], AFNES[id_er]
    regex = valida(id_er, cadeia)
    automato = afne.aceita(cadeia)
    print(LINHA)
    print(negrito(f"{er.rotulo}: {er.nome}"))
    print(f"  Alfabeto Σ  : {er.alfabeto}")
    print(f"  ER formal   : {er.formal}")
    print(f'  No código   : r"{er.padrao}"   (usada com re.fullmatch)')
    print(f"  Cadeia      : {cadeia!r} ({len(cadeia)} símbolo(s))"
          + ("  = palavra vazia ε" if not cadeia else ""))
    fora = sorted(set(cadeia) - afne.alfabeto)
    if fora:
        print(amarelo(f"  Símbolos fora do alfabeto Σ: {', '.join(repr(s) for s in fora)}"))
    print(LINHA)
    print(f"  re.fullmatch: {veredito(regex)}")
    print(f"  AFNε        : {veredito(automato)}")
    if regex != automato:
        print(vermelho("  ATENÇÃO: a regex e o AFNε discordaram! A ER e o AFNε não "
                       "representam a mesma linguagem."))
    print(f"\n  Traço do AFNε (inicial {afne.inicial}, finais {', '.join(sorted(afne.finais))}):")
    for linha in afne.formatar_traco(cadeia).splitlines():
        print(f"    {linha}")


def listar_ers():
    for er in PADROES.values():
        afne = AFNES[er.id]
        vazios = sum(r == "ε" for lista in afne.transicoes.values() for r, _ in lista)
        print(LINHA)
        print(negrito(f"{er.rotulo}: {er.nome}"))
        print(f"  {er.descricao}")
        print(f"  Σ         = {er.alfabeto}")
        print(f"  ER formal : {er.formal}")
        print(f'  Código    : r"{er.padrao}"')
        print(f"  AFNε      : {len(afne.estados)} estados, inicial {afne.inicial}, "
              f"finais {', '.join(sorted(afne.finais))}, {vazios} movimentos ε "
              f"(docs/afne/{er.id}.md)")


def rodar_testes():
    from tests.relatorio import executar_unittest, tabela_casos, tabela_equivalencia

    print("Casos fixos das fichas (regex e AFNε):\n")
    print(tabela_casos()[0])
    print("\nEquivalência regex x AFNε em cadeias geradas:\n")
    print(tabela_equivalencia()[0])
    print("\nunittest:\n")
    return executar_unittest(sys.stdout, verbosidade=1).wasSuccessful()


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
        texto = ler(f"Qual ER? (1 a {len(PADROES)} ou {ids}; Enter volta): ")
        if texto is None or not texto.strip():
            return None
        id_er = normalizar_id(texto)
        if id_er:
            return id_er
        print(vermelho(f"ER '{texto.strip()}' inexistente. Digite um número de 1 a {len(PADROES)}."))


def opcao_decodificar():
    texto = ler(f"Digite o boletim (ex.: {msg.EXEMPLO}):\n> ")
    if texto is not None:
        mostrar_resultado(decodificar(texto))


def opcao_arquivo():
    caminho = ler("Caminho do arquivo (ex.: dados/metar_misto.txt): ")
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
    cadeia = ler(f"Cadeia para a {PADROES[id_er].rotulo} (Enter vazio testa a palavra vazia ε): ")
    if cadeia is None:
        return
    if not cadeia:
        print(amarelo("Entrada vazia: será testada a palavra vazia ε."))
    mostrar_teste(id_er, cadeia)


OPCOES = {
    "1": ("Decodificar um boletim digitado", opcao_decodificar),
    "2": ("Processar arquivo de boletins", opcao_arquivo),
    "3": ("Testar uma cadeia em uma ER (regex + AFNε com traço)", opcao_testar),
    "4": ("Listar as expressões regulares do programa", listar_ers),
    "5": ("Rodar a bateria de testes", rodar_testes),
    "6": ("Gerar de novo os diagramas dos AFNε (docs/afne/)", gerar_diagramas),
}


def menu():
    while True:
        print(f"\n{negrito('=== DecodMETAR ===')}")
        for chave, (descricao, _) in OPCOES.items():
            print(f"{chave}) {descricao}")
        print("0) Sair")
        escolha = ler("Opção: ")
        if escolha is None or escolha.strip() == "0":
            print("Até mais!")
            return
        acao = OPCOES.get(escolha.strip())
        if acao is None:
            print(vermelho(f"Opção inválida. Digite um número de 0 a {len(OPCOES)}."))
            continue
        acao[1]()


# ------------------------------------------------------------------------ CLI


def argumentos(args):
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Valida e decodifica boletins METAR/SPECI usando Expressões Regulares.",
    )
    parser.add_argument("boletim", nargs="?", help="boletim entre aspas; sem nada abre o menu")
    parser.add_argument("--arquivo", metavar="CAMINHO", help="arquivo com um boletim por linha")
    parser.add_argument("--testar", nargs=2, metavar=("ER", "CADEIA"),
                        help="testa a cadeia na ER (regex + AFNε com traço)")
    parser.add_argument("--listar", action="store_true", help="lista as ERs")
    parser.add_argument("--gerar-diagramas", action="store_true", help="gera docs/afne/")
    parser.add_argument("--testes", action="store_true", help="roda a bateria de testes")
    return parser.parse_args(args)


def main(args=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    Cores.configurar()
    opcoes = argumentos(args)

    if opcoes.testar:
        id_er = normalizar_id(opcoes.testar[0])
        if id_er is None:
            print(vermelho(f"ER '{opcoes.testar[0]}' inexistente. Use ER01 a ER{len(PADROES):02d}."))
            return 2
        mostrar_teste(id_er, opcoes.testar[1])
        return 0
    if opcoes.arquivo is not None:
        return 0 if mostrar_arquivo(opcoes.arquivo) else 1
    if opcoes.listar:
        listar_ers()
        return 0
    if opcoes.gerar_diagramas:
        gerar_diagramas()
        return 0
    if opcoes.testes:
        return 0 if rodar_testes() else 1
    if opcoes.boletim is not None:
        resultado = decodificar(opcoes.boletim)
        mostrar_resultado(resultado)
        return 0 if resultado.valido else 1
    try:
        menu()
    except KeyboardInterrupt:
        print("\nAté mais!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
