#!/usr/bin/env python
"""Check every SKILL.md in this repo against the limits the Freebuff client
enforces, before you hand the pack to it.

Standard library only, Python 3.8+. Run from the repo root:

    python tools/check_skills.py            # every replica-*/ folder
    python tools/check_skills.py replica-diff

The limits are the ones in the client's own schemas, not guesses:

  agent loader (a skill folder the client discovers on disk)
    - the folder holds SKILL.md
    - frontmatter must be YAML and have `name` and `description`
    - name: /^[a-z0-9]+(-[a-z0-9]+)*$/, at most 64 characters, and it has to
      equal the folder name, or the loader skips the skill
    - description: truncated at 1024 characters by the loader
  account skill (Settings - Skills - Create, synced with the cloud)
    - name: /^[a-z0-9][a-z0-9-]{0,63}$/
    - description: trimmed, 1 to 1000 characters
    - instructions: trimmed, 1 to 50000 characters
    - resources: at most 50 files, each path is relative, has no backslash and
      is not skill.md, is at most 256 characters and has no <>:"|?* or control
      characters; each file is at most 100000 characters; the whole package
      stays under 2.5 MB of JSON
  this fork
    - no `/replica-x` slash command left in a body: the client has none
    - every `python <tool>.py` in a body resolves to a file in the skill folder
    - every file the body calls "in this folder" is in the folder

Exit status is 1 if any check fails, 0 otherwise.
"""

import json
import os
import re
import sys

AGENT_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CLOUD_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
NAME_MAX = 64
AGENT_DESCRIPTION_MAX = 1024
CLOUD_DESCRIPTION_MAX = 1000
INSTRUCTIONS_MAX = 50000
RESOURCE_MAX_FILES = 50
RESOURCE_PATH_MAX = 256
RESOURCE_CONTENT_MAX = 100000
PACKAGE_JSON_MAX = 2500000

ALLOWED_KEYS = {"name", "description", "license", "disable-model-invocation", "metadata"}
BAD_PATH_CHARS = re.compile(r'[<>:"|?*\x00-\x1f]')
IN_FOLDER_RE = re.compile(
    r"in this folder|in this folder:|\bin this folder\b", re.IGNORECASE
)
FILENAME_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:md|csv|json|py|ts|tsx|css|html)")
PYTHON_TOOL_RE = re.compile(r"python3?\s+((?:\.\./)*[A-Za-z0-9_./-]+\.py)")
TEMPLATE_BEFORE_RE = re.compile(
    r"([A-Za-z0-9_.-]+\.(?:md|csv|json|py|ts|css|html|tsx))\s+in this folder", re.IGNORECASE
)
TEMPLATE_AFTER_RE = re.compile(r"templates? in this folder:\s*(.+)", re.IGNORECASE)
SLASH_COMMAND_RE = re.compile(r"(?<![\w./])/replica-[a-z][a-z-]*(?![\w/-])")


class Problem(Exception):
    pass


def split_frontmatter(text):
    """Return (frontmatter_lines, body). Strict, like the client's parser."""
    if text.startswith("\ufeff"):
        text = text[1:]
    if not re.match(r"^---[ \t]*\r?\n", text):
        raise Problem("does not start with a YAML frontmatter block")
    lines = text.split("\n")
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r").strip() == "---":
            return lines[1:index], "\n".join(lines[index + 1 :])
    raise Problem("frontmatter block is never closed")


def parse_scalar(raw, line_number):
    """A plain, single or double quoted YAML scalar."""
    value = raw.strip()
    if not value:
        return ""
    if value[0] == '"' and value[-1] == '"' and len(value) > 1:
        body = value[1:-1]
        return (
            body.replace('\\"', '"')
            .replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace("\\\\", "\\")
        )
    if value[0] == "'" and value[-1] == "'" and len(value) > 1:
        return value[1:-1].replace("''", "'")
    return value


