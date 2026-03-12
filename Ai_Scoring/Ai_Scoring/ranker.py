# Ai_Scoring/ranker.py
import json
import os

try:
    from .scorer import score_resume
except ImportError:
    from scorer import score_resume


def process_ranking():
    # --- EXACT PATH RESOLUTION (Handles the double folder) ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(parent_dir)

    nlp_output_dir = os.path.join(project_root, "Nlp_Engine", "output")
    # ---------------------------------------------------------

    if not os.path.exists(nlp_output_dir):
        print(f"❌ Error: Directory not found: {nlp_output_dir}")
        return

    # Find ALL json files in the folder
    json_files = [f for f in os.listdir(nlp_output_dir) if f.endswith('.json')]

    if not json_files:
        print(f"⚠️  No JSON files found in {nlp_output_dir}")
        return

    print(f"\n⚙️  Processing {len(json_files)} resume files from NLP Output...")

    scored_results = []

    # Loop through EVERY single file in the folder
    for filename in json_files:
        filepath = os.path.join(nlp_output_dir, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            metadata = data.get("metadata", {})
            resumes = data.get("resumes", {})

            for resume_id, resume_data in resumes.items():
                if resume_data.get("scoring_ready", False):
                    score = score_resume(resume_data, metadata)

                    # Extract Clean Name
                    raw_filename = resume_data.get("resume_filename", "Unknown")
                    email = resume_data.get("contact_info", {}).get("email", "")
                    candidate_name = resume_data.get("contact_info", {}).get("name")

                    if not candidate_name:
                        if raw_filename.startswith("resume_") and len(raw_filename) > 20 and email:
                            candidate_name = ''.join([i for i in email.split('@')[0] if not i.isdigit()]).title()
                        else:
                            clean = raw_filename.replace(".txt", "").replace(".pdf", "").replace(".docx", "").replace(
                                "_", " ").replace("-", " ")
                            candidate_name = ''.join([i for i in clean if not i.isdigit()]).strip().title()

                    scored_results.append({
                        "rank": 0,
                        "resume_id": resume_id,
                        "candidate_name": candidate_name or "Unknown",
                        "filename": raw_filename,
                        "total_score": score
                    })
        except Exception as e:
            print(f"⚠️ Could not process {filename}: {str(e)}")

    if not scored_results:
        print("⚠️ No candidates were marked as 'scoring_ready: true' across all files.")
        return

    # 1. Sort the massive combined list High to Low
    scored_results.sort(
        key=lambda x: x["total_score"],
        reverse=True
    )

    # 2. --- 🔥 STRICT UNIQUE SCORE ENFORCER 🔥 ---
    # If a score is identical to the one above it, subtract a microscopic fraction to break the tie!
    for i in range(1, len(scored_results)):
        if scored_results[i]["total_score"] >= scored_results[i - 1]["total_score"]:
            scored_results[i]["total_score"] = scored_results[i - 1]["total_score"] - 0.0001
    # ---------------------------------------------

    # 3. Assign strict ranks
    for idx, item in enumerate(scored_results, 1):
        item["rank"] = idx

    output_path = os.path.join(current_dir, "ranked_candidates.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scored_results, f, indent=4)

    print(f"🎉 Success! Combined ranked list saved to: {output_path}")

    # --- EXACT FORMAT REQUESTED ---
    print("\nrank | score     | name")
    print("-" * 40)
    for cand in scored_results:
        print(f"{cand['rank']:<4} | {cand['total_score']:.4f}  | {cand['candidate_name']}")


if __name__ == "__main__":
    process_ranking()