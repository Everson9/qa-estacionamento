"""Casos de teste. Cada caso diz o que espera e devolve o que o sistema fez.

Severidade (vale quando o teste falha):
  CRÍTICA - dinheiro errado ou regra de segurança quebrada: não pode ir para produção.
  ALTA    - funcionalidade principal não funciona, mas não causa prejuízo direto.
  MÉDIA   - funciona, mas de um jeito que confunde o usuário.
  BAIXA   - detalhe de texto ou apresentação.
"""
from sistema.estacionamento import ErroEstacionamento, Estacionamento, calcular_valor


def tentar(acao):
    """Executa a ação e devolve o resultado, ou a mensagem de erro do sistema."""
    try:
        return acao()
    except ErroEstacionamento as erro:
        return f"ERRO: {erro}"


def reais(valor):
    return f"R$ {valor:.2f}"


def ct01():
    e = Estacionamento(vagas=5)
    e.registrar_entrada("ABC-1234", 0)
    return f"entrou, vagas livres: {e.vagas_livres}"


def ct02():
    e = Estacionamento(vagas=5)
    e.registrar_entrada("BRA2E19", 0)
    return f"entrou, vagas livres: {e.vagas_livres}"


def ct03():
    e = Estacionamento(vagas=5)
    return tentar(lambda: e.registrar_entrada("12-ABCD", 0))


def ct04():
    e = Estacionamento(vagas=5)
    e.registrar_entrada("ABC-1234", 0)
    return tentar(lambda: e.registrar_entrada("ABC-1234", 10))


def ct05():
    e = Estacionamento(vagas=2)
    e.registrar_entrada("AAA-1111", 0)
    e.registrar_entrada("BBB-2222", 0)
    return tentar(lambda: e.registrar_entrada("CCC-3333", 0))


def ct06():
    return reais(calcular_valor(15))


def ct07():
    return reais(calcular_valor(60))


def ct08():
    return reais(calcular_valor(90))


def ct09():
    return reais(calcular_valor(12 * 60))


def ct10():
    e = Estacionamento(vagas=1)
    e.registrar_entrada("ABC-1234", 0)
    valor = e.registrar_saida("ABC-1234", 130)
    return f"pagou {reais(valor)}, vagas livres: {e.vagas_livres}"


def ct11():
    e = Estacionamento(vagas=5)
    return tentar(lambda: e.registrar_saida("XYZ-9999", 30))


def ct12():
    e = Estacionamento(vagas=5, mensalistas=["BRA2E19"])
    e.registrar_entrada("BRA2E19", 0)
    return reais(e.registrar_saida("BRA2E19", 300))


CASOS = [
    {"id": "CT01", "requisito": "RN01 - Entrada", "severidade": "ALTA", "executar": ct01,
     "descricao": "Entrada de carro com placa no padrão antigo (ABC-1234)",
     "esperado": "entrou, vagas livres: 4"},
    {"id": "CT02", "requisito": "RN01 - Entrada", "severidade": "ALTA", "executar": ct02,
     "descricao": "Entrada de carro com placa Mercosul (BRA2E19)",
     "esperado": "entrou, vagas livres: 4"},
    {"id": "CT03", "requisito": "RN01 - Entrada", "severidade": "BAIXA", "executar": ct03,
     "descricao": "Placa fora de qualquer padrão é recusada e o motivo aparece",
     "esperado": "ERRO: Placa inválida: 12-ABCD"},
    {"id": "CT04", "requisito": "RN01 - Entrada", "severidade": "CRÍTICA", "executar": ct04,
     "descricao": "Mesma placa não pode entrar duas vezes",
     "esperado": "ERRO: Veículo ABC-1234 já está no estacionamento"},
    {"id": "CT05", "requisito": "RN02 - Lotação", "severidade": "CRÍTICA", "executar": ct05,
     "descricao": "Com as 2 vagas ocupadas, o 3º carro é recusado",
     "esperado": "ERRO: Estacionamento lotado"},
    {"id": "CT06", "requisito": "RN03 - Cobrança", "severidade": "MÉDIA", "executar": ct06,
     "descricao": "15 minutos (limite da tolerância) não paga",
     "esperado": "R$ 0.00"},
    {"id": "CT07", "requisito": "RN03 - Cobrança", "severidade": "CRÍTICA", "executar": ct07,
     "descricao": "Exatamente 1 hora paga só a primeira hora",
     "esperado": "R$ 8.00"},
    {"id": "CT08", "requisito": "RN03 - Cobrança", "severidade": "CRÍTICA", "executar": ct08,
     "descricao": "1h30 cobra a fração como hora cheia (8 + 4)",
     "esperado": "R$ 12.00"},
    {"id": "CT09", "requisito": "RN03 - Cobrança", "severidade": "CRÍTICA", "executar": ct09,
     "descricao": "12 horas para no teto da diária",
     "esperado": "R$ 40.00"},
    {"id": "CT10", "requisito": "RN04 - Saída", "severidade": "CRÍTICA", "executar": ct10,
     "descricao": "Saída após 2h10 cobra 3 horas e libera a vaga",
     "esperado": "pagou R$ 16.00, vagas livres: 1"},
    {"id": "CT11", "requisito": "RN04 - Saída", "severidade": "ALTA", "executar": ct11,
     "descricao": "Saída de placa que não entrou é recusada",
     "esperado": "ERRO: Veículo XYZ-9999 não está no estacionamento"},
    {"id": "CT12", "requisito": "RN05 - Mensalista", "severidade": "ALTA", "executar": ct12,
     "descricao": "Mensalista fica 5 horas e não paga",
     "esperado": "R$ 0.00"},
]
