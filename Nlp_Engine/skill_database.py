"""
Comprehensive Skill Database
All possible skills for accurate extraction

Categories:
1. Programming Languages
2. AI/ML Technologies
3. Databases
4. Backend Frameworks
5. Frontend Technologies
6. DevOps & Tools
7. Cloud Platforms
8. Mobile Development
"""

# ============================================
# SKILL DATABASE WITH CATEGORIES & SYNONYMS
# ============================================

SKILL_DATABASE = {

    # ========================================
    # PROGRAMMING LANGUAGES
    # ========================================
    "python": {
        "category": "programming_language",
        "synonyms": ["python3", "py", "python 3", "python2"],
        "importance": "high"
    },
    "java": {
        "category": "programming_language",
        "synonyms": ["core java", "java se", "java ee", "j2ee", "jdk", "java 8", "java8"],
        "importance": "high"
    },
    "javascript": {
        "category": "programming_language",
        "synonyms": ["js", "es6", "ecmascript", "node.js", "nodejs", "node js"],
        "importance": "high"
    },
    "c++": {
        "category": "programming_language",
        "synonyms": ["cpp", "c plus plus", "cplusplus", "c++11", "c++14"],
        "importance": "high"
    },
    "c": {
        "category": "programming_language",
        "synonyms": ["c programming", "ansi c"],
        "importance": "medium"
    },
    "c#": {
        "category": "programming_language",
        "synonyms": ["csharp", "c sharp"],
        "importance": "high"
    },
    "go": {
        "category": "programming_language",
        "synonyms": ["golang"],
        "importance": "medium"
    },
    "rust": {
        "category": "programming_language",
        "synonyms": [],
        "importance": "medium"
    },
    "kotlin": {
        "category": "programming_language",
        "synonyms": [],
        "importance": "medium"
    },
    "swift": {
        "category": "programming_language",
        "synonyms": [],
        "importance": "medium"
    },
    "ruby": {
        "category": "programming_language",
        "synonyms": [],
        "importance": "medium"
    },
    "php": {
        "category": "programming_language",
        "synonyms": [],
        "importance": "medium"
    },
    "r": {
        "category": "programming_language",
        "synonyms": ["r programming"],
        "importance": "medium"
    },
    "scala": {
        "category": "programming_language",
        "synonyms": [],
        "importance": "medium"
    },

    # ========================================
    # AI/ML TECHNOLOGIES
    # ========================================
    "machine learning": {
        "category": "ai_ml",
        "synonyms": ["ml", "machine-learning"],
        "importance": "very_high"
    },
    "deep learning": {
        "category": "ai_ml",
        "synonyms": ["dl"],
        "importance": "very_high"
    },
    "artificial intelligence": {
        "category": "ai_ml",
        "synonyms": ["ai"],
        "importance": "very_high"
    },
    "natural language processing": {
        "category": "ai_ml",
        "synonyms": ["nlp", "text mining", "text analytics"],
        "importance": "very_high"
    },
    "nlp": {
        "category": "ai_ml",
        "synonyms": ["natural language processing"],
        "importance": "very_high"
    },
    "computer vision": {
        "category": "ai_ml",
        "synonyms": ["cv", "image processing"],
        "importance": "very_high"
    },
    "tensorflow": {
        "category": "ai_ml",
        "synonyms": ["tensor flow", "tf"],
        "importance": "high"
    },
    "pytorch": {
        "category": "ai_ml",
        "synonyms": ["torch"],
        "importance": "high"
    },
    "keras": {
        "category": "ai_ml",
        "synonyms": [],
        "importance": "high"
    },
    "scikit-learn": {
        "category": "ai_ml",
        "synonyms": ["sklearn", "scikit learn"],
        "importance": "high"
    },
    "opencv": {
        "category": "ai_ml",
        "synonyms": ["open cv"],
        "importance": "high"
    },
    "spacy": {
        "category": "ai_ml",
        "synonyms": [],
        "importance": "high"
    },
    "nltk": {
        "category": "ai_ml",
        "synonyms": ["natural language toolkit"],
        "importance": "high"
    },
    "hugging face": {
        "category": "ai_ml",
        "synonyms": ["transformers", "huggingface"],
        "importance": "high"
    },
    "langchain": {
        "category": "ai_ml",
        "synonyms": [],
        "importance": "high"
    },
    "llm": {
        "category": "ai_ml",
        "synonyms": ["large language model"],
        "importance": "very_high"
    },
    "gpt": {
        "category": "ai_ml",
        "synonyms": ["chatgpt", "gpt-3", "gpt-4"],
        "importance": "high"
    },
    "bert": {
        "category": "ai_ml",
        "synonyms": [],
        "importance": "high"
    },

    # ========================================
    # DATABASES
    # ========================================
    "sql": {
        "category": "database",
        "synonyms": ["structured query language"],
        "importance": "high"
    },
    "mysql": {
        "category": "database",
        "synonyms": ["my sql"],
        "importance": "high"
    },
    "postgresql": {
        "category": "database",
        "synonyms": ["postgres", "psql"],
        "importance": "high"
    },
    "mongodb": {
        "category": "database",
        "synonyms": ["mongo db", "mongo"],
        "importance": "high"
    },
    "oracle": {
        "category": "database",
        "synonyms": ["oracledb", "oracle database"],
        "importance": "high"
    },
    "cassandra": {
        "category": "database",
        "synonyms": [],
        "importance": "medium"
    },
    "redis": {
        "category": "database",
        "synonyms": [],
        "importance": "medium"
    },
    "elasticsearch": {
        "category": "database",
        "synonyms": ["elastic search"],
        "importance": "medium"
    },
    "dynamodb": {
        "category": "database",
        "synonyms": ["dynamo db"],
        "importance": "medium"
    },
    "firebase": {
        "category": "database",
        "synonyms": [],
        "importance": "medium"
    },

    # ========================================
    # BACKEND FRAMEWORKS
    # ========================================
    "flask": {
        "category": "backend",
        "synonyms": ["flask framework", "python flask"],
        "importance": "high"
    },
    "django": {
        "category": "backend",
        "synonyms": ["django framework"],
        "importance": "high"
    },
    "spring": {
        "category": "backend",
        "synonyms": ["spring boot", "spring framework", "springboot"],
        "importance": "high"
    },
    "express": {
        "category": "backend",
        "synonyms": ["expressjs", "express.js"],
        "importance": "high"
    },
    "fastapi": {
        "category": "backend",
        "synonyms": ["fast api"],
        "importance": "high"
    },
    "asp.net": {
        "category": "backend",
        "synonyms": ["asp net", "dotnet"],
        "importance": "high"
    },
    "ruby on rails": {
        "category": "backend",
        "synonyms": ["rails", "ror"],
        "importance": "medium"
    },
    "laravel": {
        "category": "backend",
        "synonyms": [],
        "importance": "medium"
    },
    "jsp": {
        "category": "backend",
        "synonyms": ["javaserver pages"],
        "importance": "medium"
    },
    "servlets": {
        "category": "backend",
        "synonyms": ["java servlets", "servlet"],
        "importance": "medium"
    },
    "jdbc": {
        "category": "backend",
        "synonyms": ["java database connectivity"],
        "importance": "medium"
    },

    # ========================================
    # FRONTEND TECHNOLOGIES
    # ========================================
    "html": {
        "category": "frontend",
        "synonyms": ["html5"],
        "importance": "high"
    },
    "css": {
        "category": "frontend",
        "synonyms": ["css3", "cascading style sheets"],
        "importance": "high"
    },
    "react": {
        "category": "frontend",
        "synonyms": ["reactjs", "react.js", "react js"],
        "importance": "very_high"
    },
    "angular": {
        "category": "frontend",
        "synonyms": ["angularjs", "angular.js"],
        "importance": "high"
    },
    "vue": {
        "category": "frontend",
        "synonyms": ["vuejs", "vue.js"],
        "importance": "high"
    },
    "nextjs": {
        "category": "frontend",
        "synonyms": ["next.js", "next js"],
        "importance": "high"
    },
    "typescript": {
        "category": "frontend",
        "synonyms": ["ts"],
        "importance": "high"
    },
    "tailwind": {
        "category": "frontend",
        "synonyms": ["tailwind css", "tailwindcss"],
        "importance": "medium"
    },
    "bootstrap": {
        "category": "frontend",
        "synonyms": [],
        "importance": "medium"
    },
    "jquery": {
        "category": "frontend",
        "synonyms": [],
        "importance": "low"
    },

    # ========================================
    # DEVOPS & TOOLS
    # ========================================
    "git": {
        "category": "tools",
        "synonyms": ["version control"],
        "importance": "high"
    },
    "github": {
        "category": "tools",
        "synonyms": [],
        "importance": "medium"
    },
    "gitlab": {
        "category": "tools",
        "synonyms": [],
        "importance": "medium"
    },
    "docker": {
        "category": "tools",
        "synonyms": ["containerization"],
        "importance": "very_high"
    },
    "kubernetes": {
        "category": "tools",
        "synonyms": ["k8s"],
        "importance": "very_high"
    },
    "jenkins": {
        "category": "tools",
        "synonyms": [],
        "importance": "high"
    },
    "terraform": {
        "category": "tools",
        "synonyms": [],
        "importance": "high"
    },
    "ansible": {
        "category": "tools",
        "synonyms": [],
        "importance": "medium"
    },
    "ci/cd": {
        "category": "tools",
        "synonyms": ["cicd", "continuous integration"],
        "importance": "high"
    },
    "linux": {
        "category": "tools",
        "synonyms": ["unix"],
        "importance": "high"
    },
    "bash": {
        "category": "tools",
        "synonyms": ["shell scripting", "bash scripting"],
        "importance": "medium"
    },
    "power bi": {
        "category": "tools",
        "synonyms": ["powerbi", "power-bi"],
        "importance": "medium"
    },
    "tableau": {
        "category": "tools",
        "synonyms": [],
        "importance": "medium"
    },

    # ========================================
    # CLOUD PLATFORMS
    # ========================================
    "aws": {
        "category": "cloud",
        "synonyms": ["amazon web services"],
        "importance": "very_high"
    },
    "azure": {
        "category": "cloud",
        "synonyms": ["microsoft azure"],
        "importance": "very_high"
    },
    "gcp": {
        "category": "cloud",
        "synonyms": ["google cloud platform", "google cloud"],
        "importance": "very_high"
    },
    "heroku": {
        "category": "cloud",
        "synonyms": [],
        "importance": "medium"
    },
    "vercel": {
        "category": "cloud",
        "synonyms": [],
        "importance": "medium"
    },

    # ========================================
    # MOBILE DEVELOPMENT
    # ========================================
    "android": {
        "category": "mobile",
        "synonyms": ["android development"],
        "importance": "high"
    },
    "ios": {
        "category": "mobile",
        "synonyms": ["ios development"],
        "importance": "high"
    },
    "react native": {
        "category": "mobile",
        "synonyms": ["react-native", "reactnative"],
        "importance": "high"
    },
    "flutter": {
        "category": "mobile",
        "synonyms": [],
        "importance": "high"
    },
    "xamarin": {
        "category": "mobile",
        "synonyms": [],
        "importance": "medium"
    },

    # ========================================
    # DATA SCIENCE & LIBRARIES
    # ========================================
    "pandas": {
        "category": "ai_ml",
        "synonyms": [],
        "importance": "high"
    },
    "numpy": {
        "category": "ai_ml",
        "synonyms": [],
        "importance": "high"
    },
    "matplotlib": {
        "category": "ai_ml",
        "synonyms": [],
        "importance": "medium"
    },
    "seaborn": {
        "category": "ai_ml",
        "synonyms": [],
        "importance": "medium"
    },
    "plotly": {
        "category": "ai_ml",
        "synonyms": [],
        "importance": "medium"
    },

    # ========================================
    # OTHER IMPORTANT SKILLS
    # ========================================
    "rest api": {
        "category": "backend",
        "synonyms": ["restful api", "rest", "api"],
        "importance": "very_high"
    },
    "graphql": {
        "category": "backend",
        "synonyms": [],
        "importance": "high"
    },
    "microservices": {
        "category": "backend",
        "synonyms": ["micro-services"],
        "importance": "very_high"
    },
    "blockchain": {
        "category": "tools",
        "synonyms": ["block chain"],
        "importance": "medium"
    },
    "web3": {
        "category": "tools",
        "synonyms": [],
        "importance": "medium"
    },
}


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_all_skills():
    """Get list of all skill names"""
    return list(SKILL_DATABASE.keys())


def get_skills_by_category(category):
    """Get skills in a specific category"""
    return [
        skill for skill, data in SKILL_DATABASE.items()
        if data["category"] == category
    ]


def get_skill_synonyms(skill_name):
    """Get synonyms for a skill"""
    if skill_name in SKILL_DATABASE:
        return SKILL_DATABASE[skill_name]["synonyms"]
    return []


# Print statistics
if __name__ == "__main__":
    print(f"Total Skills: {len(SKILL_DATABASE)}")
    print("\nSkills by Category:")

    categories = {}
    for skill, data in SKILL_DATABASE.items():
        cat = data["category"]
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")