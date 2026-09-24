"""AFNε com fecho-ε, aceitação e traço da simulação."""

EPSILON = "ε"


def expandir_rotulo(rotulo):
    """Conjunto de símbolos que um rótulo reconhece.

    Um rótulo é um símbolo literal ("K") ou uma classe finita no formato do
    guia ("[0-9]", "[BDINSW]"), que é só abreviação de uma união de símbolos.
    """
    if len(rotulo) < 3 or rotulo[0] != "[" or rotulo[-1] != "]":
        return {rotulo}
    miolo = rotulo[1:-1]
    simbolos = set()
    i = 0
    while i < len(miolo):
        if i + 2 < len(miolo) and miolo[i + 1] == "-":
            inicio, fim = miolo[i], miolo[i + 2]
            if inicio > fim:
                raise ValueError(f"Intervalo inválido no rótulo {rotulo}")
            simbolos.update(chr(c) for c in range(ord(inicio), ord(fim) + 1))
            i += 3
        else:
            simbolos.add(miolo[i])
            i += 1
    return simbolos


class AFNe:
    def __init__(self, nome, estados, inicial, finais, transicoes):
        """transicoes: {estado: [(rotulo, destino), ...]}; rótulo EPSILON é movimento vazio."""
        self.nome = nome
        self.estados = list(estados)
        self.inicial = inicial
        self.finais = set(finais)
        self.transicoes = {e: list(transicoes.get(e, [])) for e in self.estados}
        self._validar()
        self._simbolos = {
            rotulo: expandir_rotulo(rotulo)
            for lista in self.transicoes.values()
            for rotulo, _ in lista
            if rotulo != EPSILON
        }

    def _validar(self):
        conhecidos = set(self.estados)
        if self.inicial not in conhecidos:
            raise ValueError(f"{self.nome}: estado inicial {self.inicial} não existe")
        if not self.finais <= conhecidos:
            raise ValueError(f"{self.nome}: finais desconhecidos {self.finais - conhecidos}")
        for origem, lista in self.transicoes.items():
            for rotulo, destino in lista:
                if destino not in conhecidos:
                    raise ValueError(f"{self.nome}: {origem} --{rotulo}--> {destino} inexistente")

    @property
    def alfabeto(self):
        return set().union(*self._simbolos.values())

    def fecho_epsilon(self, conjunto):
        resultado = set(conjunto)
        pilha = list(conjunto)
        while pilha:
            estado = pilha.pop()
            for rotulo, destino in self.transicoes[estado]:
                if rotulo == EPSILON and destino not in resultado:
                    resultado.add(destino)
                    pilha.append(destino)
        return resultado

    def mover(self, conjunto, simbolo):
        return {
            destino
            for estado in conjunto
            for rotulo, destino in self.transicoes[estado]
            if rotulo != EPSILON and simbolo in self._simbolos[rotulo]
        }

    def simular(self, cadeia):
        """Lista de passos (símbolo, estados ativos); o primeiro passo tem símbolo None.

        Para no primeiro símbolo que esvazia o conjunto de estados.
        """
        atuais = self.fecho_epsilon({self.inicial})
        passos = [(None, atuais)]
        for simbolo in cadeia:
            atuais = self.fecho_epsilon(self.mover(atuais, simbolo))
            passos.append((simbolo, atuais))
            if not atuais:
                break
        return passos

    def aceita(self, cadeia):
        passos = self.simular(cadeia)
        consumiu_tudo = len(passos) == len(cadeia) + 1
        return consumiu_tudo and bool(passos[-1][1] & self.finais)

    def formatar_traco(self, cadeia):
        """Traço legível da simulação, usado na demonstração."""
        passos = self.simular(cadeia)
        linhas = [f"início: {formatar_conjunto(passos[0][1])}"]
        for simbolo, estados in passos[1:]:
            linhas.append(f"--{simbolo}--> {formatar_conjunto(estados)}")
        veredito = "ACEITA" if self.aceita(cadeia) else "REJEITADA"
        linhas.append(f"resultado: {veredito}")
        return "\n".join(linhas)


def formatar_conjunto(estados):
    if not estados:
        return "∅"
    return "{" + ", ".join(sorted(estados, key=lambda e: (len(e), e))) + "}"
