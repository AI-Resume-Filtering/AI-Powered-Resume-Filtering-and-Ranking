import os
import sys
import argparse
import json
import shutil

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def main():
    parser = argparse.ArgumentParser(
        description="Test the full pipeline: Parse -> NLP -> Score",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--resumes", "-r",
        nargs="+",
        required=True,
        help="One or more PDF resume file paths.\nExample: --resumes C:/files/john.pdf C:/files/jane.pdf"
    )
    parser.add_argument(
        "--jd", "-j",
        required=True,
        help="Path to the job description file (.txt or .pdf).\nExample: --jd C:/files/data_scientist_jd.txt"
    )
    parser.add_argument(
        "--step",
        choices=["parse", "nlp", "score", "all"],
        default="all",
        help=(
            "Which step to run:\n"
            "  parse  - Resume Parser only (PDF -> cleaned text)\n"
            "  nlp    - NLP extraction only (requires parsed text)\n"
            "  score  - AI Scoring only (requires existing NLP output)\n"
            "  all    - Full pipeline (default)"
        )
    )
    args = parser.parse_args()

    # Validate input files
    for resume in args.resumes:
        if not os.path.exists(resume):
            print(f"ERROR: Resume file not found: {resume}")
            sys.exit(1)

    if not os.path.exists(args.jd):
        print(f"ERROR: JD file not found: {args.jd}")
        sys.exit(1)

    step = args.step

    # Step 1: Parse resumes (PDF/image -> clean text)
    parsed_txt_paths = []
    if step in ("parse", "all"):
        print("\n" + "="*60)
        print("STEP 1: RESUME PARSER")
        print("="*60)

        from Resume_Parser.resume_parser import ResumeParser
        rp = ResumeParser()

        tmp_dir = os.path.join(PROJECT_ROOT, "Backend", "instance", "storage", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        for resume_path in args.resumes:
            fname = os.path.splitext(os.path.basename(resume_path))[0]
            out_txt = os.path.join(tmp_dir, f"{fname}.txt")
            print(f"  Parsing: {os.path.basename(resume_path)} ...", end=" ")
            try:
                text = rp.parse(resume_path)
                with open(out_txt, "w", encoding="utf-8") as f:
                    f.write(text)
                parsed_txt_paths.append(out_txt)
                print(f"Done  ({len(text)} chars)")
            except Exception as e:
                print(f"FAILED: {e}")
                sys.exit(1)

        print(f"\nParsed text saved in: {tmp_dir}")

        if step == "parse":
            for p in parsed_txt_paths:
                print(f"\n--- Preview: {os.path.basename(p)} ---")
                with open(p, encoding="utf-8") as f:
                    print(f.read()[:800])
            return

    # Prepare JD path (copy to tmp if it's a PDF)
    jd_path = args.jd
    if jd_path.lower().endswith(".pdf"):
        from Resume_Parser.resume_parser import ResumeParser
        tmp_dir = os.path.join(PROJECT_ROOT, "Backend", "instance", "storage", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        jd_txt_path = os.path.join(tmp_dir, "jd_input.txt")
        print("\nConverting JD PDF to text...")
        rp = ResumeParser()
        jd_text = rp.parse(jd_path)
        with open(jd_txt_path, "w", encoding="utf-8") as f:
            f.write(jd_text)
        jd_path = jd_txt_path

    # Step 2: NLP extraction
    nlp_output_file = None
    if step in ("nlp", "all"):
        print("\n" + "="*60)
        print("STEP 2: NLP ENGINE")
        print("="*60)

        if step == "nlp" and not parsed_txt_paths:
            # If running nlp only, resumes are already text files
            parsed_txt_paths = args.resumes

        from Nlp_Engine.Nlp_service import NLPMicroservice
        nlp = NLPMicroservice()
        result = nlp.process_request(
            jd_path=jd_path,
            resume_paths=parsed_txt_paths
        )

        if not result.get("success"):
            print(f"\nNLP FAILED: {result.get('error', 'Unknown error')}")
            sys.exit(1)

        nlp_output_file = os.path.join(
            PROJECT_ROOT,
            result.get("output_path", "")
        )
        nlp_output_file = os.path.normpath(nlp_output_file)
        print(f"\nNLP output: {nlp_output_file}")

        if step == "nlp":
            with open(nlp_output_file, encoding="utf-8") as f:
                data = json.load(f)
            for rid, rdata in data.get("resumes", {}).items():
                print(f"\n--- {rid} ---")
                print(f"  Skills:           {rdata.get('skills', [])}")
                print(f"  Experience Years: {rdata.get('experience_years')}")
                print(f"  Skill Experience: {rdata.get('skill_experience')}")
                print(f"  Education:        {rdata.get('education_level')}")
                print(f"  Match %:          {rdata.get('job_match', {}).get('match_percentage')}%")
            return

    # Step 3: AI Scoring
    if step in ("score", "all"):
        print("\n" + "="*60)
        print("STEP 3: AI SCORING & RANKING")
        print("="*60)

        if step == "score":
            # Find the most recent NLP output file automatically
            nlp_out_dir = os.path.join(PROJECT_ROOT, "Nlp_Engine", "output")
            json_files = sorted(
                [f for f in os.listdir(nlp_out_dir) if f.endswith(".json")],
                reverse=True
            )
            if not json_files:
                print("No NLP output files found. Run with --step nlp first.")
                sys.exit(1)
            nlp_output_file = os.path.join(nlp_out_dir, json_files[0])
            print(f"Using latest NLP output: {json_files[0]}")

        with open(nlp_output_file, encoding="utf-8") as f:
            output_data = json.load(f)

        job_reqs = output_data.get("job_requirements", {})
        scoring_metadata = {"job_requirements": job_reqs}

        from Ai_Scoring.Ai_Scoring.scorer import process_resume_batch
        filename = os.path.basename(nlp_output_file)
        scored = process_resume_batch(filename, scoring_metadata)

        if scored and "error" in scored[0]:
            print(f"SCORING FAILED: {scored[0]['error']}")
            sys.exit(1)

        print(f"\nJob: {job_reqs.get('job_title', 'N/A')}")
        print(f"Required Skills: {job_reqs.get('required_skills', [])}")
        print(f"Min Experience:  {job_reqs.get('minimum_experience')} years\n")
        print(f"{'Rank':<6} {'Score':<10} {'Skills Match':<15} {'Exp (yrs)':<12} {'File'}")
        print("-" * 65)
        for c in scored:
            details = c.get("details", {})
            print(
                f"{c['rank']:<6} "
                f"{c['total_score']:<10.4f} "
                f"{details.get('skills_match', 0):<15.1f} "
                f"{details.get('experience_years', 0):<12} "
                f"{c['filename']}"
            )

        output_json = os.path.join(PROJECT_ROOT, "Ai_Scoring", "Ai_Scoring", "ranked_candidates.json")
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(scored, f, indent=4)
        print(f"\nFull results saved: {output_json}")


if __name__ == "__main__":
    main()
