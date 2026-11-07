"""Runs the ticket scripts on a throwaway repo, with a fake `gh` on PATH that logs its calls."""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1] / "templates/docs/parallax"
FAKE_GH = """#!/bin/sh
printf '%s\\n' "$*" >> "$GH_LOG"
case "$1 $2" in
  "repo view") [ -z "$GH_NO_REPO" ] ;;
  "issue create") echo https://github.com/o/r/issues/7 ;;
  "issue view") cat "$GH_VIEW" ;;
esac
"""


class Tickets(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name) / "repo"
        self.parallax = self.repo / "docs/parallax"
        shutil.copytree(TEMPLATES, self.parallax, ignore=shutil.ignore_patterns("__pycache__"))
        (self.parallax / "parallax.toml").write_text('source_roots = ["src"]\n')
        (self.repo / "src/pkg").mkdir(parents=True)
        (self.repo / "src/pkg/a.py").write_text("")
        (self.repo / "top.py").write_text("")
        bin_dir = Path(tmp.name) / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
        self.log = Path(tmp.name) / "gh.log"
        self.view = Path(tmp.name) / "view.json"
        self.env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "GH_LOG": str(self.log),
                    "GH_VIEW": str(self.view)}

    def run_script(self, name, *args, **env):
        return subprocess.run([sys.executable, str(self.parallax / "tools" / f"{name}_ticket.py"), *args],
                              cwd=self.repo, env={**self.env, **env}, capture_output=True, text=True)

    def calls(self):
        return self.log.read_text() if self.log.exists() else ""

    def ideas(self):
        return (self.parallax / "pages/agent-guide/ideas.md").read_text()

    def open_idea(self):
        out = self.run_script("open", "idea", "try x", "top.py")
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout.strip()

    def view_issue(self, labels):
        body = "**Where:** `top.py`\n\n### Observed\nit broke\n\n> **Lead, not fact.**"
        self.view.write_text(json.dumps({"body": body, "title": "t", "labels": [{"name": n} for n in labels]}))

    def test_idea_gets_row_and_4_char_id(self):
        tid = self.open_idea()
        self.assertRegex(tid, r"^[0-9a-z]{4}$")
        self.assertIn(f"| `{tid}` |", self.ideas())
        self.assertIn("try x", self.ideas())
        self.assertEqual(self.calls(), "")

    def test_issue_has_sections_and_labels(self):
        out = self.run_script("open", "wanted", "it broke", "top.py", "--repro", "run it", "--cause", "a guess")
        self.assertEqual(out.stdout.strip(), "#7", out.stderr)
        calls = self.calls()
        for needle in ("### Observed", "### Reproduce", "### Suspected cause", "Prio:WANTED,needs-triage", "Lead, not fact"):
            self.assertIn(needle, calls)

    def test_where_path_resolves_through_source_roots(self):
        out = self.run_script("open", "idea", "x", "pkg/a.py")
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_unknown_path_rejected(self):
        out = self.run_script("open", "idea", "x", "nope.py")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("nope.py", out.stderr)
        self.assertIn("not found", out.stderr)

    def test_edit_verified_drops_triage_label(self):
        self.view_issue(["needs-triage"])
        out = self.run_script("edit", "#7", "--verified", "red test")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("--remove-label needs-triage", self.calls())
        self.assertIn("Verified:** red test", self.calls())

    def test_close_issue_requires_comment(self):
        self.assertNotEqual(self.run_script("close", "#7").returncode, 0)
        self.assertEqual(self.calls(), "")
        self.assertEqual(self.run_script("close", "#7", "--comment", "wrong").returncode, 0)
        self.assertIn("issue close 7", self.calls())

    def test_close_idea_removes_row(self):
        tid = self.open_idea()
        self.assertEqual(self.run_script("close", tid).returncode, 0)
        self.assertNotIn(tid, self.ideas())

    def test_tier_move_idea_to_issue_opens_and_closes(self):
        tid = self.open_idea()
        out = self.run_script("edit", tid, "--tier", "minor")
        self.assertEqual(out.stdout.strip(), "#7", out.stderr)
        self.assertIn("Prio:MINOR", self.calls())
        self.assertNotIn(f"| `{tid}` |", self.ideas())

    def test_issue_tier_without_github_refuses_clearly(self):
        out = self.run_script("open", "wanted", "it broke", "top.py", GH_NO_REPO="1")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("only ideas", out.stderr)
        self.assertNotIn("issue create", self.calls())

    def test_idea_works_without_github(self):
        out = self.run_script("open", "idea", "x", "top.py", GH_NO_REPO="1", PATH="/usr/bin:/bin")
        self.assertEqual(out.returncode, 0, out.stderr)


if __name__ == "__main__":
    unittest.main()
