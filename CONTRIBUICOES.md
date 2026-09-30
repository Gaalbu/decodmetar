# Contribuições dos integrantes

> **Antes da entrega:** preencham as linhas `[preencher]` do registro e ajustem a tabela ao que cada um realmente fez. O histórico do Git (`git log --format="%an %ad %s" --date=short`) serve de evidência.

## Divisão por frente

Cada integrante é dono de duas ERs do começo ao fim (padrão no código, ficha, AFNε, testes e a parte dessas ERs nos slides) e de uma parte da aplicação ou da documentação.

| Integrante | ERs | Parte da aplicação / documentação | Na apresentação |
|---|---|---|---|
| Davi Maciel Corrêa | ER-01 (identificação) e ER-02 (data/hora) | `decodmetar/decodificador.py`, `decodmetar/mensagens.py`, `tests/test_decodificador.py`: tokenização, ordem dos grupos, extração, tradução e avisos | Problema, solução e arquitetura |
| Gabriel Albuquerque Alencar | ER-03 (vento) e ER-04 (visibilidade) | `decodmetar/afne/` (simulador de AFNε, diagramas), `tests/test_afne.py`, `tests/test_automato.py`, `tests/test_diagramas.py` | Como a equivalência ER × AFNε é garantida |
| José Valdez | ER-05 (tempo presente) e ER-06 (nuvens) | `main.py` (menu e linha de comando), `tests/casos.py`, `tests/test_padroes.py`, `tests/test_main.py`, `dados/` | Demonstração ao vivo |
| Alberto Acosta | ER-07 (temperatura) e ER-08 (pressão) | `docs/EXPRESSOES_REGULARES.md`, relatório técnico, slides, `tests/test_documentacao.py`, este arquivo | Testes, limitações, melhorias e contribuições |

## Registro do que foi feito

| Data | Integrante | Entrega |
|---|---|---|
| 24/09/2026 | Gabriel Albuquerque Alencar | Plano de execução, README inicial e divisão de tarefas |
| 24/09/2026 | Gabriel Albuquerque Alencar | Padrões ER-03/ER-04 e casos de teste |
| 24/09/2026 | Gabriel Albuquerque Alencar | Simulador de AFNε (fecho-ε, aceitação, traço) |
| 24/09/2026 | Gabriel Albuquerque Alencar | AFNε das ER-03/ER-04, teste de equivalência regex × AFNε |
| 24/09/2026 | Gabriel Albuquerque Alencar | Geração dos diagramas e fichas das ER-03/ER-04 |
| 30/09/2026 | [preencher] | Padrões, casos e AFNε das ER-01, ER-02, ER-05, ER-06, ER-07 e ER-08 |
| 30/09/2026 | [preencher] | Decodificador, mensagens e testes do decodificador |
| 30/09/2026 | [preencher] | `main.py` (menu e linha de comando), dados de exemplo e testes da interface |
| 30/09/2026 | [preencher] | Fichas das 8 ERs, SVG dos AFNε, relatório técnico e resultado dos testes |

## Tarefas de todos

- [ ] Cada um revisou a ficha e o AFNε das suas duas ERs e rodou os testes.
- [ ] Todos entendem as 8 ERs (o professor pode perguntar sobre qualquer uma e pedir alterações ao vivo).
- [ ] Apresentação ensaiada (10 a 12 minutos).

## Uso de Inteligência Artificial

A equipe usou IA (Claude, da Anthropic) no planejamento, na escrita de parte do código, dos testes e da documentação. Detalhes na seção "Uso de Inteligência Artificial" do [README](README.md) e do [relatório técnico](docs/RELATORIO_TECNICO.pdf).
