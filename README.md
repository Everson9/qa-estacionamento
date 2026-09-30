# QA — Sistema de Estacionamento

Projeto de Garantia da Qualidade em Python: um sistema pequeno de estacionamento, 12 casos de
teste automatizados, métricas de qualidade, decisão de QA e relatório gerado sozinho a cada execução.

Não precisa instalar nada além do Python 3 (só biblioteca padrão).

## Como rodar no VS Code

Abra a pasta `qa-estacionamento` no VS Code e, no terminal integrado:

```
python main.py                  # versão correta
python main.py --bug critico    # liga o bug proposital crítico
python main.py --bug leve       # liga o bug proposital leve
python main.py --comparar       # roda as duas versões e compara
```

Também dá para rodar pelo botão Executar (F5): as quatro opções já estão em `.vscode/launch.json`.

Cada execução grava em `relatorios/`:

- `relatorio_<versão>.html` — relatório final de qualidade (abrir no navegador);
- `resultados_<versão>.csv` — todos os testes, um por linha (abre no Excel);
- `historico_execucoes.csv` — uma linha por execução, para acompanhar as versões.

## O sistema e as regras de negócio

| Regra | O que diz |
|---|---|
| RN01 - Entrada | Só entra placa válida (antiga ABC-1234 ou Mercosul ABC1D23) que ainda não esteja dentro. |
| RN02 - Lotação | Com todas as vagas ocupadas, ninguém entra. |
| RN03 - Cobrança | Até 15 min é grátis; 1ª hora R$ 8,00; cada hora adicional ou fração R$ 4,00; teto R$ 40,00. |
| RN04 - Saída | Só sai quem está dentro, e a vaga volta a ficar livre. |
| RN05 - Mensalista | Placa de mensalista não paga. |

## Casos de teste

| ID | Regra | Teste | Tipo | Severidade se falhar |
|---|---|---|---|---|
| CT01 | RN01 | Placa antiga entra | normal | ALTA |
| CT02 | RN01 | Placa Mercosul entra | normal | ALTA |
| CT03 | RN01 | Placa inválida é recusada com o motivo | erro | BAIXA |
| CT04 | RN01 | Mesma placa não entra duas vezes | erro | CRÍTICA |
| CT05 | RN02 | Estacionamento lotado recusa entrada | erro | CRÍTICA |
| CT06 | RN03 | 15 min (tolerância) não paga | limite | MÉDIA |
| CT07 | RN03 | Exatamente 1 h paga R$ 8,00 | limite | CRÍTICA |
| CT08 | RN03 | 1h30 paga R$ 12,00 (fração vira hora) | normal | CRÍTICA |
| CT09 | RN03 | 12 h para no teto de R$ 40,00 | limite | CRÍTICA |
| CT10 | RN04 | Saída após 2h10 cobra R$ 16,00 e libera vaga | normal | CRÍTICA |
| CT11 | RN04 | Saída de placa que não entrou é recusada | erro | ALTA |
| CT12 | RN05 | Mensalista não paga | normal | ALTA |

Critério de severidade: **CRÍTICA** mexe com dinheiro ou deixa entrar quem não pode; **ALTA** quebra
uma funcionalidade principal; **MÉDIA** confunde o usuário; **BAIXA** é detalhe de texto.

## Decisão de QA

- nenhuma falha: **LIBERADO**
- falhas, mas nenhuma crítica: **LIBERADO COM RESSALVAS**
- qualquer falha crítica: **NÃO LIBERAR**

## Bug proposital

Os dois bugs ficam no próprio código do sistema (`sistema/estacionamento.py`) e são ligados pela
variável `BUG`:

- **crítico** — em `calcular_valor`, a hora adicional passa a ser calculada com `minutos_extras // 60`,
  que joga fora a fração de hora. Quem fica 1h30 paga R$ 8,00 em vez de R$ 12,00.
- **leve** — a mensagem de placa inválida perde o motivo e diz só "Entrada recusada".

| | Versão correta | Bug leve | Bug crítico |
|---|---|---|---|
| PASS / FAIL | 12 / 0 | 11 / 1 | 10 / 2 |
| Taxa de aprovação | 100% | 91,7% | 83,3% |
| Falhas críticas | 0 | 0 | 2 |
| Decisão | LIBERADO | LIBERADO COM RESSALVAS | NÃO LIBERAR |
| Testes que pegaram | — | CT03 | CT08, CT10 |

O CT09 (12 horas) continua passando com o bug crítico, porque o teto da diária esconde o erro.
É um bom exemplo de por que um teste só não basta.

## Estrutura

```
main.py                   executa tudo e mostra o resultado no terminal
sistema/estacionamento.py sistema testado (regras de negócio + bugs propositais)
qa/casos.py               os 12 casos de teste
qa/execucao.py            executa, calcula métricas e decide
qa/relatorio.py           gera HTML, CSV e histórico
```

Fluxo: Requisito → Teste → Execução → Resultado → Dados → Identificação de Defeitos → Decisão de QA → Relatório.
