# Escritório Cível — plugin multi-agente para Claude Code

Equipe de agentes especialistas para um escritório de advocacia cível brasileiro:

| Agente | Função |
|---|---|
| `triagem-civel` | Ficha do caso: fatos, cronologia, documentos, prescrição, competência, viabilidade |
| `pesquisador-juridico` | Legislação, súmulas e precedentes, com selo `[CONFIRMADO]`/`[CONHECIDO]`/`[VERIFICAR]` |
| `estrategista-processual` | Teses, pedidos, tutela, valor da causa, riscos |
| `redator-pecas` | Minuta da peça (inicial, contestação, réplica, apelação, agravo, embargos…) |
| `analista-contratos` | Riscos de cláusulas e redação substitutiva |
| `revisor-critico` | Revisão como juiz e como parte contrária |
| `controlador-prazos` | Prazos em dias úteis com memória de cálculo |

A skill `escritorio-civel` coordena a equipe e entrega o resultado em Word (.docx).

## Instalação

**Como plugin (recomendado)** — dentro do Claude Code:

```
/plugin marketplace add brnmadeira/skill-advocacia
/plugin install escritorio-civel@skill-advocacia
```

**Manual (sem plugin)** — copie para a sua pasta pessoal do Claude Code:

```bash
git clone https://github.com/brnmadeira/skill-advocacia.git
mkdir -p ~/.claude/skills ~/.claude/agents
cp -r skill-advocacia/skills/escritorio-civel ~/.claude/skills/
cp skill-advocacia/agents/*.md ~/.claude/agents/
```

Requisito: Python 3 com `python-docx` (`pip install python-docx`) para gerar o .docx.

## Uso

Basta pedir em linguagem natural, por exemplo:

- "Faz uma contestação para este processo" (anexando a inicial)
- "Esse contrato de locação tem problema?"
- "A sentença saiu no DJEN em 18/11, até quando posso apelar?"

Os arquivos de cada caso ficam em `casos/AAAA-MM-DD-<cliente>/` no diretório em que você estiver.

## Aviso

Tudo o que a equipe produz é **minuta para revisão de advogado**. Citações marcadas `[VERIFICAR]`
precisam ser conferidas em fonte oficial antes do protocolo, e prazos dependem do calendário do
tribunal (feriados locais e portarias não são conhecidos pelo script).
