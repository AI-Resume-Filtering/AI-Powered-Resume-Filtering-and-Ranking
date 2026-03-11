# Ai_Scoring/ranker.py
import json
import os
import sys

# --- IMPORT FIX (Works for Run Button & Terminal) ---
try:
    from .scorer import score_resume
except ImportError:
    from scorer import score_resume
# ----------------------------------------------------

def select_input_file(search_dir):
    """Provides an interactive CLI menu to select the NLP JSON file."""
    if not os.path.exists(search_dir):
        print(f"❌ Error: Directory not found: {search_dir}")
        return None

    files = [f for f in os.listdir(search_dir) if f.endswith('.json')]

    if not files:
        print(f"⚠️  No JSON files found in {search_dir}")
        return None

    if len(files) == 1:
        print(f"ℹ️  Found 1 file. Auto-selecting: {files[0]}")
        return os.path.join(search_dir, files[0])

    print(f"\n📂 Found {len(files)} parser outputs. Please select one:")
    for idx, filename in enumerate(files, 1):
        print(f"[{idx}] {filename}")

    while True:
        try:
            selection = int(input("👉 Enter number: "))
            if 1 <= selection <= len(files):
                return os.path.join(search_dir, files[selection - 1])
        except ValueError:
            pass

def process_ranking():
    """Main execution function for local testing."""
    # Define path to Nlp_Engine/output
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    nlp_output_dir = os.path.join(project_root, "Nlp_Engine", "output")

    # Select File
    input_file = select_input_file(nlp_output_dir)
    if not input_file:
        return

    # Load Data
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = data.get("metadata", {})
    resumes = data.get("resumes", {})

    print(f"\n⚙️  Processing {len(resumes)} resumes...")

    scored_results = []

    # Score Loop
    for resume_id, resume_data in resumes.items():
        if resume_data.get("scoring_ready", False):
            # CALL SCORER
            score = score_resume(resume_data, metadata)

            scored_results.append({
                "rank": 0,
                "resume_id": resume_id,
                "filename": resume_data.get("resume_filename", "Unknown"),
                "total_score": score
            })

    # Sort High to Low 
    # Cascading Sort: Primary is Total Score, Secondary is raw experience from the JSON
    scored_results.sort(
        key=lambda x: (x["total_score"], resumes[x["resume_id"]].get("experience_years", 0)), 
        reverse=True
    )

    # --- STRICT RANKING (Finite/Unique Declaration) ---
    for idx, item in enumerate(scored_results, 1):
        item["rank"] = idx
    # --------------------------------------------------

    # Save
    output_path = os.path.join(current_dir, "ranked_candidates.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scored_results, f, indent=4)

    print(f"🎉 Success! Ranked list saved to: {output_path}")

    print("\n🏆 --- TOP CANDIDATES ---")
    for cand in scored_results[:3]:
        print(f"#{cand['rank']} | Score: {cand['total_score']} | File: {cand['filename']}")

if __name__ == "__main__":
    process_ranking()
