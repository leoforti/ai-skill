---
name: replica-pack
description: >-
  The map of the Replica pack: what each of the twelve skills does, the order
  they run in, who writes and who reads what inside `replica/` in the user's
  project, and how to run any one of them on its own. Start here when the user
  wants to clone an app end to end, or asks which skill comes next. Use when
  the user says "clone this app" and means the whole process, "where do I
  start", "what's the order", "which skill do I run next". Trigger anche in
  italiano: 'clona questa app', 'da dove comincio', 'quale skill replica tocca
  adesso'.
---

> Freebuff note (added in this fork; the original is a Claude skill). There is
> no slash command here: this skill is invoked by name, and that name has to
> match the folder it sits in. Its support files travel with it, so copy or
> install the whole folder, never the SKILL.md alone. For Freebuff that folder
> is the first of these for a Discover install available to every project, the
> second when the pack is cloned into one project:
>
>     ~/.agents/skills/replica-pack/
>     <project>/.agents/skills/replica-pack/
>
> Run the Python tools with `python` on Windows, `python3` on macOS and Linux.
> The handoff between the twelve skills is manual: the order, and who writes
> and reads what, is in this skill. End this skill by naming the
> next one; never claim a later skill's output exists before it has run.

# replica-pack

The Replica pack is twelve skills that run in order. Each one reads what the
previous one wrote, in `replica/` inside the user's project. Print the table
below when the user asks where to start, then name the one skill that goes
first and stop.

| # | skill | writes | reads |
| --- | --- | --- | --- |
| 1 | replica-recon | replica/recon.md, replica/features.csv, replica/screens/ | nothing: public pages and the user's own account |
| 2 | replica-architect | replica/architecture.md, replica/schema.sql | recon.md, features.csv |
| 3 | replica-design | replica/design/tokens.json, tokens.css, components.md | recon.md, screenshots |
| 4 | replica-build | the app itself, replica/build-log.md | architecture.md, recon.md, features.csv |
| 5 | replica-backend | auth, database, payments, replica/backend.md | architecture.md |
| 6 | replica-test | replica/test-plan.md, replica/bugs.md, e2e/ | recon.md |
| 7 | replica-diff | replica/parity.md, replica/diffs/ | features.csv, clone screenshots |
| 8 | replica-entrepreneur | replica/feedback.md, replica/fixes.md | replica/reviews.csv (the user supplies it), features.csv |
| 9 | replica-brand | replica/brand.md, replica/brand.json | tokens.json, fixes.md |
| 10 | replica-launch | replica/launch/landing.md, pricing.md, listing.json | brand.md, brand.json, feedback.md, fixes.md |
| 11 | replica-deploy | the live site, replica/deploy/deploy.md | everything above, as the preflight |

Order: recon -> architect -> design -> build -> backend -> test -> diff ->
entrepreneur -> brand -> launch -> deploy.

The handoff is manual. At the end of a skill, say which skill comes next and
what it will read, then stop and wait. Never run the next skill on your own
initiative, and never claim a later skill's output exists when its file is not
in `replica/`. A skill whose input file is missing stops and names the earlier
skill that has to run first. Any skill also runs alone, if the user asks for
that one thing: recon on an app they are only thinking about, entrepreneur on a
market they are checking, brand on an app that already exists, and so on.

Three rules hold across the whole pack and are not relaxed anywhere:

1. **Public sources and the user's own account only.** No logging into someone
   else's account, no paywall tricks, no scraping behind a login.
2. **Clean room.** Rebuild functionality, flows and UX patterns. Never the
   original's code, assets, logo, copy, brand colour or private APIs.
3. **Rebrand before launch, and do not ship while the sweep reports the
   original's name, domain or colours.**

## Working in this client

- **Invoked by name.** Each skill is a folder with a `SKILL.md`; the `name` in
  its frontmatter has to match the folder. The description is what the client
  matches against what the user typed, which is why every one of them ends with
  Italian triggers.
- **Project install:** the pack cloned into a project still works when the
  folders sit in `<project>/.agents/skills/` or `<project>/.claude/skills/`
  (`.agents` wins where both exist). The client picks those up from the thread's
  workspace, and they are per-project, not per-account.
- **Personal install:** the client's Discover tab puts a skill in
  `~/.agents/skills/<name>/`, and `install.py` in this repo does the same copy
  by hand. Those are available in every project.
- **Account install:** Settings - Skills - Create takes Name, Description and
  Instructions as text. The limits there are a name matching
  `^[a-z0-9][a-z0-9-]{0,63}$`, a description of at most 1000 characters and
  instructions of at most 50000. A skill created that way has no sibling files,
  so any template it needs has to be pasted into the instructions instead of
  read from the folder.
- **Tools never install themselves.** Every Python tool in the pack is standard
  library only; nothing to pip install. On Windows the interpreter is `python`
  because `python3` is the Microsoft Store stub.

`tools/check_skills.py` in this repo re-checks every SKILL.md against those
limits; run it after editing a skill.

## Credit

Replica is MIT, by Jake Schincariol, [opusjake.ai](https://opusjake.ai). The
`replica-pack` skill itself is an addition in this fork.
