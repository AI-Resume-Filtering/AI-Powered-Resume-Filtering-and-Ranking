# project_extractor.py

import re

def extract_project_metrics(project_lines: list[str]) -> dict:
    project_titles = []
    metric_values = []

    for line in project_lines:
        l = line.lower()

        # Detect metric values (percentages)
        metrics = re.findall(r'(\d+)\s*%', l)
        for m in metrics:
            metric_values.append(int(m))

        # Detect project title (heuristic)
        if (
            "%" not in line
            and "impact" not in l
            and "accuracy" not in l
            and len(line.split()) <= 8
        ):
            project_titles.append(line)

    project_count = len(project_titles)

    if metric_values:
        avg_score = sum(metric_values) / len(metric_values)
    else:
        avg_score = 0

    return {
        "count": project_count,
        "average_project_score": round(avg_score, 2)
    }
