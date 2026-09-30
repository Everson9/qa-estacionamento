"""Gera o relatório final de qualidade (HTML e CSV) e o histórico de execuções."""
import csv
import html
import os

from sistema import estacionamento

PASTA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "relatorios")

REGRAS = estacionamento.REGRAS

CAMPOS = ["id", "requisito", "descricao", "esperado", "obtido", "situacao", "severidade", "duracao_ms"]

NOME_VERSAO = {
    "correta": "versão correta",
    "bug_leve": "versão com bug proposital leve",
    "bug_critico": "versão com bug proposital crítico",
    "comparacao_critico": "versão com bug proposital crítico (comparada com a correta)",
    "comparacao_leve": "versão com bug proposital leve (comparada com a correta)",
}

COR_DECISAO = {"LIBERADO": "#1b7a3a", "LIBERADO COM RESSALVAS": "#9a5b00", "NÃO LIBERAR": "#b3261e"}


def salvar_csv(resultados, modo):
    caminho = os.path.join(PASTA, f"resultados_{modo}.csv")
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";")
        w.writeheader()
        w.writerows(resultados)
    return caminho


def registrar_historico(data_hora, modo, metricas):
    caminho = os.path.join(PASTA, "historico_execucoes.csv")
    novo = not os.path.exists(caminho)
    with open(caminho, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        if novo:
            w.writerow(["data_hora", "versao", "total", "aprovados", "reprovados",
                        "taxa_aprovacao", "falhas_criticas", "decisao"])
        w.writerow([data_hora, modo, metricas["total"], metricas["aprovados"],
                    metricas["reprovados"], metricas["taxa_aprovacao"],
                    metricas["criticas"], metricas["decisao"]])
    return caminho


def _e(texto):
    return html.escape(str(texto))


def _tabela_testes(resultados):
    linhas = []
    for r in resultados:
        classe = "pass" if r["situacao"] == "PASS" else "fail"
        linhas.append(
            f"<tr class='{classe}'><td>{_e(r['id'])}</td><td>{_e(r['requisito'])}</td>"
            f"<td>{_e(r['descricao'])}</td><td><code>{_e(r['esperado'])}</code></td>"
            f"<td><code>{_e(r['obtido'])}</code></td><td class='sit'>{r['situacao']}</td>"
            f"<td>{_e(r['severidade'])}</td></tr>")
    return ("<table><thead><tr><th>ID</th><th>Requisito</th><th>Descrição</th>"
            "<th>Esperado</th><th>Obtido</th><th>Situação</th><th>Severidade</th></tr></thead>"
            f"<tbody>{''.join(linhas)}</tbody></table>")


def _defeitos(resultados):
    falhas = [r for r in resultados if r["situacao"] == "FAIL"]
    if not falhas:
        return "<p>Nenhum defeito encontrado nesta versão.</p>"
    itens = "".join(
        f"<li><strong>{_e(r['id'])} ({_e(r['severidade'])})</strong> — {_e(r['descricao'])}. "
        f"Esperado <code>{_e(r['esperado'])}</code>, o sistema devolveu <code>{_e(r['obtido'])}</code>.</li>"
        for r in falhas)
    return f"<ul>{itens}</ul>"


def _comparacao(antes, depois, modo):
    ma, md = antes["metricas"], depois["metricas"]
    linhas = [("Testes aprovados", ma["aprovados"], md["aprovados"]),
              ("Testes reprovados", ma["reprovados"], md["reprovados"]),
              ("Taxa de aprovação", f"{ma['taxa_aprovacao']}%", f"{md['taxa_aprovacao']}%"),
              ("Falhas críticas", ma["criticas"], md["criticas"]),
              ("Decisão de QA", ma["decisao"], md["decisao"])]
    corpo = "".join(f"<tr><td>{a}</td><td>{_e(b)}</td><td>{_e(c)}</td></tr>" for a, b, c in linhas)
    mudaram = [d["id"] for a, d in zip(antes["resultados"], depois["resultados"])
               if a["situacao"] != d["situacao"]]
    return (f"<h2>Antes e depois do bug proposital ({_e(modo)})</h2>"
            "<table class='comp'><thead><tr><th>Métrica</th><th>Versão correta</th>"
            f"<th>Versão com bug</th></tr></thead><tbody>{corpo}</tbody></table>"
            f"<p>Testes que mudaram de resultado: <strong>{_e(', '.join(mudaram) or 'nenhum')}</strong>.</p>")


def salvar_html(resultados, metricas, modo, data_hora, comparacao=None):
    cor = COR_DECISAO[metricas["decisao"]]
    regras = "".join(f"<li>{_e(r)}</li>" for r in REGRAS)
    cards = [("Testes executados", metricas["total"]), ("Aprovados (PASS)", metricas["aprovados"]),
             ("Reprovados (FAIL)", metricas["reprovados"]),
             ("Taxa de aprovação", f"{metricas['taxa_aprovacao']}%"),
             ("Falhas críticas", metricas["criticas"])]
    resumo = "".join(f"<div class='card'><span>{a}</span><b>{b}</b></div>" for a, b in cards)
    extra = _comparacao(comparacao["antes"], comparacao["depois"], comparacao["modo"]) if comparacao else ""
    pagina = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatório de QA - Estacionamento</title>
<style>
  body {{ font-family: system-ui, "Segoe UI", Arial, sans-serif; font-size: 15px; line-height: 1.4;
         color: #1a1a1a; background: #fff; margin: 0 auto; max-width: 1100px; padding: 24px 16px; }}
  h1 {{ font-size: 26px; font-weight: 700; margin: 0 0 4px; }}
  h2 {{ font-size: 19px; font-weight: 700; margin: 28px 0 10px; border-bottom: 2px solid #1a1a1a; padding-bottom: 4px; }}
  .meta {{ color: #444; margin: 0 0 16px; }}
  .decisao {{ border: 2px solid {cor}; color: {cor}; font-size: 22px; font-weight: 700; padding: 12px 16px; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; margin-top: 14px; }}
  .card {{ border: 1px solid #bbb; padding: 10px 12px; }}
  .card span {{ display: block; color: #444; font-size: 13px; font-weight: 600; }}
  .card b {{ font-size: 24px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
  th, td {{ border: 1px solid #bbb; padding: 6px 8px; text-align: left; vertical-align: top; }}
  th {{ background: #eee; font-weight: 700; }}
  tr.fail td {{ background: #fdecea; }}
  tr.pass .sit {{ color: #1b7a3a; font-weight: 700; }}
  tr.fail .sit {{ color: #b3261e; font-weight: 700; }}
  code {{ font-size: 13px; }}
  .comp {{ max-width: 640px; }}
  .tabela {{ overflow-x: auto; }}
</style></head><body>
<h1>Relatório de QA — Sistema de Estacionamento</h1>
<p class="meta">Versão testada: <strong>{_e(NOME_VERSAO.get(modo, modo))}</strong> · Executado em {_e(data_hora)}</p>
<div class="decisao">Decisão de QA: {_e(metricas['decisao'])}</div>
<div class="cards">{resumo}</div>
<h2>Funcionalidades e regras testadas</h2><ul>{regras}</ul>
<h2>Casos de teste</h2><div class="tabela">{_tabela_testes(resultados)}</div>
<h2>Defeitos encontrados</h2>{_defeitos(resultados)}
{extra}
<h2>Critério da decisão</h2>
<ul><li>Nenhuma falha: <strong>LIBERADO</strong>.</li>
<li>Falhas, mas nenhuma crítica: <strong>LIBERADO COM RESSALVAS</strong>.</li>
<li>Qualquer falha crítica: <strong>NÃO LIBERAR</strong>.</li></ul>
</body></html>"""
    caminho = os.path.join(PASTA, f"relatorio_{modo}.html")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(pagina)
    return caminho
