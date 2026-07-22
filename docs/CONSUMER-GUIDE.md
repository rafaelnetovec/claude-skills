# Consumer guide — VEC skills in Claude (desktop app)

This guide is for people who **use** the shared VEC skills (not for those who create them).
It covers two things: **installing for the first time** and **getting updates** afterward.

> This is for the **Claude desktop app** — what the team uses. People using Claude Code
> in the terminal have a different flow (see the end).

---

## Prerequisite (one time)

You need **read access** to the private repository `rafaelnetovec/claude-skills`:

- Ask the owner to add you as a **collaborator** and **accept the invite**
  (GitHub emails it, or open `https://github.com/rafaelnetovec/claude-skills/invitations`).
- Without accepting the invite, Claude cannot see the private repository.

---

## Part 1 — Install for the first time

1. Open **Claude** (desktop app) → **Settings** → **Plugins**.
2. Click **Add** (or the **"+"** inside the **Directory**).
3. Choose to add a marketplace **from GitHub** and enter:
   ```
   rafaelnetovec/claude-skills
   ```
4. If prompted, **connect/authorize GitHub** (sign in with the account that has access
   to the repository).
5. Open the **"Vec skills"** plugin and confirm it installed. Skills show up as
   abilities, e.g. `/vec-example`, `/text-reviewer`.

Done — the skills are ready to use (type `/` in the chat, or let Claude use them
automatically).

---

## Part 2 — Getting updates (when a new skill or version ships)

The app does **not** update on its own by default. When the team publishes something new,
do a **manual refresh** (one click):

1. Go to **Plugins → Directory → "Personal" tab**.
2. On the **`claude-skills`** marketplace, click the **"..."** menu.
3. Click **"Check for updates"**.
4. Reopen the skill (or the app). New skills / new versions appear.

> ⚠️ **Gotcha:** reinstalling the *plugin* does NOT update it — it uses a cached copy.
> Updates only arrive via **"Check for updates"** on the **marketplace** menu (steps above).

### (Optional) Automatic updates

The same **"..."** menu has a **"Sync automatically"** toggle. With it on, the app
fetches updates on its own.

- **Requirement:** the **Claude GitHub App** must have access to the repository. While the
  repo lives in a private personal account, this depends on the owner's configuration (or
  moving the repo to an organization). Until that's enabled, use the manual
  **"Check for updates"** from Part 2.

---

## How to know it worked

- Type `/vec-example` → it should reply with the health-check.
- Type `/text-reviewer` with some text → it should review it.

---

## Quick summary

| Action | Where | Frequency |
|---|---|---|
| Accept collaborator invite | GitHub | once |
| Add the `rafaelnetovec/claude-skills` marketplace | Plugins → Add | once |
| **Update** the skills | Plugins → Directory → Personal → "..." → **Check for updates** | whenever notified |

---

## Stay notified when skills change

- **Slack:** join the team channel where the SkillHub bot posts updates (e.g. `#vec-skills`).
  Whenever a skill gets a new version, it posts what changed.
- **Email:** on the repo, click **Watch → Custom → Releases → Apply**. GitHub will email you
  whenever a new skill version is released.

---

## For Claude Code (terminal) users — alternative

Most of the team uses the desktop app (above). People using **Claude Code in the terminal**
subscribe to the marketplace via `~/.claude/settings.json` (`extraKnownMarketplaces` +
`enabledPlugins`) and, since the repo is private, need a **classic GitHub token**
(`GH_TOKEN`) with the `repo` scope. That environment has a real refresh
(`claude plugin marketplace update`). Ask for the specific steps if that's your case.
