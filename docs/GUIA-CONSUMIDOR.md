# Guia do consumidor — Skills da VEC no Claude (app desktop)

Este guia é para **quem vai usar** as skills compartilhadas da VEC (não para quem cria).
Ele cobre duas coisas: **instalar pela primeira vez** e **receber atualizações** depois.

> Vale para o **app desktop do Claude** — o que o time usa. Quem usa o Claude Code no
> terminal tem um fluxo diferente (ver o final).

---

## Pré-requisito (uma vez)

Você precisa de **acesso de leitura** ao repositório `rafaelnetovec/claude-skills` (privado):

- Peça ao responsável para te adicionar como **colaborador** e **aceite o convite**
  (o GitHub manda por e-mail, ou acesse `https://github.com/rafaelnetovec/claude-skills/invitations`).
- Sem aceitar o convite, o Claude não consegue enxergar o repositório.

---

## Parte 1 — Instalar pela primeira vez

1. Abra o **Claude** (app desktop) → **Configurações** → **Plugins**.
2. Clique em **Adicionar** (ou no **"+"** dentro do **Diretório**).
3. Escolha adicionar um marketplace **do GitHub** e informe:
   ```
   rafaelnetovec/claude-skills
   ```
4. Se pedir para **conectar/autorizar o GitHub**, siga o fluxo (entre com a conta que
   tem acesso ao repositório).
5. Abra o plugin **"Vec skills"** e confirme que ele instalou. As skills aparecem como
   habilidades (ex.: `/exemplo-vec`, `/revisor-pt`).

Pronto — as skills já podem ser usadas (digitando `/` no chat ou deixando o Claude
usá-las automaticamente).

---

## Parte 2 — Receber atualizações (quando sai skill nova ou versão nova)

O app **não** atualiza sozinho por padrão. Quando o time publicar novidades, faça o
**refresh manual** (leva 1 clique):

1. Vá em **Plugins → Diretório → aba "Pessoal"**.
2. No marketplace **`claude-skills`**, clique no menu **"..."**.
3. Clique em **"Verificar atualizações"**.
4. Reabra a skill (ou o app). As skills novas / versões novas aparecem.

> ⚠️ **Reinstalar o plugin NÃO atualiza** — ele usa uma cópia em cache. A atualização
> só vem pelo **"Verificar atualizações"** no menu do **marketplace** (passos acima).

### (Opcional) Atualização automática

No mesmo menu **"..."** existe o toggle **"Sincronizar automaticamente"**. Com ele
ligado, o app passa a buscar atualizações sozinho.

- **Requisito:** o **Claude GitHub App** precisa ter acesso ao repositório. Enquanto o
  repo estiver numa conta pessoal privada, isso depende de configuração do dono
  (ou da migração do repo para uma organização). Enquanto isso não estiver liberado,
  use o **"Verificar atualizações"** manual da Parte 2.

---

## Como saber que deu certo

- Digite `/exemplo-vec` → deve responder o health-check.
- Digite `/revisor-pt` com um texto → deve revisar.

---

## Resumo rápido

| Ação | Onde | Frequência |
|---|---|---|
| Aceitar convite de colaborador | GitHub | 1× |
| Adicionar o marketplace `rafaelnetovec/claude-skills` | Plugins → Adicionar | 1× |
| **Atualizar** as skills | Plugins → Diretório → Pessoal → "..." → **Verificar atualizações** | sempre que avisarem |

---

## Para quem usa o Claude Code (terminal) — alternativo

O time em geral usa o app desktop (acima). Quem usa o **Claude Code no terminal** assina
o marketplace pelo `~/.claude/settings.json` (`extraKnownMarketplaces` + `enabledPlugins`)
e, por ser repo privado, precisa de um **token classic** do GitHub (`GH_TOKEN`) com escopo
`repo`. Nesse ambiente existe refresh de verdade (`claude plugin marketplace update`).
Peça o passo a passo específico se for o seu caso.
