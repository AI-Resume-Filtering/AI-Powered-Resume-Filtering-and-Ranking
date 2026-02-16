# demo_backend.py
import os
import json

# --- IMPORT YOUR MODULE ---
# This simulates the Backend importing your microservice function
try:
    from Ai_Scoring.scorer import process_resume_batch
except ImportError:
    print("❌ Error: Could not import Ai_Scoring.")
    print("   Make sure this file (demo_backend.py) is in the root directory")
    print("   (AI-Powered-Resume-Filtering-and-Ranking/)")
    exit(1)


# --- HELPER: Create dummy data so the demo runs instantly ---
def create_dummy_nlp_output(filename):
    """
    Creates a fake NLP output file so we have something to rank.
    """
    path = os.path.join("Nlp_Engine", "output", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    fake_data = {
        "resumes": {
            "101": {
                "resume_filename": "Alice_Python_Dev.pdf",
                "skills": ["python", "flask", "django", "aws"],
                "experience_years": 3,
                "education_level": "bachelors",
                "job_match": {"match_percentage": 85.0},
                "scoring_ready": True
            },
            "102": {
                "resume_filename": "Bob_Manager.pdf",
                "skills": ["leadership", "excel"],
                "experience_years": 10,
                "education_level": "masters",
                "job_match": {"match_percentage": 40.0},
                "scoring_ready": True
            },
            "103": {
                "resume_filename": "Charlie_Fresher.pdf",
                "skills": ["python", "html"],
                "experience_years": 0,
                "education_level": "bachelors",
                "job_match": {"match_percentage": 60.0},
                "scoring_ready": True
            }
        }
    }

    with open(path, "w") as f:
        json.dump(fake_data, f, indent=4)
    print(f"✅ (Setup) Created test file: {path}")


# ==========================================
# 🚀 THE DEMO (Backend Logic)
# ==========================================
def main():
    target_filename = "demo_test_batch.json"

    # 1. Setup Data (You can remove this if you have real files)
    create_dummy_nlp_output(target_filename)

    # 2. Define Job Requirements (Metadata)
    # Backend tells us: "We need a Python Dev with 2+ years exp"
    print("\n🔹 Backend: Sending Job Data...")
    job_data = {
        "minimum_experience": 2,
        "required_skills": ["python"],
        "preferred_skills": ["aws"],
        "required_education": "bachelors"
    }

    # 3. CALL YOUR FUNCTION
    print(f"🔹 Backend: Calling Ai_Scoring module...")

    # This is the ONE LINE the backend team needs to use
    ranked_results = process_resume_batch(target_filename, job_data)

    # 4. Display Results (Simulating Frontend)
    print("\n🏆 --- FINAL RANKED LIST (JSON) --- 🏆")
    print(json.dumps(ranked_results, indent=4))


if __name__ == "__main__":
    main()