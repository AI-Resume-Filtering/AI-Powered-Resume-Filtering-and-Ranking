"""
Batch Resume Processor
Parses job description and compares resumes against requirements
"""

import os
import json
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

from .config import (
    INPUT_FOLDER,
    OUTPUT_FILE,
    JOB_DESCRIPTION_FILE,  # NEW
    RESUME_ID_PREFIX,
    ID_PADDING,
    CONTINUE_ON_ERROR,
    ERROR_LOG_FILE
)

from .text_normalizer import normalize_text
from .section_detector import detect_sections, get_section_text
from .contact_extractor import extract_contact_info
from .skill_extractor import extract_skills
from .experience_calculator import calculate_experience_years
from .education_detector import detect_education_level
from .job_description_parser import parse_job_description  # NEW
from .output_formatter import format_resume_data, format_error_resume


class NLPBatchProcessor:
    """
    Processes multiple resumes and compares against job requirements
    """

    def __init__(self, input_folder=None, output_file=None, jd_file=None):
        """
        Initialize with input/output paths
        """
        self.input_folder = input_folder or INPUT_FOLDER
        self.output_file = output_file or OUTPUT_FILE
        self.jd_file = jd_file or JOB_DESCRIPTION_FILE

        # Setup output directory and initialize tracking
        Path(os.path.dirname(self.output_file)).mkdir(parents=True, exist_ok=True)
        self.job_requirements = None
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "qualified": 0,
            "errors": []
        }

        print("="*70)
        print("🚀 NLP BATCH PROCESSOR INITIALIZED")
        print("="*70)
        print(f"📂 Input Folder: {self.input_folder}")
        print(f"📄 Job Description: {self.jd_file}")
        print(f"📄 Output File: {self.output_file}")
        print("="*70 + "\n")

    def process_folder(self):
        """
        Main pipeline: parse JD then process all resumes
        3. Compare each resume with JD
        4. Rank by match percentage
        """

        # STEP 1: Parse Job Description
        print("="*70)
        print("STEP 1: PARSING JOB DESCRIPTION")
        print("="*70)

        self.job_requirements = self._parse_job_description()

        if not self.job_requirements:
            print("❌ Failed to parse job description. Cannot proceed.")
            return None

        print(f"✅ Job Title: {self.job_requirements['job_title']}")
        print(f"✅ Required Skills: {len(self.job_requirements['required_skills'])}")
        print(f"✅ Preferred Skills: {len(self.job_requirements['preferred_skills'])}")
        print(f"✅ Min Experience: {self.job_requirements['minimum_experience']} years")
        print(f"✅ Education: {self.job_requirements['required_education']}")

        # Get all resume files and start processing
        print("\n" + "=" * 70)
        print("Processing resumes")
        print("=" * 70)

        resume_files = self._get_resume_files()

        if not resume_files:
            print(f"❌ No resume files found in: {self.input_folder}")
            return None

        print(f"📊 Found {len(resume_files)} resume files")
        print(f"🔄 Starting processing...\n")

        # Process each resume with progress tracking
        results = {}

        with tqdm(total=len(resume_files), desc="Processing Resumes", ncols=100) as pbar:
            for idx, file_path in enumerate(resume_files, 1):
                resume_id = f"{RESUME_ID_PREFIX}{str(idx).zfill(ID_PADDING)}"
                filename = os.path.basename(file_path)

                try:
                    # Process single resume
                    resume_data = self._process_single_resume(file_path, resume_id, filename)
                    results[resume_id] = resume_data
                    self.stats["success"] += 1

                    # Count qualified candidates
                    if resume_data.get("job_match", {}).get("meets_requirements"):
                        self.stats["qualified"] += 1

                except Exception as e:
                    # Handle error
                    error_msg = str(e)
                    results[resume_id] = format_error_resume(resume_id, filename, error_msg)
                    self.stats["failed"] += 1
                    self.stats["errors"].append({
                        "resume_id": resume_id,
                        "filename": filename,
                        "error": error_msg
                    })

                    if not CONTINUE_ON_ERROR:
                        pbar.close()
                        raise

                finally:
                    self.stats["total"] += 1
                    pbar.update(1)

        # Sort by match score
        ranked_results = self._rank_resumes(results)

        # Save results and statistics
        output_path = self._save_results(ranked_results)

        # Save errors
        if self.stats["errors"]:
            self._save_errors()

        # Print summary
        self._print_summary()

        return output_path

    def _parse_job_description(self) -> dict:
        """Parse job description file"""
        try:
            if not os.path.exists(self.jd_file):
                print(f"⚠️  Job description file not found: {self.jd_file}")
                print(f"⚠️  Please create the file with job requirements")
                return None

            with open(self.jd_file, 'r', encoding='utf-8', errors='ignore') as f:
                jd_text = f.read()

            if not jd_text.strip():
                print("⚠️  Job description file is empty")
                return None

            # Parse JD
            job_requirements = parse_job_description(jd_text)
            return job_requirements

        except Exception as e:
            print(f"❌ Error parsing job description: {e}")
            return None

    def _get_resume_files(self):
        """Get all TXT files from input folder"""
        if not os.path.exists(self.input_folder):
            return []

        files = []
        for file in os.listdir(self.input_folder):
            if file.endswith('.txt'):
                files.append(os.path.join(self.input_folder, file))

        return sorted(files)

    def _process_single_resume(self, file_path: str, resume_id: str, filename: str) -> dict:
        """Process a single resume"""

        # Read file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_text = f.read()

        if not raw_text.strip():
            raise ValueError("Empty file")

        # Step 1: Normalize text
        normalized = normalize_text(raw_text)

        # Step 2: Detect sections
        sections = detect_sections(normalized)

        # Step 3: Extract contact info
        contact_info = extract_contact_info(normalized)

        # Step 4: Extract skills
        skills_text = get_section_text(sections, "skills") + "\n" + get_section_text(sections, "projects")
        skills_data = extract_skills(skills_text)

        # Step 5: Calculate experience
        experience_text = get_section_text(sections, "experience")
        experience_years = calculate_experience_years(experience_text)

        # Step 6: Detect education
        education_text = get_section_text(sections, "education")
        education_level = detect_education_level(education_text)

        # Step 7: Format output (with JD comparison)
        formatted_data = format_resume_data(
            resume_id=resume_id,
            filename=filename,
            contact_info=contact_info,
            skills_data=skills_data,
            experience_years=experience_years,
            education_level=education_level,
            job_requirements=self.job_requirements
        )

        return formatted_data

    def _rank_resumes(self, results: dict) -> dict:
        """
        Rank resumes by match percentage

        Order:
        1. Qualified candidates (meet all requirements) - sorted by match %
        2. Non-qualified candidates - sorted by match %
        """
        qualified = {}
        not_qualified = {}

        for resume_id, data in results.items():
            if data.get("scoring_ready"):
                if data["job_match"]["meets_requirements"]:
                    qualified[resume_id] = data
                else:
                    not_qualified[resume_id] = data
            else:
                not_qualified[resume_id] = data  # Errors go to bottom

        # Sort by match percentage
        qualified_sorted = dict(sorted(
            qualified.items(),
            key=lambda x: x[1].get("job_match", {}).get("match_percentage", 0),
            reverse=True
        ))

        not_qualified_sorted = dict(sorted(
            not_qualified.items(),
            key=lambda x: x[1].get("job_match", {}).get("match_percentage", 0),
            reverse=True
        ))

        # Combine: Qualified first, then not qualified
        ranked = {**qualified_sorted, **not_qualified_sorted}

        return ranked

    def _save_results(self, results: dict) -> str:
        """Save all results to JSON"""
        output_data = {
            "metadata": {
                "total_resumes": self.stats["total"],
                "successfully_parsed": self.stats["success"],
                "failed": self.stats["failed"],
                "qualified_candidates": self.stats["qualified"],  # NEW
                "processed_at": datetime.now().isoformat(),
                "input_folder": self.input_folder
            },
            "job_requirements": self.job_requirements,
            "resumes": results
        }

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        return self.output_file

    def _save_errors(self):
        """Save errors to log file"""
        with open(ERROR_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.stats["errors"], f, indent=2)

    def _print_summary(self):
        """Print processing summary"""
        print("\n" + "="*70)
        print("📊 PROCESSING SUMMARY")
        print("="*70)
        print(f"Total Resumes: {self.stats['total']}")
        print(f"✅ Success: {self.stats['success']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"🎯 Qualified: {self.stats['qualified']}")  # NEW
        print(f"📈 Success Rate: {(self.stats['success']/self.stats['total']*100):.1f}%")
        print(f"🎯 Qualification Rate: {(self.stats['qualified']/self.stats['success']*100):.1f}%")  # NEW
        print(f"\n💾 Output saved to: {self.output_file}")

        if self.stats["errors"]:
            print(f"⚠️  Errors logged to: {ERROR_LOG_FILE}")

        print("\n✅ RESUMES RANKED BY MATCH PERCENTAGE")
        print("✅ READY FOR AI SCORING MODULE")
        print("="*70)