"""Scaffold Feature classes from pasted feature text: reads Input.txt (blocks
headed "Level N: FEATURE NAME") and writes one class per block to Output.py,
both next to this script. Run it directly; importing it does nothing."""

from pathlib import Path

ADDITIONAL = "Wild Magic Sorcerer"

_HERE = Path(__file__).parent
INPUT_PATH = _HERE / "Input.txt"
OUTPUT_PATH = _HERE / "Output.py"


def parse_features(lines: list[str]) -> list[tuple[str, str, str, list[str]]]:
    """(level, display name, class name, description lines) per feature block."""
    headers = []
    content = []
    local_content: list[str] = []
    for line in lines:
        if line.startswith("Level "):
            level, name = (part.strip() for part in line.strip().split(":", 1))
            name = " ".join(word[0] + word[1:].lower() for word in name.split(" "))
            headers.append((level, name, name.replace(" ", "")))
            if local_content:
                content.append(local_content)
            local_content = []
        elif line != "\n":
            local_content.append(line)
    content.append(local_content)
    return [
        (level, name, class_name, body)
        for (level, name, class_name), body in zip(headers, content)
    ]


def render_feature(level: str, name: str, class_name: str, body: list[str]) -> str:
    out = [
        f"class {class_name}(Feature):\n",
        "    def __init__(self):\n",
        f'        super().__init__(name="{name}", origin="{ADDITIONAL} {level}")\n\n',
        "    def get_description(self, character: CharacterView) -> str:\n",
        "        description = (\n",
    ]
    for i, line in enumerate(body):
        terminator = '"' if i >= len(body) - 1 else r'\n"'
        out.append(f'            "{line.strip()}{terminator}\n')
    out.append("        )\n")
    out.append("        return description\n")
    out.append("\n\n")
    return "".join(out)


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8") as f:
        lines = f.readlines()
    OUTPUT_PATH.write_text(
        "".join(render_feature(*feature) for feature in parse_features(lines)),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
