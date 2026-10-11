#!/usr/bin/env python
"""Install the Replica pack into a Freebuff skills folder.

Standard library only, Python 3.8+.

    python install.py                      # ~/.agents/skills, every project
    python install.py --dry-run            # say what it would copy, copy nothing
    python install.py --list               # what is installed in the target now
    python install.py --project .          # ./.agents/skills, this project only
    python install.py --target DIR         # any folder the client scans
    python install.py --remove             # take the pack back out of the target

Why these folders: the client loads skills from `<project>/.agents/skills/`
and `<project>/.claude/skills/` for the project it is working in, and from
`~/.agents/skills/` and `~/.claude/skills/` for the machine. The Discover tab
installs into `~/.agents/skills/` as well, which is why that is the default
here. `.agents` wins over `.claude` when both hold a skill with the same name.

Skills are read when a thread starts, so open a new thread (or restart the
client) after installing, and the pack shows up on its own.
"""

import argparse
import os
import shutil
import sys

SKIP_DIRS = {"__pycache__", ".git"}


def skills_here():
    """The replica-*/ folders of this checkout, in pack order."""
    found = []
    for entry in sorted(os.listdir(".")):
        if entry.startswith("replica-") and os.path.isfile(
            os.path.join(entry, "SKILL.md")
        ):
            found.append(entry)
    return found


def copy_skill(source, target, dry_run):
    """Copy one skill folder, files and subfolders, minus caches."""
    def ignore(_directory, names):
        return [name for name in names if name in SKIP_DIRS or name.endswith(".pyc")]

    destination = os.path.join(target, source)
    if dry_run:
        return destination
    if os.path.isdir(destination):
        shutil.rmtree(destination)
    shutil.copytree(source, destination, ignore=ignore)
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Install the Replica pack into a skills folder the Freebuff client reads."
    )
    parser.add_argument(
        "--target",
        help="skills folder to install into (default: ~/.agents/skills)",
    )
    parser.add_argument(
        "--project",
        metavar="DIR",
        help="install into DIR/.agents/skills instead of the user's folder",
    )
    parser.add_argument("--dry-run", action="store_true", help="copy nothing, just say what would happen")
    parser.add_argument("--list", action="store_true", help="list what the target holds now")
    parser.add_argument("--remove", action="store_true", help="delete the pack from the target")
    arguments = parser.parse_args(argv)

    if arguments.target and arguments.project:
        parser.error("use --target or --project, not both")
    if arguments.project:
        target = os.path.join(os.path.abspath(arguments.project), ".agents", "skills")
    elif arguments.target:
        target = os.path.abspath(arguments.target)
    else:
        target = os.path.join(os.path.expanduser("~"), ".agents", "skills")

    skills = skills_here()
    if not skills:
        print("no replica-*/SKILL.md folders here: run this from the repo root")
        return 1

    print(f"target: {target}")
    if arguments.list:
        if not os.path.isdir(target):
            print("the folder does not exist yet")
            return 1
        for entry in sorted(os.listdir(target)):
            marker = "skill" if os.path.isfile(os.path.join(target, entry, "SKILL.md")) else "     "
            print(f"  {marker}  {entry}")
        return 0

    if arguments.remove:
        removed = []
        for name in skills:
            path = os.path.join(target, name)
            if os.path.isdir(path):
                if not arguments.dry_run:
                    shutil.rmtree(path)
                removed.append(name)
        for name in removed:
            print(f"  {'would remove' if arguments.dry_run else 'removed'}  {name}")
        if not removed:
            print("nothing of the pack is installed there")
        else:
            print("open a new thread in the client for the change to be picked up.")
        return 0

    if not arguments.dry_run:
        os.makedirs(target, exist_ok=True)
    for name in skills:
        destination = copy_skill(name, target, arguments.dry_run)
        verb = "would install" if arguments.dry_run else "installed"
        print(f"  {verb}  {name:22s} -> {destination}")

    if arguments.dry_run:
        print(f"\n{len(skills)} skills, nothing copied (--dry-run)")
        return 0

    print(
        f"\n{len(skills)} skills installed: {', '.join(skills)}."
        "\nOpen a new thread in the client, then ask it to clone an app: it will"
        "\nfind the pack by name. python install.py --remove undoes this."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
