"""
NLP Engine Microservice API
Extracts data from resumes - NO RANKING
Ranking is done by AI Scoring Module
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class NLPMicroservice:
    """
    NLP Extraction Service
    - Extracts skills, experience, education
    - Matches against job requirements
    - Stores data in output folder
    - NO RANKING (AI module handles that)
    """

    def __init__(self):
        """Initialize with internal output directory"""
        self.package_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.package_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)


    def process_request(self,
                       jd_path: str,
                       resume_paths: List[str],
                       request_id: str = None) -> Dict:
        """
        Extract data from resumes (NO RANKING)

        Args:
            jd_path: Path to job description file
            resume_paths: List of resume file paths
            request_id: Optional request ID

        Returns:
            {
                "success": True,
                "request_id": "REQ_xxx",
                "total_resumes": 5,
                "successfully_parsed": 5,
                "output_path": "Nlp_Engine/output/REQ_xxx_nlp_output.json",
                "message": "Data extracted. Ready for AI Scoring."
            }
        """

        request_id = request_id or f"REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n{'='*70}")
        print(f"🚀 NLP EXTRACTION - REQUEST: {request_id}")
        print(f"{'='*70}")

        try:
            # Parse job description first
            jd_data = self._parse_job_description(jd_path)
            if not jd_data:
                return self._error_response("Failed to parse job description")

            # Process each resume
            results = {}
            stats = {"total": 0, "success": 0, "failed": 0}

            for idx, resume_path in enumerate(resume_paths, 1):
                resume_id = f"resume_{str(idx).zfill(3)}"

                try:
                    resume_data = self._process_single_resume(
                        resume_path,
                        resume_id,
                        jd_data
                    )
                    results[resume_id] = resume_data
                    stats["success"] += 1
                    
                except Exception as e:
                    results[resume_id] = self._create_error_resume(
                        resume_id,
                        os.path.basename(resume_path),
                        str(e)
                    )
                    stats["failed"] += 1

                stats["total"] += 1

            # Save results and return response
            output_file = self._save_output(request_id, jd_data, results, stats)
            return self._create_response(request_id, stats, output_file)

        except Exception as e:
            return self._error_response(str(e))


    def _parse_job_description(self, jd_path: str) -> Dict:
        """Parse job description"""
        from .job_description_parser import parse_job_description

        try:
            with open(jd_path, 'r', encoding='utf-8', errors='ignore') as f:
                jd_text = f.read()

            if not jd_text.strip():
                return None

            jd_data = parse_job_description(jd_text)
            print(f"✅ JD Parsed: {jd_data['job_title']}")
            print(f"   Required Skills: {len(jd_data['required_skills'])}")
            print(f"   Min Experience: {jd_data['minimum_experience']} years")

            return jd_data

        except Exception as e:
            print(f"❌ Error parsing JD: {e}")
            return None


    def _process_single_resume(self, resume_path: str, resume_id: str, jd_data: Dict) -> Dict:
        """Process single resume - extract data only"""
        from .text_normalizer import normalize_text
        from .section_detector import detect_sections, get_section_text
        from .contact_extractor import extract_contact_info
        from .skill_extractor import extract_skills
        from .experience_calculator import calculate_experience_years, calculate_skill_experience
        from .education_detector import detect_education_level
        from .output_formatter import format_resume_data

        with open(resume_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_text = f.read()

        if not raw_text.strip():
            raise ValueError("Empty resume file")

        # Extract data
        normalized = normalize_text(raw_text)
        sections = detect_sections(normalized)
        contact_info = extract_contact_info(normalized)

        # Extract skills
        skills_text = get_section_text(sections, "skills") + "\n" + get_section_text(sections, "projects")
        skills_data = extract_skills(skills_text)

        # Extract experience
        experience_text = get_section_text(sections, "experience")
        experience_years = calculate_experience_years(experience_text)

        # NEW: Calculate skill-wise experience
        skills_data["skill_experience"] = calculate_skill_experience(
            experience_text,
            skills_data["skills_list"]
        )

        # Extract education
        education_text = get_section_text(sections, "education")
        education_level = detect_education_level(education_text)

        # Format (includes job match calculation)
        formatted_data = format_resume_data(
            resume_id=resume_id,
            filename=os.path.basename(resume_path),
            contact_info=contact_info,
            skills_data=skills_data,
            experience_years=experience_years,
            education_level=education_level,
            job_requirements=jd_data
        )

        return formatted_data


    def _save_output(self, request_id: str, jd_data: Dict, results: Dict, stats: Dict) -> str:
        """Save extracted data (NO RANKING - order by resume_id)"""
        output_data = {
            "metadata": {
                "request_id": request_id,
                "processed_at": datetime.now().isoformat(),
                "total_resumes": stats["total"],
                "successfully_parsed": stats["success"],
                "failed": stats["failed"]
            },
            "job_requirements": jd_data,
            "resumes": results  # No sorting - keep original order
        }

        output_file = os.path.join(self.output_dir, f"{request_id}_nlp_output.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Data saved: {output_file}")
        return output_file


    def _create_response(self, request_id: str, stats: Dict, output_file: str) -> Dict:
        """Create minimal response"""
        relative_path = os.path.relpath(output_file, start=os.path.dirname(self.package_dir))

        return {
            "success": True,
            "request_id": request_id,
            "total_resumes": stats["total"],
            "successfully_parsed": stats["success"],
            "failed": stats["failed"],
            "output_path": relative_path,
            "message": "NLP extraction complete. Data ready for AI Scoring Module."
        }


    def _create_error_resume(self, resume_id: str, filename: str, error: str) -> Dict:
        """Create error resume entry"""
        return {
            "resume_filename": filename,
            "sequential_id": resume_id.split('_')[-1],
            "error": error,
            "scoring_ready": False,
            "contact_info": {"email": "", "phone": ""},
            "skills": [],
            "skill_categories": {},
            "experience_years": 0,
            "skill_experience": {},
            "education_level": "unknown",
            "job_match": {
                "meets_requirements": False,
                "matched_required_skills": [],
                "matched_preferred_skills": [],
                "missing_required_skills": [],
                "match_percentage": 0.0,
                "experience_match": False,
                "education_match": False
            }
        }


    def _error_response(self, error_msg: str) -> Dict:
        """Return error response"""
        return {
            "success": False,
            "error": error_msg,
            "message": "NLP extraction failed"
        }


# ============================================
# SIMPLE FUNCTION API
# ============================================

def process_resumes(jd_path: str, resume_paths: List[str]) -> Dict:

    service = NLPMicroservice()
    return service.process_request(jd_path, resume_paths)