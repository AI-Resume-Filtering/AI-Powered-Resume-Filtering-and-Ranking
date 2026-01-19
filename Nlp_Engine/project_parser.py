def parse_projects(project_lines: list[str]) -> dict:
    titles = []

    for line in project_lines:
        if len(line.split()) <= 6:
            titles.append(line.strip())

    return {"count": len(set(titles))}
