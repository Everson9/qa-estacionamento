"""Executa os casos de teste, calcula as métricas e toma a decisão de QA."""
import time

from qa.casos import CASOS


def executar_testes():
    resultados = []
    for caso in CASOS:
        inicio = time.perf_counter()
        try:
            obtido = str(caso["executar"]())
        except Exception as erro:  # erro inesperado também é resultado de teste
            obtido = f"EXCEÇÃO: {type(erro).__name__}: {erro}"
        duracao_ms = (time.perf_counter() - inicio) * 1000
        passou = obtido == caso["esperado"]
        resultados.append({
            "id": caso["id"],
            "requisito": caso["requisito"],
            "descricao": caso["descricao"],
            "esperado": caso["esperado"],
            "obtido": obtido,
            "situacao": "PASS" if passou else "FAIL",
            "severidade": "-" if passou else caso["severidade"],
            "duracao_ms": round(duracao_ms, 2),
        })
    return resultados


def calcular_metricas(resultados):
    total = len(resultados)
    aprovados = sum(r["situacao"] == "PASS" for r in resultados)
    falhas = [r for r in resultados if r["situacao"] == "FAIL"]
    criticas = sum(r["severidade"] == "CRÍTICA" for r in falhas)
    return {
        "total": total,
        "aprovados": aprovados,
        "reprovados": len(falhas),
        "taxa_aprovacao": round(aprovados / total * 100, 1) if total else 0.0,
        "criticas": criticas,
        "decisao": decidir(len(falhas), criticas),
    }


def decidir(reprovados, criticas):
    """Regra de liberação da versão."""
    if criticas > 0:
        return "NÃO LIBERAR"
    if reprovados > 0:
        return "LIBERADO COM RESSALVAS"
    return "LIBERADO"
