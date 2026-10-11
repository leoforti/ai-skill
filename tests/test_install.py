import os
import subprocess
import sys
import tempfile
import unittest

from _load import ROOT

SKILLS = ["replica-pack", "replica-recon", "replica-architect", "replica-design",
          "replica-build", "replica-backend", "replica-test", "replica-diff",
          "replica-entrepreneur", "replica-brand", "replica-launch", "replica-deploy"]


def run_install(*arguments):
    """Run install.py the way a user would, from the repo root."""
    return subprocess.run(
        [sys.executable, os.path.join(ROOT, "install.py")] + list(arguments),
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )


class Install(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.target = os.path.join(self.tmp.name, "skills")

    def tearDown(self):
        self.tmp.cleanup()

    def test_installs_every_skill_with_its_files(self):
        result = run_install("--target", self.target)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(sorted(os.listdir(self.target)), sorted(SKILLS))
        for name in SKILLS:
            self.assertTrue(os.path.isfile(os.path.join(self.target, name, "SKILL.md")), name)
        self.assertTrue(os.path.isfile(os.path.join(self.target, "replica-diff", "parity.py")))
        self.assertTrue(os.path.isfile(os.path.join(self.target, "replica-deploy", "preflight.md")))

    def test_the_installed_skills_pass_the_client_check(self):
        run_install("--target", self.target)
        folders = [os.path.join(self.target, name) for name in SKILLS]
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "check_skills.py")] + folders,
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_dry_run_copies_nothing(self):
        result = run_install("--target", self.target, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(os.path.isdir(self.target))
        self.assertIn("nothing copied", result.stdout)

    def test_list_says_what_is_there(self):
        run_install("--target", self.target)
        result = run_install("--target", self.target, "--list")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("skill  replica-diff", result.stdout)

    def test_project_target_goes_under_agents_skills(self):
        project = os.path.join(self.tmp.name, "app")
        result = run_install("--project", project)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(
            os.path.isfile(os.path.join(project, ".agents", "skills", "replica-pack", "SKILL.md"))
        )

    def test_remove_takes_the_pack_back_out(self):
        run_install("--target", self.target)
        result = run_install("--target", self.target, "--remove")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(os.listdir(self.target), [])
        self.assertTrue(os.path.isdir(self.target))

    def test_install_over_an_older_copy_replaces_it(self):
        stale = os.path.join(self.target, "replica-diff")
        os.makedirs(stale)
        with open(os.path.join(stale, "gone.txt"), "w") as fh:
            fh.write("old\n")
        run_install("--target", self.target)
        self.assertFalse(os.path.exists(os.path.join(stale, "gone.txt")))
        self.assertTrue(os.path.isfile(os.path.join(stale, "SKILL.md")))


if __name__ == "__main__":
    unittest.main()
