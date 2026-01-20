# scoring_engine/ranker.py

def rank_resumes(scored_resumes: list[dict]) -> list[dict]:
    """
    Sorts resumes in descending order of final_score.
    """
    return sorted(
        scored_resumes,
        key=lambda r: r["final_score"],
        reverse=True
    )