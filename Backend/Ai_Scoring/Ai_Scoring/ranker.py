# Ai_Scoring/ranker.py
import json
import os

try:
    from .scorer import score_resume
except ImportError:
    from scorer import score_resume


def _resolve_candidate_name(resume_data: dict) -> str:
    """Extract a clean display name from resume data."""
    candidate_name = resume_data.get("contact_info", {}).get("name")
    if candidate_name:
        return candidate_name

    raw_filename = resume_data.get("resume_filename", "Unknown")
    email = resume_data.get("contact_info", {}).get("email", "")

    if raw_filename.startswith("resume_") and len(raw_filename) > 20 and email:
        return ''.join(c for c in email.split('@')[0] if not c.isdigit()).title()

    clean = (raw_filename
             .replace(".txt", "").replace(".pdf", "").replace(".docx", "")
             .replace("_", " ").replace("-", " "))
    return ''.join(c for c in clean if not c.isdigit()).strip().title() or "Unknown"


def process_ranking():
    # --- Path resolution (handles the double Ai_Scoring/Ai_Scoring/ folder) ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    nlp_output_dir = os.path.join(project_root, "Nlp_Engine", "output")
    # ---------------------------------------------------------------------------

    if not os.path.exists(nlp_output_dir):
        print(f"❌ Error: Directory not found: {nlp_output_dir}")
        return

    json_files = [f for f in os.listdir(nlp_output_dir) if f.endswith('.json')]
    if not json_files:
        print(f"⚠️  No JSON files found in {nlp_output_dir}")
        return

    print(f"\n⚙️  Processing {len(json_files)} NLP output file(s)...")

    scored_results = []

    for filename in json_files:
        filepath = os.path.join(nlp_output_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # ── FIX: job_requirements lives at top-level, NOT inside metadata ──
            metadata = {"job_requirements": data.get("job_requirements", {})}
            resumes = data.get("resumes", {})

            for resume_id, resume_data in resumes.items():
                if not resume_data.get("scoring_ready", False):
                    continue

                score, score_details = score_resume(resume_data, metadata, return_details=True)
                job_match = resume_data.get("job_match", {})

                scored_results.append({
                    "rank": 0,
                    "resume_id": resume_id,
                    "candidate_name": _resolve_candidate_name(resume_data),
                    "filename": resume_data.get("resume_filename", "Unknown"),
                    "total_score": score,
                    "score_source": score_details.get("score_source", "blended"),
                    # Tiebreaker fields — reflect real candidate quality differences
                    "_matched_required": len(job_match.get("matched_required_skills", [])),
                    "_experience_years": resume_data.get("experience_years", 0),
                    "_matched_preferred": len(job_match.get("matched_preferred_skills", [])),
                    "_skill_count": len(resume_data.get("skills", [])),
                })

        except Exception as e:
            print(f"⚠️ Could not process {filename}: {str(e)}")

    if not scored_results:
        print("⚠️ No candidates were marked as 'scoring_ready: true' across all files.")
        return

    # ── Multi-key sort: primary = total score, then real quality signals ────────
    # Scores are NEVER modified — tiebreakers use actual extracted candidate data.
    scored_results.sort(key=lambda x: (
        -x["total_score"],
        -x["_matched_required"],
        -x["_experience_years"],
        -x["_matched_preferred"],
        -x["_skill_count"],
    ))
    # ────────────────────────────────────────────────────────────────────────────

    # Assign sequential ranks and strip private tiebreaker fields from output
    for idx, item in enumerate(scored_results, 1):
        item["rank"] = idx
        for key in ["_matched_required", "_experience_years", "_matched_preferred", "_skill_count"]:
            item.pop(key, None)

    output_path = os.path.join(current_dir, "ranked_candidates.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scored_results, f, indent=4)

    print(f"🎉 Success! Ranked list saved to: {output_path}")
    print("\nrank | score     | name")
    print("-" * 40)
    for cand in scored_results:
        print(f"{cand['rank']:<4} | {cand['total_score']:.4f}  | {cand['candidate_name']}")


if __name__ == "__main__":
    process_ranking()