# Notifications setup (admin — one time)

When a skill gets a new version on `main`, the CI can notify the team on **Slack**, and
people can get **email** via GitHub. Here's how to turn each on.

## Slack (Incoming Webhook)

The CI posts a message listing the skills that just got a new release. It reads the
webhook URL from a repository **secret** — the URL never lives in the code.

1. Create the webhook in Slack:
   - https://api.slack.com/apps → **Create New App** → *From scratch* → pick the workspace.
   - **Incoming Webhooks** → toggle **On** → **Add New Webhook to Workspace** → choose the
     channel (e.g. `#vec-skills`) → **Allow**.
   - Copy the webhook URL (looks like `https://hooks.slack.com/services/…`).
2. Add it as a repo secret:
   - GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**.
   - Name: `SLACK_WEBHOOK_URL` · Value: the URL you copied → **Add secret**.
3. Done. On the next push that bumps a skill version, the channel gets a message like:
   > ✨ **VEC skills updated**
   > • text-reviewer v1.1.0
   > Get them in Claude → Plugins → Directory → Personal → ⋯ → Check for updates.

> If the secret isn't set, the CI simply skips the Slack step (no error).
> **Never paste the webhook URL into chat, code, or docs — only into the GitHub secret.**

## Email (Watch → Releases)

The CI already creates a GitHub **Release** per skill version. Anyone with access to the
repo can get an email automatically:

1. Open the repo on GitHub.
2. Click **Watch** (top right) → **Custom** → check **Releases** → **Apply**.

From then on, GitHub emails that person whenever a new release is published — no infra,
no credentials. It's opt-in per person and requires repo access.

> Want a fixed distribution list instead of opt-in? That needs an SMTP action with
> credentials stored as secrets — ask and we can add it.
