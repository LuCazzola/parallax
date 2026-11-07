"""Runs the shipped docs check on throwaway repos."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "templates/docs/parallax/tools/check_docs.py"


class CheckDocs(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        self.write("docs/parallax/parallax.toml", 'source_roots = ["src"]\n')
        self.write("docs/parallax/mkdocs.yml", "nav:\n  - Home: index.md\n")
        self.write("src/pkg/__init__.py", "")
        self.write("src/pkg/core.py", "x = 1\n")
        self.write("docs/parallax/pages/index.md", "# Home\n\nSee `src/pkg/core.py`.\n")
        dest = self.repo / "docs/parallax/tools/check_docs.py"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(SCRIPT, dest)

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def run_check(self):
        return subprocess.run([sys.executable, "docs/parallax/tools/check_docs.py"], cwd=self.repo,
                              capture_output=True, text=True)

    def assert_clean(self):
        out = self.run_check()
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def assert_flags(self, *needles):
        out = self.run_check()
        self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
        for needle in needles:
            self.assertIn(needle, out.stdout)

    def test_clean_repo_passes(self):
        self.assert_clean()

    def test_missing_backticked_path_fails_with_location(self):
        self.write("docs/parallax/pages/index.md", "# Home\n\nline\nSee `src/pkg/gone.py`.\n")
        self.assert_flags("docs/parallax/pages/index.md:4", "src/pkg/gone.py")

    def test_root_level_file_with_extension_is_checked(self):
        self.write("real.toml", "")
        self.write("docs/parallax/pages/index.md", "`real.toml`\n")
        self.assert_clean()

    def test_paths_in_fenced_blocks_ignored(self):
        self.write("docs/parallax/pages/index.md", "```\n`src/pkg/gone.py`\n```\n")
        self.assert_clean()

    def test_non_paths_ignored(self):
        self.write("docs/parallax/pages/index.md",
                   "`<path>` `src/*.py` `https://x.y/z` `nowhere/b` `$HOME/x` `a b/c` `v1.2` `x.y`\n")
        self.assert_clean()

    def test_paths_outside_the_repo_ignored(self):
        self.write("docs/parallax/pages/index.md", "`/usr/bin/nope` `../other/nope.py` `~/nope.py`\n")
        self.assert_clean()

    def test_dotfile_at_root_is_checked(self):
        self.write("docs/parallax/pages/index.md", "`.github/workflows/gone.yml`\n")
        self.write(".github/workflows/real.yml", "")
        self.assert_flags("gone.yml")

    def test_only_pages_are_scanned(self):
        self.write("docs/parallax/notes/n.md", "`src/pkg/gone.py`\n")
        self.write("docs/other/old.md", "`src/pkg/gone.py`\n")
        self.assert_clean()

    def test_user_guide_page_needs_code_line(self):
        self.write("docs/parallax/pages/user-guide/part.md", "# Part\n\nProse.\n")
        self.assert_flags("docs/parallax/pages/user-guide/part.md", "Code:")

    def test_user_guide_index_is_exempt(self):
        self.write("docs/parallax/pages/user-guide/index.md", "# Why\n\nProse.\n")
        self.assert_clean()

    def test_code_line_accepted(self):
        self.write("docs/parallax/pages/user-guide/part.md", "# Part\n\nCode: `src/pkg/core.py`, `src/pkg`\n")
        self.assert_clean()

    def test_code_line_path_must_exist(self):
        self.write("docs/parallax/pages/user-guide/part.md", "# Part\n\nCode: `nowhere/gone.py`\n")
        self.assert_flags("docs/parallax/pages/user-guide/part.md:3", "nowhere/gone.py")

    def stubs(self):
        self.write("docs/parallax/pages/agent-guide/api/pkg/index.md", "::: pkg\n\n::: pkg.core\n")
        self.write("docs/parallax/mkdocs.yml", "nav:\n  - x: agent-guide/api/pkg/index.md\n")

    def test_no_api_dir_skips_stub_check(self):
        self.assert_clean()

    def test_complete_stubs_pass(self):
        self.stubs()
        self.assert_clean()

    def test_api_stub_missing_fails(self):
        self.stubs()
        self.write("src/pkg/sub/__init__.py", "")
        self.assert_flags("pkg.sub")

    def test_module_missing_from_stub_fails(self):
        self.stubs()
        self.write("src/pkg/extra.py", "")
        self.assert_flags("pkg.extra")

    def test_stale_api_stub_fails(self):
        self.stubs()
        self.write("docs/parallax/pages/agent-guide/api/old/index.md", "::: old\n")
        self.write("docs/parallax/mkdocs.yml", "nav:\n  - x: agent-guide/api/pkg/index.md\n  - y: agent-guide/api/old/index.md\n")
        self.assert_flags("old")

    def test_stub_not_in_nav_fails(self):
        self.stubs()
        self.write("docs/parallax/mkdocs.yml", "nav:\n  - Home: index.md\n")
        self.assert_flags("agent-guide/api/pkg/index.md", "nav")

    def test_renamed_top_folder_is_caught(self):
        self.write("docs/parallax/pages/index.md", "`src/pkg/core.py` and `lib_gone/pkg/core.py`\n")
        self.assert_flags("lib_gone/pkg/core.py")

    def test_missing_top_level_file_is_caught(self):
        self.write("docs/parallax/pages/index.md", "`missing_top.md`\n")
        self.assert_flags("missing_top.md")

    def test_bare_filename_found_elsewhere_passes(self):
        self.write("docs/parallax/pages/index.md", "`core.py`\n")
        self.assert_clean()

    def test_docs_relative_path_passes(self):
        self.write("docs/parallax/pages/agent-guide/map.md", "x\n")
        self.write("docs/parallax/pages/index.md", "`agent-guide/map.md`\n")
        self.assert_clean()

    def test_code_line_without_backticks_is_checked(self):
        self.write("docs/parallax/pages/user-guide/part.md", "# Part\n\nCode: src/nothing_here.py\n")
        self.assert_flags("src/nothing_here.py")

    def test_nested_user_guide_page_needs_code_line(self):
        self.write("docs/parallax/pages/user-guide/sub/part.md", "# Part\n")
        self.assert_flags("docs/parallax/pages/user-guide/sub/part.md", "Code:")

    def test_flat_layout_skips_virtualenvs(self):
        self.stubs()
        self.write("docs/parallax/parallax.toml", 'source_roots = ["src", "."]\n')
        self.write(".venv/lib/site-packages/foo/__init__.py", "")
        self.write("venv/lib/site-packages/bar/__init__.py", "")
        out = self.run_check()
        self.assertNotIn("site-packages", out.stdout)

    def test_malformed_toml_reports_clearly(self):
        self.write("docs/parallax/parallax.toml", "= nonsense [\n")
        self.assert_flags("parallax.toml")


if __name__ == "__main__":
    unittest.main()
