"""Runs the shipped site script with fake tools on PATH, in a throwaway repo layout."""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "templates/docs/parallax"
FAKE = '#!/bin/sh\nprintf "%s\\n" "$0 $*" >> "$TOOL_LOG"\n'


class Serve(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.parallax = self.root / "repo/docs/parallax"
        (self.parallax / "tools").mkdir(parents=True)
        shutil.copy(TEMPLATE / "tools/serve.py", self.parallax / "tools")
        (self.parallax / "requirements.txt").write_text("")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "tools.log"

    def fake(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(FAKE)
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def run_script(self, *args, cwd=None):
        env = {**os.environ, "PATH": f"{self.bin}:/usr/bin:/bin", "TOOL_LOG": str(self.log)}
        return subprocess.run([sys.executable, str(self.parallax / "tools/serve.py"), *args],
                              cwd=cwd or self.root / "repo", env=env, capture_output=True, text=True)

    def calls(self):
        return self.log.read_text() if self.log.exists() else ""

    def no_system_uvx(self):
        if shutil.which("uvx", path="/usr/bin:/bin"):
            self.skipTest("uvx installed system-wide")

    def test_uses_uvx_when_present(self):
        self.fake(self.bin / "uvx")
        self.assertEqual(self.run_script().returncode, 0)
        calls = self.calls()
        self.assertIn("--with-requirements", calls)
        self.assertIn(str(self.parallax / "requirements.txt"), calls)
        self.assertIn("mkdocs serve -f", calls)
        self.assertIn(str(self.parallax / "mkdocs.yml"), calls)
        self.assertFalse((self.parallax / ".venv").exists())

    def test_build_flag_runs_a_strict_build_to_a_temp_dir(self):
        self.fake(self.bin / "uvx")
        self.run_script("--build")
        self.assertIn("mkdocs build --strict", self.calls())
        self.assertIn("-d ", self.calls())

    def test_extra_arguments_are_passed_on(self):
        self.fake(self.bin / "uvx")
        self.run_script("--build", "-d", "/x/site")
        self.assertIn("-d /x/site", self.calls())
        self.assertEqual(self.calls().count(" -d "), 1)

    def test_works_from_any_folder(self):
        self.fake(self.bin / "uvx")
        self.assertEqual(self.run_script(cwd=self.root).returncode, 0)

    def test_without_uvx_builds_a_private_venv_once(self):
        self.no_system_uvx()
        out = self.run_script()
        self.assertTrue((self.parallax / ".venv/requirements.txt").is_file(), out.stderr)
        self.fake(self.parallax / ".venv/bin/mkdocs")
        self.assertEqual(self.run_script().returncode, 0)
        self.assertIn(".venv/bin/mkdocs serve", self.calls())

    def test_changed_pins_rebuild_the_venv(self):
        self.no_system_uvx()
        self.run_script()
        self.fake(self.parallax / ".venv/bin/mkdocs")
        (self.parallax / "requirements.txt").write_text("# changed\n")
        self.run_script()
        self.assertFalse((self.parallax / ".venv/bin/mkdocs").exists())

    def test_failure_exit_code_is_passed_on(self):
        (self.bin / "uvx").write_text("#!/bin/sh\nexit 3\n")
        (self.bin / "uvx").chmod(0o755)
        self.assertEqual(self.run_script().returncode, 3)


if __name__ == "__main__":
    unittest.main()
