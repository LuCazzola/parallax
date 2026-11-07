"""Drives the real hook script through subprocess on throwaway git repos."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "hooks" / "check_sync.py"


class Hook(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name) / "data"
        self.repo = Path(tmp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        self.write("src/a.py", "a = 1\n")
        self.write("docs/index.md", "# hi\n")
        self.write(".parallax.toml", 'docs_dir = "docs"\nignore = ["*.lock"]\n')
        self.commit("init")

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.repo, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)

    def run_hook(self, event, cwd=None, session="s1", active=False, stdin=None):
        payload = stdin if stdin is not None else json.dumps(
            {"cwd": str(cwd or self.repo), "session_id": session, "stop_hook_active": active})
        env = {**os.environ, "CLAUDE_PLUGIN_DATA": str(self.data)}
        out = subprocess.run([sys.executable, str(SCRIPT), event], input=payload, env=env,
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        if not out.stdout.strip():
            return None
        hook = json.loads(out.stdout)["hookSpecificOutput"]
        self.assertEqual(hook["hookEventName"], "Stop")
        return hook["additionalContext"]

    def test_no_marker_is_silent(self):
        (self.repo / ".parallax.toml").unlink()
        self.run_hook("session-start")
        self.write("src/a.py", "a = 2\n")
        self.assertIsNone(self.run_hook("stop"))

    def test_not_a_git_repo_is_silent(self):
        with tempfile.TemporaryDirectory() as plain:
            self.assertIsNone(self.run_hook("stop", cwd=plain))

    def test_code_edit_blocks_once_naming_the_file(self):
        self.run_hook("session-start")
        self.write("src/a.py", "a = 2\n")
        first = self.run_hook("stop")
        self.assertIn("src/a.py", first)
        self.assertIn("parallax:sync", first)
        self.assertIsNone(self.run_hook("stop"))

    def test_second_edit_blocks_again(self):
        self.run_hook("session-start")
        self.write("src/a.py", "a = 2\n")
        self.run_hook("stop")
        self.write("src/a.py", "a = 3\n")
        self.assertTrue(self.run_hook("stop"))

    def test_stop_hook_active_is_silent(self):
        self.run_hook("session-start")
        self.write("src/a.py", "a = 2\n")
        self.assertIsNone(self.run_hook("stop", active=True))

    def test_dirty_tree_at_session_start_is_not_attributed(self):
        self.write("src/a.py", "a = 2\n")
        self.run_hook("session-start")
        self.assertIsNone(self.run_hook("stop"))

    def test_edit_made_outside_any_tool_is_seen(self):
        self.run_hook("session-start")
        subprocess.run(["sh", "-c", "echo x > src/new.py"], cwd=self.repo, check=True)
        self.assertIn("src/new.py", self.run_hook("stop"))

    def test_deleted_file_blocks(self):
        self.run_hook("session-start")
        (self.repo / "src/a.py").unlink()
        self.assertIn("src/a.py", self.run_hook("stop"))

    def test_docs_only_change_is_silent(self):
        self.run_hook("session-start")
        self.write("docs/index.md", "# changed\n")
        self.assertIsNone(self.run_hook("stop"))

    def test_ignored_glob_is_silent(self):
        self.run_hook("session-start")
        self.write("deps.lock", "x\n")
        self.assertIsNone(self.run_hook("stop"))

    def test_commit_of_code_blocks(self):
        self.run_hook("session-start")
        self.write("src/a.py", "a = 2\n")
        self.commit("change")
        self.assertIn("src/a.py", self.run_hook("stop"))

    def test_commit_of_docs_only_is_silent(self):
        self.run_hook("session-start")
        self.write("docs/index.md", "# changed\n")
        self.commit("docs")
        self.assertIsNone(self.run_hook("stop"))

    def test_committing_an_already_synced_edit_is_silent(self):
        self.run_hook("session-start")
        self.write("src/a.py", "a = 2\n")
        self.run_hook("stop")
        self.commit("change")
        self.assertIsNone(self.run_hook("stop"))

    def test_branch_switch_is_silent(self):
        self.git("checkout", "-q", "-b", "other")
        self.write("src/b.py", "b = 1\n")
        self.commit("other")
        self.git("checkout", "-q", "main")
        self.write("src/c.py", "c = 1\n")
        self.commit("main work")
        self.run_hook("session-start")
        self.git("checkout", "-q", "other")
        self.assertIsNone(self.run_hook("stop"))
        self.write("src/b.py", "b = 2\n")
        self.assertTrue(self.run_hook("stop"))

    def test_forward_branch_switch_is_silent(self):
        self.git("checkout", "-q", "-b", "ahead")
        self.write("src/b.py", "b = 1\n")
        self.commit("ahead")
        self.git("checkout", "-q", "main")
        self.run_hook("session-start")
        self.git("checkout", "-q", "ahead")
        self.assertIsNone(self.run_hook("stop"))

    def test_fast_forward_merge_is_silent(self):
        self.git("checkout", "-q", "-b", "ahead")
        self.write("src/b.py", "b = 1\n")
        self.commit("ahead")
        self.git("checkout", "-q", "main")
        self.run_hook("session-start")
        self.git("merge", "-q", "--ff-only", "ahead")
        self.assertIsNone(self.run_hook("stop"))

    def test_dirty_edit_during_branch_switch_is_seen(self):
        self.git("checkout", "-q", "-b", "ahead")
        self.write("src/b.py", "b = 1\n")
        self.commit("ahead")
        self.git("checkout", "-q", "main")
        self.run_hook("session-start")
        self.git("checkout", "-q", "ahead")
        self.write("src/a.py", "a = 9\n")
        self.assertIn("src/a.py", self.run_hook("stop"))

    def test_amend_is_seen(self):
        self.write("src/a.py", "a = 2\n")
        self.commit("one")
        self.run_hook("session-start")
        self.write("src/a.py", "a = 3\n")
        self.git("add", "-A")
        self.git("commit", "-q", "--amend", "-m", "one")
        self.assertIn("src/a.py", self.run_hook("stop"))

    def test_soft_reset_and_recommit_is_seen(self):
        self.write("src/a.py", "a = 2\n")
        self.commit("one")
        self.run_hook("session-start")
        self.git("reset", "-q", "--soft", "HEAD~1")
        self.write("src/a.py", "a = 3\n")
        self.commit("two")
        self.assertIn("src/a.py", self.run_hook("stop"))

    def test_rebase_with_no_edits_is_silent(self):
        self.git("checkout", "-q", "-b", "work")
        self.write("src/b.py", "b = 1\n")
        self.commit("work")
        self.git("checkout", "-q", "main")
        self.write("src/c.py", "c = 1\n")
        self.commit("main")
        self.git("checkout", "-q", "work")
        self.run_hook("session-start")
        self.git("rebase", "-q", "main")
        self.assertIsNone(self.run_hook("stop"))

    def test_reverting_a_synced_edit_is_seen(self):
        self.run_hook("session-start")
        self.write("src/a.py", "a = 2\n")
        self.run_hook("stop")
        self.git("checkout", "-q", "src/a.py")
        self.assertIn("src/a.py", self.run_hook("stop"))

    def test_mkdocs_and_readme_edits_are_not_code(self):
        self.write("mkdocs.yml", "nav: []\n")
        self.write("README.md", "# hi\n")
        self.commit("config")
        self.run_hook("session-start")
        self.write("mkdocs.yml", "nav: [a]\n")
        self.write("README.md", "# changed\n")
        self.assertIsNone(self.run_hook("stop"))

    def test_edit_during_sync_turn_is_not_reported_next_turn(self):
        self.run_hook("session-start")
        self.write("src/a.py", "a = 2\n")
        self.run_hook("stop")
        self.write("src/a.py", "a = 3\n")
        self.run_hook("stop", active=True)
        self.assertIsNone(self.run_hook("stop"))

    def test_subfolder_cwd_finds_marker(self):
        self.run_hook("session-start", cwd=self.repo / "src")
        self.write("src/a.py", "a = 2\n")
        self.assertTrue(self.run_hook("stop", cwd=self.repo / "src"))

    def test_repo_with_no_commits_does_not_crash(self):
        with tempfile.TemporaryDirectory() as empty:
            self.git("init", "-q", cwd=empty)
            Path(empty, ".parallax.toml").write_text('docs_dir = "docs"\n')
            self.run_hook("session-start", cwd=empty)
            Path(empty, "x.py").write_text("x\n")
            self.assertIn("x.py", self.run_hook("stop", cwd=empty))
            self.assertIsNone(self.run_hook("stop", cwd=empty))

    def test_path_with_spaces_and_unicode_named_correctly(self):
        self.run_hook("session-start")
        self.write("src/my café file.py", "x\n")
        self.assertIn("src/my café file.py", self.run_hook("stop"))

    def test_malformed_toml_fails_open(self):
        (self.repo / ".parallax.toml").write_text("= nonsense [\n")
        self.run_hook("session-start")
        self.write("src/a.py", "a = 2\n")
        self.assertIsNone(self.run_hook("stop"))

    def test_garbage_stdin_fails_open(self):
        self.assertIsNone(self.run_hook("stop", stdin="not json"))

    def test_missing_session_state_records_baseline_silently(self):
        self.write("src/a.py", "a = 2\n")
        self.assertIsNone(self.run_hook("stop"))
        self.write("src/a.py", "a = 3\n")
        self.assertTrue(self.run_hook("stop"))

    def test_second_session_keeps_its_own_baseline(self):
        self.run_hook("session-start", session="a")
        self.write("src/a.py", "a = 2\n")
        self.run_hook("session-start", session="b")
        self.assertIsNone(self.run_hook("stop", session="b"))
        self.assertTrue(self.run_hook("stop", session="a"))

    def test_stale_session_files_removed(self):
        self.run_hook("session-start", session="old")
        stale = next((self.data / "sessions").iterdir())
        past = time.time() - 2 * 86400
        os.utime(stale, (past, past))
        self.run_hook("session-start", session="new")
        self.assertFalse(stale.exists())
        self.assertEqual(len(list((self.data / "sessions").iterdir())), 1)

    def test_compaction_keeps_pending_changes(self):
        self.run_hook("session-start")
        self.write("src/a.py", "a = 2\n")
        payload = json.dumps({"cwd": str(self.repo), "session_id": "s1", "source": "compact"})
        self.run_hook("session-start", stdin=payload)
        self.assertTrue(self.run_hook("stop"))

    def test_rename_names_both_paths(self):
        self.run_hook("session-start")
        self.git("mv", "src/a.py", "src/b.py")
        reason = self.run_hook("stop")
        self.assertIn("src/a.py", reason)
        self.assertIn("src/b.py", reason)

    def test_long_change_list_is_capped(self):
        self.run_hook("session-start")
        for i in range(30):
            self.write(f"src/f{i}.py", "x\n")
        reason = self.run_hook("stop")
        self.assertLessEqual(sum(f"src/f{i}.py" in reason for i in range(30)), 20)
        self.assertIn("more", reason)


if __name__ == "__main__":
    unittest.main()
