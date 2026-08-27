# brazilian-public-data-platform

## Agent skills

Skills de engenharia do [mattpocock/skills](https://github.com/mattpocock/skills)
estão instaladas em `.claude/skills/`.

### Issue tracker

Issues vivem no GitHub Issues de `jlfig13/brazilian-public-data-platform` (via `gh`, ou
via as ferramentas MCP do GitHub quando `gh` não estiver disponível).
Ver `docs/agents/issue-tracker.md`.

### Triage labels

Vocabulário padrão de cinco papéis: `needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`. Ver `docs/agents/triage-labels.md`.

### Domain docs

Single-context: um `CONTEXT.md` na raiz e ADRs em `docs/adr/`.
Ver `docs/agents/domain.md`.

### Slash commands

As skills com `disable-model-invocation: true` não são invocáveis pelo modelo e, em
alguns ambientes, também não viram slash command automaticamente. `.claude/commands/`
traz um wrapper para cada uma delas, de modo que `/implement`, `/to-spec`, `/triage`
e as demais funcionem. O wrapper apenas manda ler o `SKILL.md` correspondente — a
skill continua sendo a fonte da verdade.