def parse_frontmatter(lines, path):
    """The subset of YAML the client's skills use, or a Problem."""
    fields = {}
    index = 0
    while index < len(lines):
        line = lines[index].rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if "\t" in line:
            raise Problem(f"line {index + 2}: a tab in the frontmatter")
        match = re.match(r"^([A-Za-z0-9_-]+):[ \t]*(.*)$", line)
        if not match:
            raise Problem(f"line {index + 2}: cannot read {line!r}")
        key, rest = match.group(1), match.group(2)
        if key in fields:
            raise Problem(f"line {index + 2}: {key} appears twice")
        if key not in ALLOWED_KEYS:
            raise Problem(f"line {index + 2}: unknown key {key!r}")
        if rest.startswith((">", "|")):
            style = rest
            block = []
            index += 1
            while index < len(lines) and (
                lines[index].strip() == "" or lines[index].startswith(" ")
            ):
                block.append(lines[index].rstrip("\r").strip())
                index += 1
            if style.startswith(">"):
                fields[key] = " ".join(part for part in block if part)
            else:
                fields[key] = "\n".join(block)
            continue
        fields[key] = parse_scalar(rest, index + 2)
        index += 1
    return fields


def check_path(path):
    """The client's rule for one resource path. Returns an error or None."""
    if not path or path.startswith("/") or "\\" in path:
        return "must be relative and use forward slashes"
    if len(path) > RESOURCE_PATH_MAX:
        return f"is longer than {RESOURCE_PATH_MAX} characters"
    if path.lower() == "skill.md":
        return "may not be skill.md: the SKILL.md is the skill itself"
    if BAD_PATH_CHARS.search(path):
        return 'contains one of <>:"|?* or a control character'
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return "has an empty, . or .. path segment"
    return None


