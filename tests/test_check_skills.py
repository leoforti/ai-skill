import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from _load import ROOT, load

check = load("tools", "check_skills")

GOOD = (
    "---\n"
    "name: %s\n"
    "description: >-\n"
    "  A skill that does the thing, in enough words to be worth reading. Trigger\n"
    "  anche in italiano: 'fai la cosa'.\n"
    "---\n\n"
    "# %s\n\n"
    "%s\n"
)


def write_skill(root, name, body=None, description=None, folder=None):
    body = body if body is not None else ("Body line.\n" * 40)
    directory = os.path.join(root, folder or name)
    os.makedirs(directory, exist_ok=True)
    text = GOOD % (name, name, body)
    if description is not None:
        text = text.replace(
            "  A skill that does the thing, in enough words to be worth reading. Trigger\n"
            "  anche in italiano: 'fai la cosa'.",
            description,
        )
    with open(os.path.join(directory, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    return directory


class CheckSkills(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_repo_itself_passes(self):
        folders = [os.path.join(ROOT, d) for d in os.listdir(ROOT)
                   if os.path.isfile(os.path.join(ROOT, d, "SKILL.md"))]
        self.assertEqual(len(folders), 12)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(check.main(folders), 0)

    def test_a_clean_skill_passes(self):
        directory = write_skill(self.root, "replica-demo")
        errors, _warnings, summary = check.check_skill(directory)
        self.assertEqual(errors, [])
        self.assertEqual(summary["name"], "replica-demo")

    def test_name_must_match_the_folder(self):
        directory = write_skill(self.root, "replica-demo", folder="replica-other")
        errors, _warnings, _summary = check.check_skill(directory)
        self.assertTrue(any("does not match the folder" in e for e in errors), errors)

    def test_a_bad_name_is_refused(self):
        directory = write_skill(self.root, "replica_demo")
        errors, _warnings, _summary = check.check_skill(directory)
        self.assertTrue(any("is not /^[a-z0-9]+" in e for e in errors), errors)

    def test_a_long_description_is_refused(self):
        long_line = "  " + ("x" * 1200)
        directory = write_skill(self.root, "replica-demo", description=long_line)
        errors, _warnings, _summary = check.check_skill(directory)
        self.assertTrue(any("description is" in e for e in errors), errors)

    def test_a_slash_command_is_reported(self):
        directory = write_skill(self.root, "replica-demo", body="Run `/replica-build` next.\n")
        _errors, warnings, _summary = check.check_skill(directory)
        self.assertTrue(any("slash command" in w for w in warnings), warnings)

    def test_a_path_is_not_a_slash_command(self):
        directory = write_skill(
            self.root, "replica-demo", body="Run `python ../replica-brand/sweep.py .` here.\n"
        )
        _errors, warnings, _summary = check.check_skill(directory)
        self.assertFalse(any("slash command" in w for w in warnings), warnings)

    def test_a_missing_tool_is_refused(self):
        directory = write_skill(self.root, "replica-demo", body="```bash\npython nowhere.py\n```\n")
        errors, _warnings, _summary = check.check_skill(directory)
        self.assertTrue(any("nowhere.py" in e for e in errors), errors)

    def test_a_tool_that_is_there_is_fine(self):
        directory = write_skill(self.root, "replica-demo", body="```bash\npython tool.py\n```\n")
        with open(os.path.join(directory, "tool.py"), "w", encoding="utf-8") as fh:
            fh.write("print('ok')\n")
        errors, _warnings, _summary = check.check_skill(directory)
        self.assertEqual(errors, [])

    def test_a_missing_template_is_refused(self):
        directory = write_skill(
            self.root, "replica-demo", body="Writes the map (template: map.md in this folder).\n"
        )
        errors, _warnings, _summary = check.check_skill(directory)
        self.assertTrue(any("map.md" in e for e in errors), errors)

    def test_a_template_that_is_there_is_fine(self):
        directory = write_skill(
            self.root, "replica-demo", body="Writes the map (template: map.md in this folder).\n"
        )
        with open(os.path.join(directory, "map.md"), "w", encoding="utf-8") as fh:
            fh.write("# Map\n")
        errors, _warnings, _summary = check.check_skill(directory)
        self.assertEqual(errors, [])

    def test_frontmatter_is_required(self):
        directory = write_skill(self.root, "replica-demo")
        with open(os.path.join(directory, "SKILL.md"), "w", encoding="utf-8") as fh:
            fh.write("# no frontmatter here\n")
        errors, _warnings, _summary = check.check_skill(directory)
        self.assertTrue(any("frontmatter" in e for e in errors), errors)

    def test_resources_are_counted(self):
        directory = write_skill(self.root, "replica-demo")
        for index in range(3):
            with open(os.path.join(directory, "file%d.txt" % index), "w") as fh:
                fh.write("x")
        _errors, _warnings, summary = check.check_skill(directory)
        self.assertEqual(summary["resources"], 3)

    def test_a_folder_without_skill_md_is_reported(self):
        directory = os.path.join(self.root, "replica-empty")
        os.makedirs(directory)
        errors, _warnings, _summary = check.check_skill(directory)
        self.assertTrue(any("no SKILL.md" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
