"""Automação de QA do sistema de estacionamento.

  python main.py                  roda os testes na versão correta
  python main.py --bug critico    liga o bug proposital crítico (cobrança errada)
  python main.py --bug leve       liga o bug proposital leve (mensagem sem motivo)
  python main.py --comparar       roda a versão correta e a com bug crítico, lado a lado
"""
import argparse
import os
import sys
from datetime import datetime

from qa import execucao, relatorio
from sistema import estacionamento

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # acentos no terminal do Windows

VERDE, VERMELHO, AMARELO, NEGRITO, FIM = "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m"
if os.name == "nt":
    os.system("")  # liga as cores ANSI no terminal do Windows


def rodar(bug):
    estacionamento.BUG = bug
    resultados = execucao.executar_testes()
    return {"resultados": resultados, "metricas": execucao.calcular_metricas(resultados)}


def imprimir(rodada, titulo):
    print(f"\n{NEGRITO}{titulo}{FIM}")
    print(f"{'ID':<5} {'Requisito':<18} {'Situação':<8} {'Severidade':<10} Descrição")
    print("-" * 100)
    for r in rodada["resultados"]:
        cor = VERDE if r["situacao"] == "PASS" else VERMELHO
        print(f"{r['id']:<5} {r['requisito']:<18} {cor}{r['situacao']:<8}{FIM} "
              f"{r['severidade']:<10} {r['descricao']}")
        if r["situacao"] == "FAIL":
            print(f"      esperado: {r['esperado']}\n      obtido:   {r['obtido']}")
    m = rodada["metricas"]
    cor = {"LIBERADO": VERDE, "LIBERADO COM RESSALVAS": AMARELO}.get(m["decisao"], VERMELHO)
    print("-" * 100)
    print(f"Total: {m['total']} | PASS: {m['aprovados']} | FAIL: {m['reprovados']} | "
          f"Aprovação: {m['taxa_aprovacao']}% | Falhas críticas: {m['criticas']}")
    print(f"Decisão de QA: {cor}{NEGRITO}{m['decisao']}{FIM}")


def salvar(rodada, modo, data_hora, comparacao=None):
    os.makedirs(relatorio.PASTA, exist_ok=True)
    arquivos = [
        relatorio.salvar_html(rodada["resultados"], rodada["metricas"], modo, data_hora, comparacao),
        relatorio.salvar_csv(rodada["resultados"], modo),
        relatorio.registrar_historico(data_hora, modo, rodada["metricas"]),
    ]
    print("\nArquivos gerados:")
    for a in arquivos:
        print("  " + os.path.relpath(a))


def main():
    parser = argparse.ArgumentParser(description="Automação de QA do estacionamento")
    parser.add_argument("--bug", choices=["critico", "leve"], help="liga um bug proposital")
    parser.add_argument("--comparar", action="store_true",
                        help="roda a versão correta e a versão com bug crítico e compara")
    args = parser.parse_args()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if args.comparar:
        bug = args.bug or "critico"
        antes = rodar(None)
        depois = rodar(bug)
        imprimir(antes, "VERSÃO CORRETA")
        imprimir(depois, f"VERSÃO COM BUG PROPOSITAL ({bug})")
        salvar(depois, f"comparacao_{bug}", data_hora,
               {"antes": antes, "depois": depois, "modo": bug})
    else:
        modo = f"bug_{args.bug}" if args.bug else "correta"
        rodada = rodar(args.bug)
        imprimir(rodada, f"VERSÃO {modo.upper().replace('_', ' ')}")
        salvar(rodada, modo, data_hora)


if __name__ == "__main__":
    main()
