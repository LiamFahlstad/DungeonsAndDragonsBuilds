"""What changed in a build's golden snapshot, as readable text instead of hashes.

Usage (from the repo root):
    python .claude/skills/snapshot-diffs/snapshot_diff.py                  # every build that differs from its golden
    python .claude/skills/snapshot-diffs/snapshot_diff.py Obmar Clover     # builds whose name contains these (case-insensitive)
    python .claude/skills/snapshot-diffs/snapshot_diff.py Obmar --page level_04 --max-lines 200
    python .claude/skills/snapshot-diffs/snapshot_diff.py --stats-only     # skip rendering the baseline pages
    python .claude/skills/snapshot-diffs/snapshot_diff.py Obmar --ref main # compare page text against another commit

tests/snapshots/build_stats.json holds every computed stat, so a stat change is shown
straight from it, per ability and skill by name. tests/snapshots/sheet_hashes.json holds
only a sha256 per page, so to show what a changed page says now versus before, the pages are
also rendered from --ref (default HEAD): an export of that commit is cached under the system
temp folder (never touching the working tree, the index or other worktrees) and rendered in
a separate process. Pages are compared as text (tags stripped, one line per block); a page
whose text is identical but bytes differ is reported as a markup-only change with a raw diff.

Exit status: 0 when every selected build matches its golden, 1 when any differs.
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

# Stats stored as one list entry per Ability / Skill, in enum order.
ABILITY_KEYS = ("scores", "saves", "save_prof")
SKILL_KEYS = ("skills", "skill_abilities", "skill_rolls", "skill_sources", "expertise")

# Runs inside the --ref export: renders each named build's pages with that commit's code
# into argv[1]/<build>/full/<page>, and lists the builds that commit doesn't have.
BASELINE_RENDERER = """
import json, os, sys, tempfile
from pathlib import Path
out = Path(sys.argv[1])
os.environ["SNAPSHOT_DUMP_DIR"] = str(out)
from tests import _snapshot_helpers as helpers
helpers.SNAPSHOT_DUMP_DIR = str(out)
missing, failed = [], {}
for name in sys.argv[2:]:
    if name not in helpers.ALL_BUILDS:
        missing.append(name)
        continue
    try:
        helpers.render_and_hash(name, Path(tempfile.mkdtemp()), dump=True)
    except Exception as error:
        failed[name] = f"{type(error).__name__}: {error}"
(out / "_baseline.json").write_text(json.dumps({"missing": missing, "failed": failed}))
"""


class _TextExtractor(HTMLParser):
    BLOCK = {"p", "div", "li", "tr", "br", "h1", "h2", "h3", "h4", "h5", "h6", "table", "ul", "ol", "section", "summary", "details", "header", "footer", "nav"}
    SKIP = {"script", "style"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skipping += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")
        elif tag in ("td", "th"):
            self.parts.append(" | ")
        else:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self._skipping = max(0, self._skipping - 1)
        elif tag in self.BLOCK:
            self.parts.append("\n")
        else:
            self.parts.append(" ")

    def handle_data(self, data):
        if not self._skipping:
            self.parts.append(data)


def page_text(content: bytes) -> list[str]:
    parser = _TextExtractor()
    parser.feed(content.decode("utf-8", errors="replace"))
    lines = (re.sub(r"\s+", " ", line).strip(" |") for line in "".join(parser.parts).splitlines())
    return [line for line in lines if line]


def render_pages(name: str) -> dict[str, bytes]:
    """Every page of `name`'s sheet, rendered in memory exactly as the snapshot test does."""
    from Presentation.CharacterSheetWriters import get_output_folder
    from tests._snapshot_helpers import CapturingSheetWriter, build

    data = build(name)
    output_folder = Path(tempfile.gettempdir()) / "dnd-snapshot-diff-render" / os.path.basename(get_output_folder(data))
    writer = CapturingSheetWriter(output_folder)
    writer.write_character_sheet(data, output_folder=str(output_folder))
    return dict(sorted(writer.pages.items()))


def stat_lines(golden: dict | None, actual: dict) -> list[str]:
    from Core.Definitions import Ability, Skill

    if golden is None:
        return ["  (no golden stats: a new build; UPDATE_SNAPSHOTS=1 adds it)"]
    lines = []
    for key in sorted({*golden, *actual}):
        before, after = golden.get(key), actual.get(key)
        if before == after:
            continue
        labels = [a.name for a in Ability] if key in ABILITY_KEYS else [s.name for s in Skill] if key in SKILL_KEYS else None
        if labels and isinstance(before, list) and isinstance(after, list) and len(before) == len(after) == len(labels):
            for label, old, new in zip(labels, before, after):
                if old != new:
                    lines.append(f"  {key}[{label}]: {old!r} -> {new!r}")
        else:
            lines.append(f"  {key}: {before!r} -> {after!r}")
    return lines


