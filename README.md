# The Replica skill

Eleven skills that clone any app, plus a twelfth that indexes them. Free, MIT,
no signup, no API key, nothing to connect.

One reverse-engineers the app you want to clone. One rebuilds it. One tests it
for bugs. And one is the Entrepreneur: it reads what the app's users hate and
fixes it in yours, so you have an app you can sell.

In between, the others plan the stack and the database, rebuild the design
system, wire up auth and payments, score your clone against the original, give
it a name and a brand of its own, write the landing page and the store
listing, and put it live on your domain.

**It rebuilds what an app does, never what it owns.** Features and flows,
clean-room style. Not its code, its logo, its copy or its content. The
fine print is at the bottom, and the skills enforce it.

> **This fork** runs the pack in Freebuff as well as in Claude. Skills are
> invoked by name instead of by slash command, every template and tool stays in
> its own skill folder, `replica-pack` carries the order and the handoffs,
> `install.py` copies the pack into a skills folder the client reads, and
> `tools/check_skills.py` re-checks every skill against the client's own size
> and naming limits. Italian section: [Usare il pacchetto con
> Freebuff](#usare-il-pacchetto-con-freebuff).

## Install

### Freebuff

A skill is a folder with a `SKILL.md` in it and its templates and Python tools
beside it. For the thread it is running, Freebuff reads the folders of the
project it is working in: `<project>/.agents/skills/` or
`<project>/.claude/skills/` (`.agents` wins where both hold the same name).
The user-level folders, `~/.agents/skills/` and `~/.claude/skills/`, are the
ones a `-g` install writes, and this build does not advertise them to the model
in a thread: a pack installed only there stays out of the thread's context. To
have the skills picked up on their own, install into the project.

With the skills CLI, from anywhere:

```bash
npx skills add https://github.com/leoforti/ai-skill -g     # all twelve, every project
npx skills add leoforti/ai-skill --skill replica-pack      # one skill, this project
npx skills use leoforti/ai-skill@replica-pack              # print one as a prompt, install nothing
```

`-g` puts the pack in `~/.agents/skills/` and, as the CLI does for every agent
it knows, in the other agent directories too. Without `-g` it lands in
`./.agents/skills/` and the CLI writes a `skills-lock.json`, so
`npx skills update` works later.

Without Node, or when you want to touch only `~/.agents/skills/`:

```bash
git clone https://github.com/leoforti/ai-skill.git
cd ai-skill
python install.py                 # every project, then open a new thread
python install.py --project .     # or just this project
python install.py --dry-run       # what it would copy, copy nothing
python install.py --remove        # take it back out
```

Freebuff reads skills when a thread starts: open a new thread (or restart the
client) and the pack is there. The Discover tab searches the skills.sh
directory, not a URL, so it only offers what that directory has indexed; this
pack arrives in the folders above instead. Settings - Skills takes a skill by
hand as well (Name, Description, Instructions; the limits are a name matching
`^[a-z0-9][a-z0-9-]{0,63}$`, a description of at most 1000 characters and
instructions of at most 50000), and a skill created that way has no sibling
files, so paste the templates it needs into the instructions.

Run the tools with `python` on Windows and `python3` on macOS and Linux:

```bash
python tools/check_skills.py      # every skill against the client's limits
python -m unittest discover -s tests -v
```

### Claude

Paste this into Claude:

```
https://github.com/Jakeschincariol/replica-skill

install skill
```

Or as a plugin, in Claude Code:

```
/plugin marketplace add Jakeschincariol/replica-skill
/plugin install replica-skill@replica-skill
```

Claude Code namespaces plugin skills, so installed as a plugin they show up as
`/replica-skill:replica-recon` and so on. Copy the folders instead if you want
plain `/replica-recon`:

```bash
git clone https://github.com/Jakeschincariol/replica-skill.git
cp -r replica-skill/replica-* ~/.claude/skills/
```

Project-local instead of global: copy the same folders into your repo's
`.claude/skills/`. No Claude Code at all? Paste any single `SKILL.md` at the
top of a chat and it runs as a mode. You lose the Python tools, but the
method works.

The tools need Python 3.8 or newer. Nothing to pip install.

## The twelve

| skill | what it does |
| --- | --- |
| `replica-pack` | The index: the order, who writes and who reads what in `replica/`, and the rules that hold across the whole pack. |
| `replica-recon` | Reverse-engineers any app: screens, flows, components, data model. From public pages, screenshots, store listings and your own account. |
| `replica-architect` | Plans the stack, database schema and API for your clone. |
| `replica-design` | Rebuilds the design system: colours, type, spacing, components. As tokens, with your own assets. |
| `replica-build` | Rebuilds the app screen by screen from the recon map. |
| `replica-backend` | Auth, database, payments and integrations. |
| `replica-test` | Clicks through every flow and tests it for bugs. |
| `replica-diff` | Compares your clone against the original. A parity score and what is missing. |
| `replica-entrepreneur` | Reads what the app's users hate in real reviews and turns it into fixes and a positioning angle. |
| `replica-brand` | Names and rebrands your version so it is yours. |
| `replica-launch` | Landing page, pricing and App Store listing. |
| `replica-deploy` | Ships it live on your own domain. |

In Claude Code those are `/replica-recon` and so on; in Freebuff you ask for
them by name, and `replica-pack` tells you which one comes next.

## How to use it

Run them in order. Each one reads what the last one wrote, in a `replica/`
folder in your project. The handoff is you saying "next": no skill runs another
on its own.

```
recon -> architect -> design -> build -> backend -> test -> diff -> entrepreneur -> brand -> launch -> deploy
```

An example: cloning a scheduling app, the kind where you share a link and
people book a time with you.

1. **replica-recon** with the app's URL. It reads the help center, the
   pricing page, the store listing and public walkthroughs, and you click
   through your own account with it. Out comes `replica/recon.md`: 18
   screens, 7 flows (guest books a meeting, host sets availability, guest
   reschedules...), the components, an inferred data model (users, event
   types, availability, bookings) and `features.csv`. The partner
   marketplace is marked out of scope: that is their network, not a feature.
2. **replica-architect** picks Next.js, Postgres, Stripe and Resend, writes
   the schema (with a constraint so two guests can never book the same slot)
   and orders the build: the booking flow end to end first.
3. **replica-design** measures the screenshots into tokens: colour roles,
   type scale, 8px spacing, the date picker and slot button specs. Open
   icons, an open font, your own words.
4. **replica-build** builds the shell, then the booking flow, then every
   screen with all its states, ticking off `features.csv` as it goes.
5. **replica-backend** adds sign up, Google Calendar through Google's own
   API with your keys, Stripe for paid bookings, reminder emails.
6. **replica-test** writes a test plan from the 7 flows, Playwright specs
   for the happy paths and edge cases (time zones, a slot taken mid-booking,
   double submit), and logs bugs by severity until no S1 or S2 is open.
7. **replica-diff** scores it. Features 86, all must-haves done, booking
   page layout 91. Missing: round-robin for teams, the website embed.
8. **replica-entrepreneur** reads 140 real reviews across the App Store,
   G2, Capterra and Reddit. Top complaints: per-seat price jumps, no text
   reminders, guests confused by time zones. Each with counts and linked
   quotes. Fix plan: flat pricing, SMS reminders, a time zone confirm step.
   Angle: booking links for small teams that hate per-seat pricing.
9. **replica-brand** names it (with the trademark and domain checks to
   run), gives it a new palette, a logo brief and a voice, then sweeps the
   codebase until nothing of the original is left.
10. **replica-launch** writes the landing page around the angle, sets
    pricing against the original's public page, and lints the store listing.
11. **replica-deploy** runs the preflight (tests, parity, sweep, listing),
    sets up production, gives you the DNS records for your domain, and ships
    it when you say go.

You can also run any one on its own. **replica-entrepreneur** on an app you
are only thinking about cloning is a good way to find out if you should.

## The tools

Six of them, all standard-library Python. None touch the network.

```bash
python replica-diff/imgdiff.py original.png clone.png --out diff.png   # layout diff, ignores colour
python replica-diff/parity.py replica/features.csv                     # parity score + missing list
python replica-entrepreneur/reviews.py replica/reviews.csv             # what users hate, ranked, linked
python replica-design/contrast.py replica/design/tokens.json           # WCAG contrast on your tokens
python replica-brand/sweep.py . --avoid "Original App"                 # anything of the original left?
python replica-launch/listing.py replica/launch/listing.json           # store limits + copycat checks
```

On macOS and Linux the binary is usually `python3`; the commands above work
either way, and inside a skill the tools are called relative to that skill's
own folder.

**`imgdiff.py`** reads PNGs with no libraries, turns both screenshots into
edge maps and compares where things are, so your new colours do not count
against you. It tells you which regions differ, in the original's pixels.

**`parity.py`** weights must, should and could, counts partial as half, and
never scores what you left out on purpose or what you added. Missing
must-haves means not shippable, and it says so.

**`reviews.py`** drops every review without a link. Every quote it prints is
copied from a row you gave it, with that row's URL. Themes with under three
reviews or one source are marked thin.

**`sweep.py`** finds the original's name, domain and colours anywhere in your
code, including inside identifiers like `OriginalAppEmbed`, and blocks the
deploy until it is clean.

**`listing.py`** checks App Store and Google Play limits, ranking claims in
the title, wasted keyword characters, and the original's name anywhere in
your listing.

```bash
python -m unittest discover -s tests -v
python tools/check_skills.py             # this fork: the skills against the client's limits
python install.py --dry-run              # this fork: what an install would copy
```

## Fine print

**It rebuilds functionality and UX patterns, clean-room style.** It studies
what the app does and how people move through it, then writes everything
fresh. It never copies the target's source code, proprietary assets, logos,
trademarks, copy or private APIs.

**It only reads what you are allowed to read.** Public pages and your own
account. It never scrapes behind a login or against a site's terms, never
logs into anyone else's account, and never gets past a paywall. If your
account's terms forbid using it to build a competitor, it says so and sticks
to public sources.

**It always rebrands before launch.** New name, new palette, new logo, new
words. **replica-deploy** will not ship until the sweep is clean.

**"Clone any app" means the features and the flow.** Not the content, the
network or the licences an app owns. You can rebuild a music app's player,
playlists and sharing. You cannot clone its catalogue.

**No guarantee of a "perfect" clone.** Results depend on how complex the app
is. A booking tool is weeks. A spreadsheet engine is not. **replica-recon**
sizes it honestly before you start, and **replica-diff** gives you a real
number, not a vibe.

**The Entrepreneur never makes things up.** No invented reviews, quotes or
numbers. Every claim has a link, and the sample size is stated.

**Check before you sell.** Run the trademark checks **replica-brand** lists,
read the terms of anything you used, and talk to a lawyer before launch if
there is money on the line. This is not legal advice.

## Files

```
replica-pack/          SKILL.md (the index and the handoffs)
replica-recon/         SKILL.md, recon-map.md, features.csv (the matrix template)
replica-architect/     SKILL.md, architecture.md
replica-design/        SKILL.md, tokens.json, contrast.py
replica-build/         SKILL.md
replica-backend/       SKILL.md
replica-test/          SKILL.md, test-plan.md, bug-report.md, e2e.example.spec.ts
replica-diff/          SKILL.md, imgdiff.py, parity.py
replica-entrepreneur/  SKILL.md, reviews.py, themes.json
replica-brand/         SKILL.md, sweep.py
replica-launch/        SKILL.md, listing.py, listing.example.json
replica-deploy/        SKILL.md, preflight.md
install.py             this fork: copies the pack into a skills folder
tools/                 this fork: check_skills.py, the limit checker
tests/                 the tests for every tool
```

Your own files live in `replica/` in your project. The skills read each
other's.

## Usare il pacchetto con Freebuff

Freebuff non ha gli slash command: una skill si chiama per nome, e il client la
trova dalla cartella in cui sta. Ogni cartella `replica-*/` di questo repo è
una skill intera: `SKILL.md` più i suoi template e i suoi tool.

Installazione, con il CLI ufficiale delle skill (serve Node):

```bash
npx skills add https://github.com/leoforti/ai-skill -g    # dodici skill, per tutti i progetti
npx skills add leoforti/ai-skill --skill replica-pack     # una sola, in questo progetto
npx skills use leoforti/ai-skill@replica-pack             # stampa la skill da incollare, senza installare
```

Senza Node, o se vuoi toccare solo `~/.agents/skills/`:

```bash
git clone https://github.com/leoforti/ai-skill.git
cd ai-skill
python install.py                 # copia in ~/.agents/skills, per tutti i progetti
python install.py --project .     # oppure solo nel progetto in cui sei
python install.py --list          # cosa c'è già dentro
python install.py --remove        # per togliere tutto
```

`install.py` copia ogni cartella `replica-*` in una cartella che il client
legge. Attenzione a quale: il thread legge le cartelle del **progetto** su cui
sta lavorando, `<progetto>/.agents/skills/` o `<progetto>/.claude/skills/`, e
quelle le legge sempre. Le cartelle utente, `~/.agents/skills/` (quella che
scrive `-g`) e `~/.claude/skills/`, in questa build non vengono annunciate al
modello dentro un thread: un pacchetto installato solo lì resta fuori dal
contesto. Per farsele trovare da sole, installa nel progetto; le skill si
leggono all'apertura di un thread, quindi dopo l'installazione aprine uno
nuovo e le richiami per nome (`replica-recon`, `replica-diff`, ...).

Tre cose da sapere:

- **L'handoff è manuale.** Nessuna skill lancia la successiva. La mappa, con
  l'ordine e chi scrive e chi legge cosa in `replica/`, è `replica-pack`.
- **I tool girano con `python`.** Su Windows `python3` è lo stub del Microsoft
  Store che apre il negozio; `python` è l'interprete vero. Su macOS e Linux è
  il contrario.
- **Niente dipendenze.** I sei tool Python usano solo la libreria standard.

Se preferisci crearle a mano da Settings - Skills - Create, i limiti del client
sono: nome `^[a-z0-9][a-z0-9-]{0,63}$` che deve combaciare con la cartella,
descrizione fino a 1000 caratteri, istruzioni fino a 50000. Una skill creata
così non ha file accanto, quindi i template vanno incollati nel campo
Instructions invece che letti dalla cartella. `python tools/check_skills.py`
ricontrolla tutto dopo una modifica.

## Credit

Made by Jake Schincariol, [opusjake.ai](https://opusjake.ai). Siblings:
[Arena](https://github.com/Jakeschincariol/arena-skill),
[X](https://github.com/Jakeschincariol/x-agent-skill),
[LinkedIn](https://github.com/Jakeschincariol/linkedin-agent-skill),
[Instagram](https://github.com/Jakeschincariol/instagram-agent-skill).

## License

MIT. Take it, change it, ship it.
