"""Sistema de estacionamento — o software que está sendo testado.

Regras de negócio:
  RN01 - Entrada: só entra veículo com placa válida (padrão antigo ABC-1234
         ou Mercosul ABC1D23) e que ainda não esteja dentro.
  RN02 - Lotação: com todas as vagas ocupadas, nenhum veículo entra.
  RN03 - Cobrança: até 15 min é grátis; a 1ª hora custa R$ 8,00; cada hora
         adicional (ou fração) custa R$ 4,00; o valor máximo é a diária de R$ 40,00.
  RN04 - Saída: só sai veículo que está dentro, e a vaga fica livre de novo.
  RN05 - Mensalista: placa cadastrada como mensalista não paga.
"""
import re

REGRAS = [
    "RN01 - Entrada: só entra veículo com placa válida (padrão antigo ABC-1234 ou Mercosul ABC1D23) que ainda não esteja dentro.",
    "RN02 - Lotação: com todas as vagas ocupadas, nenhum veículo entra.",
    "RN03 - Cobrança: até 15 min é grátis; a 1ª hora custa R$ 8,00; cada hora adicional (ou fração) custa R$ 4,00; teto da diária R$ 40,00.",
    "RN04 - Saída: só sai veículo que está dentro, e a vaga fica livre de novo.",
    "RN05 - Mensalista: placa cadastrada como mensalista não paga.",
]

TOLERANCIA_MIN = 15
PRIMEIRA_HORA = 8.00
HORA_ADICIONAL = 4.00
DIARIA_MAXIMA = 40.00

PLACA_ANTIGA = re.compile(r"^[A-Z]{3}-\d{4}$")
PLACA_MERCOSUL = re.compile(r"^[A-Z]{3}\d[A-Z]\d{2}$")

# Bug proposital, ligado pelo main.py (--bug critico / --bug leve).
#   "critico": a cobrança esquece a fração de hora (cobra menos do que deve).
#   "leve":    a mensagem de erro de placa inválida sai sem o motivo.
BUG = None


class ErroEstacionamento(Exception):
    """Erro de regra de negócio (entrada recusada, saída inválida...)."""


def placa_valida(placa):
    placa = placa.strip().upper()
    return bool(PLACA_ANTIGA.match(placa) or PLACA_MERCOSUL.match(placa))


def calcular_valor(minutos, mensalista=False):
    """RN03 e RN05: valor a pagar por uma permanência em minutos."""
    if minutos < 0:
        raise ErroEstacionamento("Tempo de permanência negativo")
    if mensalista or minutos <= TOLERANCIA_MIN:
        return 0.0
    if minutos <= 60:
        return PRIMEIRA_HORA
    minutos_extras = minutos - 60
    if BUG == "critico":
        horas_extras = minutos_extras // 60  # BUG: ignora a fração de hora
    else:
        horas_extras = -(-minutos_extras // 60)  # arredonda a fração para cima
    valor = PRIMEIRA_HORA + horas_extras * HORA_ADICIONAL
    return min(valor, DIARIA_MAXIMA)


class Estacionamento:
    def __init__(self, vagas, mensalistas=()):
        self.vagas = vagas
        self.mensalistas = {p.upper() for p in mensalistas}
        self.dentro = {}  # placa -> minuto de entrada

    @property
    def vagas_livres(self):
        return self.vagas - len(self.dentro)

    def registrar_entrada(self, placa, minuto):
        """RN01 e RN02."""
        placa = placa.strip().upper()
        if not placa_valida(placa):
            if BUG == "leve":
                raise ErroEstacionamento("Entrada recusada")  # BUG: sem o motivo
            raise ErroEstacionamento(f"Placa inválida: {placa}")
        if placa in self.dentro:
            raise ErroEstacionamento(f"Veículo {placa} já está no estacionamento")
        if self.vagas_livres == 0:
            raise ErroEstacionamento("Estacionamento lotado")
        self.dentro[placa] = minuto

    def registrar_saida(self, placa, minuto):
        """RN04: devolve o valor a pagar e libera a vaga."""
        placa = placa.strip().upper()
        if placa not in self.dentro:
            raise ErroEstacionamento(f"Veículo {placa} não está no estacionamento")
        entrada = self.dentro.pop(placa)
        return calcular_valor(minuto - entrada, placa in self.mensalistas)