def baseline_tree(ref: str) -> tuple[Path, str]:
    """An export of `ref` under the temp folder, made once per commit and reused."""
    sha = subprocess.run(["git", "rev-parse", ref], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    tree = Path(tempfile.gettempdir()) / "dnd-snapshot-baseline" / sha[:12]
    if not (tree / ".complete").exists():
        tree.mkdir(parents=True, exist_ok=True)
        archive = tree.parent / f"{sha[:12]}.zip"
        subprocess.run(["git", "archive", "--format=zip", "-o", str(archive), sha], cwd=ROOT, check=True)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(tree)
        archive.unlink()
        (tree / ".complete").write_text(sha)
    return tree, sha


def render_baseline(ref: str, names: list[str]) -> tuple[Path, dict, str]:
    tree, sha = baseline_tree(ref)
    out = Path(tempfile.mkdtemp(prefix="dnd-snapshot-diff-"))
    env = {**os.environ, "PYTHONPATH": str(tree), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    env.pop("UPDATE_SNAPSHOTS", None)
    result = subprocess.run([sys.executable, "-c", BASELINE_RENDERER, str(out), *names], cwd=tree, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"Rendering the baseline at {ref} ({sha[:12]}) failed:\n{result.stderr[-3000:]}")
    return out, json.loads((out / "_baseline.json").read_text()), sha


def page_diff(old: bytes, new: bytes, max_lines: int) -> list[str]:
    old_text, new_text = page_text(old), page_text(new)
    if old_text == new_text:
        diff = list(difflib.unified_diff(old.decode("utf-8", "replace").splitlines(), new.decode("utf-8", "replace").splitlines(), lineterm="", n=0))[2:]
        header = ["      (markup-only change: the text is identical; raw HTML diff)"]
    else:
        diff = list(difflib.unified_diff(old_text, new_text, lineterm="", n=1))[2:]
        header = []
    shown = [f"      {line[:300]}" for line in diff[:max_lines]]
    if len(diff) > max_lines:
        shown.append(f"      ... {len(diff) - max_lines} more diff lines (--max-lines to see more)")
    return header + shown


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("builds", nargs="*", help="substrings of build names (default: every build that differs from its golden)")
    parser.add_argument("--ref", default="HEAD", help="commit whose pages are the 'before' text (default HEAD)")
    parser.add_argument("--page", help="only show pages whose path contains this")
    parser.add_argument("--max-lines", type=int, default=60, help="diff lines shown per page (default 60)")
    parser.add_argument("--stats-only", action="store_true", help="don't render the baseline; list changed pages without their text")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    from tests._snapshot_helpers import BUILD_PARAMS, HASHES_PATH, SHEET_MODES, STATS_PATH, build, compute_stats, load

    names = BUILD_PARAMS
    if args.builds:
        wanted = [w.lower() for w in args.builds]
        names = [n for n in BUILD_PARAMS if any(w in n.lower() for w in wanted)]
        if not names:
            sys.exit(f"No registered build name contains any of {args.builds}. Builds come from RunCharacterCreator's BuildSelector and ExampleSelector.")

    golden_stats, golden_hashes = load(STATS_PATH), load(HASHES_PATH)
    mode = SHEET_MODES[0]
    reports: dict[str, dict] = {}
    for name in names:
        try:
            stats = json.loads(json.dumps(compute_stats(build(name))))
            pages = render_pages(name)
        except Exception as error:
            reports[name] = {"error": f"{type(error).__name__}: {error}"}
            continue
        hashes = {page: hashlib.sha256(content).hexdigest() for page, content in pages.items()}
        expected = golden_hashes.get(name, {}).get(mode)
        changed = added = removed = []
        if expected is not None:
            added = sorted(set(hashes) - set(expected))
            removed = sorted(set(expected) - set(hashes))
            changed = sorted(p for p in set(hashes) & set(expected) if hashes[p] != expected[p])
        stat_changes = stat_lines(golden_stats.get(name), stats)
        if stat_changes or changed or added or removed or expected is None:
            reports[name] = {"stats": stat_changes, "pages": pages, "changed": changed, "added": added, "removed": removed, "new": expected is None}

    stale = sorted((set(golden_stats) | set(golden_hashes)) - set(BUILD_PARAMS))
    if not reports:
        print(f"All {len(names)} selected builds match their goldens.")
        if stale and not args.builds:
            print(f"Golden entries for removed builds (delete by hand): {stale}")
        return 0

    baseline, info, sha = None, {"missing": [], "failed": {}}, ""
    need_baseline = [n for n, r in reports.items() if r.get("changed") or r.get("removed")]
    if need_baseline and not args.stats_only:
        baseline, info, sha = render_baseline(args.ref, need_baseline)

    for name, report in reports.items():
        print(f"\n=== {name}")
        if "error" in report:
            print(f"  BUILD FAILED: {report['error']}")
            continue
        if report["new"]:
            print("  (no golden sheet hashes: a new build; UPDATE_SNAPSHOTS=1 adds it)")
        if report["stats"]:
            print("  stats (golden -> now):")
            print("\n".join(f"  {line}" for line in report["stats"]))
        for label in ("added", "removed"):
            if report[label]:
                print(f"  pages {label}: {', '.join(report[label])}")
        if not report["changed"]:
            continue
        if baseline is None:
            print(f"  pages changed: {', '.join(report['changed'])}")
            continue
        if name in info["missing"] or name in info["failed"]:
            why = info["failed"].get(name, "the build doesn't exist there")
            print(f"  pages changed: {', '.join(report['changed'])}  (no baseline at {args.ref}: {why})")
            continue
        for page in report["changed"]:
            if args.page and args.page not in page:
                continue
            old_path = baseline / name / mode / page
            old = old_path.read_bytes() if old_path.exists() else b""
            new = report["pages"][page]
            if old == new:
                print(f"  ~ {page}: renders the same at {args.ref} ({sha[:12]}), so its golden is stale there, not changed by the working tree")
                continue
            print(f"  ~ {page}  ({args.ref} -> working tree)")
            print("\n".join(page_diff(old, new, args.max_lines)))

    differing = sorted(reports)
    print(f"\n{len(differing)} of {len(names)} selected builds differ from their goldens.")
    if stale and not args.builds:
        print(f"Golden entries for removed builds (delete by hand): {stale}")
    print("Once every change above is intended:  UPDATE_SNAPSHOTS=1 ./run_tests.sh -q -k \"" + " or ".join(differing) + "\"  then rerun ./run_tests.sh -q")
    return 1


if __name__ == "__main__":
    sys.exit(main())
