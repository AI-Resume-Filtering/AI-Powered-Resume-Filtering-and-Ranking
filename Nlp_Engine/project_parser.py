import re

def parse_projects(project_lines: list[str]) -> dict:
    project_count = 0

    for line in project_lines:
        clean = line.strip()
        if not clean:
            continue

        lower = clean.lower()

        # Ignore metadata lines
        if lower.startswith((
            "tech stack",
            "technologies",
            "tools",
            "libraries",
            "features",
            "my contribution",
            "current progress"
        )):
            continue

        # Case 1: Bullet-based project start
        if clean.startswith(("➢", "•", "-", "*")):
            project_count += 1
            continue

        # Case 2: Numbered project start (1., 2., 3.)
        if re.match(r"^\d+\.\s+", clean):
            project_count += 1
            continue

    return {"count": project_count}
