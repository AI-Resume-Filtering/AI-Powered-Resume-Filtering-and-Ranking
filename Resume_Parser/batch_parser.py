import os
from .resume_parser import ResumeParser


class BatchParser:

    def __init__(self, samples_folder: str = None):

        self.parser = ResumeParser()

        self.package_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.package_dir)
        self.input_root, self.resumes_folder, self.jd_folder = self._resolve_input_folders(
            samples_folder
        )

        self.output_resumes = os.path.join(self.package_dir, "parsed_resumes")
        self.output_jd = os.path.join(self.package_dir, "Parsed_JD")

        os.makedirs(self.output_resumes, exist_ok=True)
        os.makedirs(self.output_jd, exist_ok=True)

        print(f"✓ Batch Parser Initialized")
        print(f"  Input root: {self.input_root}")
        print(f"  Input - Resumes: {self.resumes_folder}")
        print(f"  Input - JDs: {self.jd_folder}")
        print(f"  Output - Resumes: {self.output_resumes}")
        print(f"  Output - JDs: {self.output_jd}")

    def _resolve_input_folders(self, input_root: str = None) -> tuple[str, str, str]:
        roots = [input_root] if input_root else [
            os.path.join(self.project_root, "Samples"),
            os.path.join(self.project_root, "data"),
        ]

        candidate_pairs = [
            ("Resumes", "Job_Descriptions"),
            ("resumes", "job_descriptions"),
        ]

        for root in roots:
            if not root:
                continue
            for resumes_name, jd_name in candidate_pairs:
                resumes_folder = os.path.join(root, resumes_name)
                jd_folder = os.path.join(root, jd_name)
                if os.path.isdir(resumes_folder) or os.path.isdir(jd_folder):
                    return root, resumes_folder, jd_folder

        default_root = roots[0]
        return (
            default_root,
            os.path.join(default_root, "Resumes"),
            os.path.join(default_root, "Job_Descriptions"),
        )
    
    
    def parse_all_resumes(self) -> dict:

        if not os.path.exists(self.resumes_folder):
            return {
                "success": False,
                "error": f"Resumes folder not found: {self.resumes_folder}",
                "message": "Create Samples/Resumes folder and add PDF files"
            }
        
        pdf_files = [f for f in os.listdir(self.resumes_folder) 
                     if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            return {
                "success": False,
                "error": f"No PDF files found in {self.resumes_folder}",
                "message": "Add resume PDF files to Samples/Resumes folder"
            }
        
        print(f"\n{'='*60}")
        print(f"PARSING RESUMES")
        print(f"{'='*60}")
        print(f"Found {len(pdf_files)} PDF files")
        
        parsed_files = []
        failed = 0
        
        for idx, file_name in enumerate(pdf_files, 1):
            file_path = os.path.join(self.resumes_folder, file_name)
            
            try:
                print(f"  [{idx}/{len(pdf_files)}] Parsing: {file_name}...", end=" ")
                
                # Parse PDF
                text = self.parser.parse(file_path)
                
                # Create output filename
                txt_file_name = os.path.splitext(file_name)[0] + ".txt"
                output_path = os.path.join(self.output_resumes, txt_file_name)
                
                # Save to text file
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                
                parsed_files.append(txt_file_name)
                print("✓")
                
            except Exception as e:
                print(f"✗ Error: {e}")
                failed += 1
        
        print(f"\n✓ Parsed {len(parsed_files)}/{len(pdf_files)} resumes")
        print(f"✓ Saved to: {self.output_resumes}")
        
        return {
            "success": True,
            "total": len(pdf_files),
            "parsed": len(parsed_files),
            "failed": failed,
            "output_folder": self.output_resumes,
            "files": parsed_files
        }
    
    
    def parse_all_jds(self) -> dict:

        if not os.path.exists(self.jd_folder):
            return {
                "success": False,
                "error": f"JD folder not found: {self.jd_folder}",
                "message": "Create Samples/Job_Descriptions folder and add PDF files"
            }
        
        pdf_files = [f for f in os.listdir(self.jd_folder) 
                     if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            return {
                "success": False,
                "error": f"No PDF files found in {self.jd_folder}",
                "message": "Add JD PDF files to Samples/Job_Descriptions folder"
            }
        
        print(f"\n{'='*60}")
        print(f"PARSING JOB DESCRIPTIONS")
        print(f"{'='*60}")
        print(f"Found {len(pdf_files)} PDF files")
        
        parsed_files = []
        failed = 0
        
        for idx, file_name in enumerate(pdf_files, 1):
            file_path = os.path.join(self.jd_folder, file_name)
            
            try:
                print(f"  [{idx}/{len(pdf_files)}] Parsing: {file_name}...", end=" ")
                
                # Parse PDF
                text = self.parser.parse(file_path)
                
                # Create output filename
                txt_file_name = os.path.splitext(file_name)[0] + ".txt"
                output_path = os.path.join(self.output_jd, txt_file_name)
                
                # Save to text file
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                
                parsed_files.append(txt_file_name)
                print("✓")
                
            except Exception as e:
                print(f"✗ Error: {e}")
                failed += 1
        
        print(f"\n✓ Parsed {len(parsed_files)}/{len(pdf_files)} JDs")
        print(f"✓ Saved to: {self.output_jd}")
        
        return {
            "success": True,
            "total": len(pdf_files),
            "parsed": len(parsed_files),
            "failed": failed,
            "output_folder": self.output_jd,
            "files": parsed_files
        }
    
    
    def parse_all(self) -> dict:

        print(f"\n{'='*60}")
        print(f"BATCH PARSING - RESUMES & JDs")
        print(f"{'='*60}")
        
        # Parse resumes
        resume_result = self.parse_all_resumes()
        
        # Parse JDs
        jd_result = self.parse_all_jds()
        
        print(f"\n{'='*60}")
        print(f"BATCH PARSING COMPLETE")
        print(f"{'='*60}")
        print(f"✓ Resumes: {resume_result.get('parsed', 0)} parsed")
        print(f"✓ JDs: {jd_result.get('parsed', 0)} parsed")
        print(f"{'='*60}\n")
        
        return {
            "success": resume_result.get("success") and jd_result.get("success"),
            "resumes": resume_result,
            "jds": jd_result
        }


# Quick test
if __name__ == "__main__":
    parser = BatchParser()
    result = parser.parse_all()
    
    if result["success"]:
        print("✓ All files parsed successfully!")
    else:
        print("✗ Some files failed to parse")
