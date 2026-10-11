---
name: replica-build
description: >-
  Rebuilds an app screen by screen from the recon map: app shell first, then
  the core flow as a vertical slice, then every screen with all its states,
  ticking off the feature matrix as it goes. Writes every line fresh, never
  the original's code, assets or copy. Use when the user says "build the
  clone", "build screen S07", "start building", "rebuild this screen",
  "implement the booking page", or after the replica-design skill.
  Trigger anche in italiano: 'costruisci il clone', 'fai la schermata
  S07', 'inizia a costruire'.
---

> Freebuff note (added in this fork; the original is a Claude skill). There is
> no slash command here: this skill is invoked by name, and that name has to
> match the folder it sits in. Its support files travel with it, so copy or
> install the whole folder, never the SKILL.md alone. For Freebuff that folder
> is the first of these for a Discover install available to every project, the
> second when the pack is cloned into one project:
>
>     ~/.agents/skills/replica-build/
>     <project>/.agents/skills/replica-build/
>
> Run the Python tools with `python` on Windows, `python3` on macOS and Linux.
> The handoff between the eleven skills is manual: the order, and who writes
> and reads what, is in the `replica-pack` skill. End this skill by naming the
> next one; never claim a later skill's output exists before it has run.

# replica-build

Reads `replica/recon.md`, `replica/architecture.md`, `replica/design/`.
Updates `replica/features.csv` (the `clone` column) and keeps
`replica/build-log.md`.

## The rules

- **Clean room.** Every line of code is written here, from the recon map and
  the specs. Never paste the original's HTML, CSS, JavaScript, SVGs or
  images, never load anything from its domain or CDN, never "view source and
  adapt".
- **Your words.** Write every label, button, empty state and email fresh.
  Matching what a button does is parity. Matching its sentence is copying.
- **Tokens only.** No raw hex or pixel values in components. If a value is
  missing, add it to the tokens.

## Step 1: the shell

Routing for every screen in the inventory (stub pages are fine), the layout
(nav, header, sidebar), tokens wired in, the primitives from replica-design,
and seed data so screens have something real to show. Commit.

## Step 2: the vertical slice

The core loop from the recon map, end to end, before anything else. For a
booking app: create an event type, open the public page, book a slot, see it
on the dashboard. Ugly is fine. Working is the point. If replica-backend has
not run yet, use the seed data and a fake data layer with the same function
signatures, so swapping in the real one changes no screen code.

## Step 3: screen by screen

Work in the order of `architecture.md`. For each screen:

1. Read its row in the recon map: purpose, components, states, which flows
   pass through it.
2. Look at the reference screenshot for layout and hierarchy. Not for pixels.
3. Build it with the primitives. Real data from the data layer.
4. **Every state**: empty, loading (skeletons, not spinners, if the original
   does), filled, error, no permission, long content (a 60 character name),
   mobile width.
5. Basics, every time: semantic HTML, labels on inputs, keyboard reachable,
   visible focus, images with alt text.
6. Set the matching rows in `features.csv` to `yes` or `partial` (with a note).
7. Screenshot it at the same viewport as the reference into
   `replica/clone-screens/S07.png` for replica-diff.
8. One commit per screen: `build: S07 booking page`.

## Definition of done, per screen

- [ ] every state from the recon map, plus empty, error and loading
- [ ] works at 390px and 1440px wide
- [ ] keyboard only: can complete the flow
- [ ] no console errors
- [ ] no hard-coded copy borrowed from the original
- [ ] features.csv updated
- [ ] screenshot saved for diff

## Step 4: the build log

`replica/build-log.md`, one line per screen: ID, date, done or partial, what
is missing, what was harder than expected. When a feature is bigger than it
looked, say so in the log and in the chat. Do not quietly ship half of it.

## When you are stuck on how something works

Go back to the original as a user: read its help article, watch its public
walkthrough, use the user's own account. Do not dig into its code or network
calls. Then build your own version of the behaviour.

## Output

Screens built, the feature matrix updated, screenshots saved, and a summary:
screens done of total, must-haves done of total, what is next. Then
the `replica-backend` skill if the data layer is still fake, else `replica-test`.
