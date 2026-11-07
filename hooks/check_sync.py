#!/usr/bin/env python3
"""Sends the agent to parallax:sync once per code change. Compares repo state, not tool
calls, so edits made through Bash count. Any error exits 0: a hook must never trap the agent."""
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

MAX_NAMED = 20
STALE_S = 24 * 3600
DELETED = "deleted"
MARKER = "docs/parallax/parallax.toml"
NOT_CODE = {"CLAUDE.md", "AGENTS.md", "README.md", "mkdocs.yml"}
# Whoever wrote these commits, the docs were not this agent's to follow.
FOREIGN_MOVES = ("checkout:", "rebase", "pull", "merge")


def git(root, *args, check=True):
    out = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                         encoding="utf-8", errors="surrogateescape")
    if check and out.returncode:
        raise RuntimeError(out.stderr)
    return out.stdout


def toplevel(cwd):
    return git(cwd, "rev-parse", "--show-toplevel", check=False).strip() or None


def load_config(root):
    import tomllib  # inside main's try: older Pythons fail open

    marker = Path(root, MARKER)
    if not marker.is_file():
        return None
    with marker.open("rb") as f:
        return tomllib.load(f)


def is_code(path, cfg):
    if path.startswith("docs/") or path in NOT_CODE:
        return False
    return not any(fnmatch.fnmatch(path, g) or fnmatch.fnmatch(Path(path).name, g)
                   for g in cfg.get("ignore", []))


def current_head(root):
    return git(root, "rev-parse", "-q", "--verify", "HEAD", check=False).strip()


def dirty_paths(root, cfg):
    fields = git(root, "status", "--porcelain", "-z", "--untracked-files=all").split("\0")
    paths, i = [], 0
    while i < len(fields) and fields[i]:
        status, path = fields[i][:2], fields[i][3:]
        paths.append(path)
        i += 1
        if "R" in status or "C" in status:  # the original path follows as its own field
            paths.append(fields[i])
            i += 1
    return sorted(p for p in paths if is_code(p, cfg))


def file_hash(root, path):
    full = Path(root, path)
    if not full.is_file():
        return DELETED
    with full.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def committed_code_paths(root, old, new, cfg):
    base = old or git(root, "hash-object", "-t", "tree", os.devnull).strip()
    names = git(root, "diff", "--name-only", "-z", base, new).split("\0")
    return [p for p in names if p and is_code(p, cfg)]


def state_path(session_id, root):
    safe = re.sub(r"[^\w-]", "_", session_id)
    digest = hashlib.sha1(str(root).encode()).hexdigest()[:12]
    return Path(os.environ["CLAUDE_PLUGIN_DATA"], "sessions", f"{safe}-{digest}.json")


def save_state(path, head, worktree):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"head": head, "worktree": worktree}))


def remove_stale(path):
    if path.parent.is_dir():
        cutoff = time.time() - STALE_S
        for f in path.parent.iterdir():
            if f.stat().st_mtime < cutoff:
                f.unlink()


def reason(paths):
    named = sorted(paths)[:MAX_NAMED]
    more = f" (and {len(paths) - len(named)} more)" if len(paths) > len(named) else ""
    return (f"Code changed: {', '.join(named)}{more}. Run parallax:sync so the docs follow it. "
            "If nothing needs updating, say so and stop.")


def last_move(root):
    return git(root, "reflog", "-1", "--format=%gs", check=False).strip()


def stop(data, root, cfg, state_file):
    head = current_head(root)
    dirty = dirty_paths(root, cfg)
    worktree = {p: file_hash(root, p) for p in dirty}
    if data.get("stop_hook_active"):
        save_state(state_file, head, worktree)  # what sync did is not a new change
        return
    if not state_file.is_file():
        save_state(state_file, head, worktree)
        return
    state = json.loads(state_file.read_text())
    seen = state["worktree"]
    old = state["head"]
    changed = {p for p, h in worktree.items() if seen.get(p) != h}
    moved = bool(head) and head != old
    if not (moved and last_move(root).startswith(FOREIGN_MOVES)):
        changed |= {p for p, h in seen.items() if p not in worktree and file_hash(root, p) != h}
        if moved:
            base = merge_base(root, old, head) if old else old
            changed |= {p for p in committed_code_paths(root, base, head, cfg)
                        if seen.get(p) != file_hash(root, p)}
    save_state(state_file, head, worktree)
    if changed:
        # Not {"decision": "block"}: that shows the user a "hook error".
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "Stop",
                                                 "additionalContext": reason(changed)}}))


def merge_base(root, old, new):
    """An amend or reset leaves `old` off `new`'s history: compare from where they split."""
    return git(root, "merge-base", old, new).strip()


def session_start(data, root, cfg, state_file):
    if data.get("source") == "compact":  # same session continuing: keep what it has not synced
        return
    dirty = dirty_paths(root, cfg)
    save_state(state_file, current_head(root), {p: file_hash(root, p) for p in dirty})


def main():
    data = json.load(sys.stdin)
    root = toplevel(data["cwd"])
    if not root:
        return
    cfg = load_config(root)
    if cfg is None:
        return
    state_file = state_path(data["session_id"], root)
    remove_stale(state_file)
    {"session-start": session_start, "stop": stop}[sys.argv[1]](data, root, cfg, state_file)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
