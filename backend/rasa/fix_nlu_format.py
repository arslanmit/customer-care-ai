import re
from pathlib import Path


def fix_nlu_format(file_path: Path | str) -> None:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split the content into sections by intent
    sections = re.split(
        r"(\n\s*- intent: .+?\n\s*examples: \|\n)", content, flags=re.DOTALL
    )

    # The first item is the version line, keep it as is
    fixed_content = [sections[0]]

    # Process each intent section
    for i in range(1, len(sections), 2):
        if i + 1 >= len(sections):
            fixed_content.append(sections[i])
            break

        intent_header = sections[i]
        examples = sections[i + 1]

        # Split examples into lines and process each line
        lines = examples.split("\n")
        fixed_lines = []

        for line in lines:
            stripped = line.strip()
            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue

            # Check if line is a comment
            if stripped.startswith("#"):
                fixed_lines.append(line)
            # Check if line already starts with a dash
            elif not stripped.startswith("-"):
                fixed_lines.append("      - " + stripped)
            else:
                fixed_lines.append(line)

        # Join the fixed lines back together
        fixed_examples = "\n".join(fixed_lines)
        fixed_content.append(intent_header)
        fixed_content.append(fixed_examples)

    # Join all sections back together
    result = "".join(fixed_content)

    # Write the fixed content back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Successfully fixed formatting in {file_path}")


if __name__ == "__main__":
    nlu_file = Path("data/nlu.yml")
    if nlu_file.exists():
        fix_nlu_format(nlu_file)
    else:
        print(f"Error: {nlu_file} not found")
