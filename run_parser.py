"""
Resume Parser - Standalone Runner
Parse PDFs from Samples folder to text files
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Resume_Parser import BatchParser


def main():
    print("="*60)
    print("RESUME PARSER - PDF TO TEXT")
    print("="*60)
    
    parser = BatchParser()
    result = parser.parse_all()
    
    print("\n" + "="*60)
    if result["success"]:
        print("✅ SUCCESS")
        print(f"Resumes parsed: {result['resumes']['parsed']}")
        print(f"JDs parsed: {result['jds']['parsed']}")
        print(f"\nOutput:")
        print(f"  Resumes: {result['resumes']['output_folder']}")
        print(f"  JDs: {result['jds']['output_folder']}")
    else:
        print("❌ FAILED")
        print(f"Error: {result.get('error', 'Unknown')}")
    print("="*60)


if __name__ == "__main__":
    main()
