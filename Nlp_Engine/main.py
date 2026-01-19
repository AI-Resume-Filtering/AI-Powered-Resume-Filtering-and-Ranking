from nlp_pipeline import process_resume_nlp

with open("resume.txt", "r", encoding="utf-8") as f:
    resume_text = f.read()

print(process_resume_nlp(resume_text))