def check_skill(directory):
    """Check one skill folder. Returns (errors, warnings, summary)."""
    errors, warnings = [], []
    path = os.path.join(directory, "SKILL.md")
    if not os.path.isfile(path):
        return [f"{directory}: no SKILL.md in the folder"], [], None

    with open(path, encoding="utf-8") as handle:
        text = handle.read()

    try:
        front, body = split_frontmatter(text)
        fields = parse_frontmatter(front, path)
    except Problem as problem:
        return [f"{path}: {problem}"], [], None

    name = fields.get("name", "")
    description = fields.get("description", "")
    if not name:
        errors.append(f"{path}: no `name` in the frontmatter")
    else:
        if not name.strip():
            errors.append(f"{path}: `name` is empty")
        if len(name) > NAME_MAX:
            errors.append(f"{path}: `name` is longer than {NAME_MAX} characters")
        if not AGENT_NAME_RE.match(name):
            errors.append(
                f"{path}: `name` {name!r} is not /^[a-z0-9]+(-[a-z0-9]+)*$/ "
                "(the client's loader skips it)"
            )
        if not CLOUD_NAME_RE.match(name):
            errors.append(
                f"{path}: `name` {name!r} is not /^[a-z0-9][a-z0-9-]{{0,63}}$/ "
                "(the Skills form rejects it)"
            )
        folder = os.path.basename(os.path.normpath(directory))
        if name != folder:
            errors.append(
                f"{path}: `name` {name!r} does not match the folder {folder!r}, "
                "so the loader skips the skill"
            )

    if not description.strip():
        errors.append(f"{path}: no `description` in the frontmatter")
    else:
        if len(description) > CLOUD_DESCRIPTION_MAX:
            errors.append(
                f"{path}: description is {len(description)} characters, over the "
                f"{CLOUD_DESCRIPTION_MAX} the Skills form takes"
            )
        elif len(description) > AGENT_DESCRIPTION_MAX:
            warnings.append(
                f"{path}: description is {len(description)} characters; the loader "
                f"truncates at {AGENT_DESCRIPTION_MAX}"
            )
        if description.strip() != description:
            warnings.append(f"{path}: description has leading or trailing spaces")

    if len(body.strip()) > INSTRUCTIONS_MAX:
        errors.append(
            f"{path}: the body is {len(body.strip())} characters, over the "
            f"{INSTRUCTIONS_MAX} the Skills form takes as instructions"
        )
    if len(body.strip()) < 200:
        warnings.append(f"{path}: the body is only {len(body.strip())} characters")

    for match in SLASH_COMMAND_RE.finditer(body):
        warnings.append(
            f"{path}: line {body[: match.start()].count(chr(10)) + 1}: "
            f"{match.group(0)} is a slash command and this client has none"
        )

    siblings = sorted(
        entry
        for entry in os.listdir(directory)
        if entry != "SKILL.md" and os.path.isfile(os.path.join(directory, entry))
    )
    for tool in sorted(set(PYTHON_TOOL_RE.findall(body))):
        resolved = os.path.normpath(os.path.join(directory, tool))
        if not os.path.isfile(resolved):
            errors.append(f"{path}: the body runs {tool}, which is not there")

    for line in body.split("\n"):
        named = set(TEMPLATE_BEFORE_RE.findall(line))
        after = TEMPLATE_AFTER_RE.search(line)
        if after:
            named.update(FILENAME_RE.findall(after.group(1)))
        for filename in sorted(named):
            if filename.lower() == "skill.md":
                continue
            if not os.path.isfile(os.path.join(directory, filename)):
                errors.append(
                    f"{path}: {filename} is described as being in this folder and "
                    "is not there"
                )

    resources = []
    for filename in siblings:
        with open(os.path.join(directory, filename), encoding="utf-8") as handle:
            contents = handle.read()
        problem = check_path(filename)
        if problem:
            errors.append(f"{path}: resource {filename!r} {problem}")
        if len(contents) > RESOURCE_CONTENT_MAX:
            errors.append(
                f"{path}: resource {filename!r} is {len(contents)} characters, over "
                f"{RESOURCE_CONTENT_MAX}"
            )
        resources.append({"path": filename, "contents": contents})
    if len(resources) > RESOURCE_MAX_FILES:
        errors.append(
            f"{path}: {len(resources)} resource files, over the {RESOURCE_MAX_FILES} limit"
        )

    package = {
        "settings": {
            "skills": [
                {"name": name, "description": description, "instructions": body, "files": resources}
            ]
        }
    }
    encoded = len(json.dumps(package).encode("utf-8"))
    if encoded > PACKAGE_JSON_MAX:
        errors.append(f"{path}: the package encodes to {encoded} bytes, over {PACKAGE_JSON_MAX}")

    summary = {
        "name": name,
        "description": len(description),
        "body": len(body.strip()),
        "resources": len(resources),
        "bytes": encoded,
    }
    return errors, warnings, summary


def skill_directories(arguments):
    if arguments:
        return list(arguments)
    entries = []
    for entry in sorted(os.listdir(".")):
        if os.path.isdir(entry) and os.path.isfile(os.path.join(entry, "SKILL.md")):
            entries.append(entry)
    return entries


def main(argv):
    directories = skill_directories(argv)
    if not directories:
        print("no skill folders here: run this from the repo root")
        return 1

    errors, warnings, summaries = [], [], []
    for directory in directories:
        found, notes, summary = check_skill(directory)
        errors.extend(found)
        warnings.extend(notes)
        if summary:
            summaries.append(summary)
        print(("FAIL " if found else "ok   ") + directory)

    print()
    for summary in summaries:
        print(
            "{name:22s} description {description:4d}  body {body:5d}  "
            "resources {resources:2d}  package {bytes:6d} B".format(**summary)
        )

    if warnings:
        print("\nwarnings:")
        for warning in warnings:
            print(" -", warning)
    if errors:
        print("\nerrors:")
        for error in errors:
            print(" -", error)
        print(f"\n{len(errors)} error(s): the client would refuse or skip these")
        return 1

    print(f"\nall {len(summaries)} skills fit the client's limits")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
