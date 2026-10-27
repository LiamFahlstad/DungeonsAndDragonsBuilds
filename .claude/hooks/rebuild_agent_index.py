"""PostToolUse hook (Edit/Write): regenerate the agent index after an agent or skill changes.

Reads the hook input JSON from stdin. Only an edit to `.claude/agents/**/*.md` or
`.claude/skills/<skill>/SKILL.md` triggers a rebuild; anything else exits immediately. The index
(.claude/skills/agent-index/SKILL.md) is generated from frontmatter, so keeping it current
automatically means it can never drift. tests/test_claude_config.py catches the cases this hook
can't see, such as files moved with git mv or edited outside Claude.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / ".claude" / "skills" / "agent-index"


def relevant(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(ROOT / ".claude")
    except ValueError:
        return False
    parts = rel.parts
    if parts[:1] == ("agents",) and path.suffix == ".md":
        return True
    return len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md" and parts[1] != "agent-index"


def main() -> int:
    hook_input = json.load(sys.stdin)
    file_path = (hook_input.get("tool_input") or {}).get("file_path")
    if not file_path or not relevant(Path(file_path)):
        return 0
    result = subprocess.run([sys.executable, str(INDEX / "build_index.py")], capture_output=True, text=True)
    if result.returncode != 0:
        # Not blocking: report it so Claude can fix the frontmatter that broke the build.
        print(f"agent index rebuild failed:\n{result.stdout}{result.stderr}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
