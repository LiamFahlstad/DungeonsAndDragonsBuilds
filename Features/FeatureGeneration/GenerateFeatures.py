ADDITIONAL = "Wild Magic Sorcerer"

with open("Features/FeatureGeneration/Input.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

content = []
local_content = []
other = []
for line in lines:
    if line.startswith("Level "):
        parts = line.strip().split(":", 1)
        level = parts[0].strip()
        name = parts[1].strip()
        name = " ".join([word[0] + word[1:].lower() for word in name.split(" ")])
        class_name = name.replace(" ", "")
        other.append((level, name, class_name))
        if local_content:
            content.append(local_content)
        local_content = []
    else:
        if line != "\n":
            local_content.append(line)
content.append(local_content)


with open("Features/FeatureGeneration/Output.py", "w", encoding="utf-8") as f:
    for (level, name, class_name), local_content in zip(other, content):
        f.write(f"class {class_name}(TextFeature):\n")
        f.write("    def __init__(self):\n")
        f.write(
            f'        super().__init__(name="{name}", origin="{ADDITIONAL} {level}")\n\n'
        )
        f.write(
            "    def get_description(self, character_stat_block: CharacterStatBlock) -> str:\n"
        )
        f.write("        description = (\n")
        for i, line in enumerate(local_content):
            if line == "\n":
                continue
            f.write(f'            "{line.strip()}')
            if i >= len(local_content) - 1:
                f.write('"')
            else:
                f.write(r'\n"')
            f.write("\n")
        f.write("        )\n")
        f.write("        return description\n")
        f.write("\n\n")
