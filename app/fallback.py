"""Local rule-based analyzer used when no OpenAI key is configured (or the AI call fails).
Pure Python, no third-party imports, so it is easy to test."""
import re
from typing import Any, Dict, List, Optional, Tuple

SKILLS: Dict[str, List[str]] = {
    "Python": ["python"], "Java": ["java"], "C++": ["c++", "cpp"], "C#": ["c#"],
    "JavaScript": ["javascript", "js", "ecmascript"], "TypeScript": ["typescript"],
    "Bash/Shell": ["bash", "shell scripting", "shell"],
    "HTML": ["html", "html5"], "CSS": ["css", "css3"], "Tailwind CSS": ["tailwind", "tailwind css"],
    "React": ["react", "react.js", "reactjs"], "Angular": ["angular"], "Vue.js": ["vue", "vue.js"],
    "Node.js": ["node.js", "nodejs", "node"], "Express": ["express", "express.js"],
    "Flask": ["flask"], "FastAPI": ["fastapi"], "Django": ["django"], "Streamlit": ["streamlit"],
    "REST APIs": ["rest api", "rest apis", "restful", "restful api", "restful apis", "rest"],
    "SQL": ["sql", "mysql", "postgresql", "postgres", "sqlite", "sql server"],
    "MongoDB": ["mongodb", "mongo"], "Redis": ["redis"],
    "Pandas": ["pandas"], "NumPy": ["numpy"], "Matplotlib": ["matplotlib", "seaborn"],
    "Data Analysis": ["data analysis", "data analytics", "data analyst"],
    "Data Visualization": ["data visualization", "data visualisation", "dashboards"],
    "Power BI": ["power bi", "powerbi"], "Tableau": ["tableau"], "Excel": ["excel", "ms excel"],
    "Statistics": ["statistics", "statistical analysis", "probability"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "neural network", "neural networks", "cnn", "rnn"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "TensorFlow": ["tensorflow"], "PyTorch": ["pytorch"], "Keras": ["keras"],
    "NLP": ["nlp", "natural language processing"],
    "Computer Vision": ["computer vision", "opencv", "image processing"],
    "Hugging Face": ["hugging face", "huggingface", "transformers"],
    "Generative AI": ["generative ai", "genai", "gen ai"],
    "LLMs": ["llm", "llms", "large language model", "large language models"],
    "Prompt Engineering": ["prompt engineering", "prompt design", "prompting"],
    "RAG": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
    "LangChain": ["langchain"], "LangGraph": ["langgraph"],
    "Vector Databases": ["vector database", "vector databases", "vector db", "vector store",
                         "chromadb", "chroma", "faiss", "pinecone"],
    "OpenAI API": ["openai", "openai api", "gpt", "chatgpt api"],
    "AI Agents": ["ai agent", "ai agents", "agentic ai", "agentic"],
    "Fine-tuning": ["fine-tuning", "fine tuning", "finetuning", "lora"],
    "AWS": ["aws", "amazon web services", "ec2", "s3"], "Azure": ["azure", "microsoft azure"],
    "GCP": ["gcp", "google cloud"], "Docker": ["docker", "containers"],
    "Kubernetes": ["kubernetes", "k8s"], "Git": ["git"], "GitHub": ["github"],
    "CI/CD": ["ci/cd", "cicd", "github actions", "jenkins"], "Linux": ["linux", "ubuntu"],
    "MLOps": ["mlops", "mlflow", "model deployment"],
    "Data Structures & Algorithms": ["data structures", "dsa", "algorithms", "data structures and algorithms"],
    "OOP": ["oop", "object oriented", "object-oriented"], "System Design": ["system design"],
    "Agile": ["agile", "scrum"],
}

ROLES: Dict[str, Dict[str, Any]] = {
    "AI/ML Engineer": {
        "aliases": ["ai/ml engineer", "aiml engineer", "ml engineer", "machine learning engineer",
                    "ai engineer", "artificial intelligence engineer", "ai/ml"],
        "skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "scikit-learn", "Pandas",
                   "NumPy", "SQL", "NLP", "Git", "Docker", "MLOps", "Data Structures & Algorithms"]},
    "Generative AI Developer": {
        "aliases": ["generative ai developer", "genai developer", "gen ai developer", "llm engineer",
                    "llm developer", "prompt engineer", "generative ai engineer"],
        "skills": ["Python", "Generative AI", "LLMs", "Prompt Engineering", "RAG", "LangChain", "LangGraph",
                   "Vector Databases", "OpenAI API", "AI Agents", "FastAPI", "Git", "Docker"]},
    "Data Scientist": {
        "aliases": ["data scientist", "data science"],
        "skills": ["Python", "Statistics", "Machine Learning", "Pandas", "NumPy", "SQL", "scikit-learn",
                   "Data Visualization", "Matplotlib", "Deep Learning", "Git"]},
    "Data Analyst": {
        "aliases": ["data analyst", "business analyst", "analytics"],
        "skills": ["SQL", "Excel", "Python", "Pandas", "Data Analysis", "Data Visualization", "Power BI",
                   "Tableau", "Statistics"]},
    "Full Stack Developer": {
        "aliases": ["full stack developer", "full-stack developer", "fullstack", "web developer"],
        "skills": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Node.js", "REST APIs", "SQL",
                   "MongoDB", "Git", "Docker"]},
    "Backend Developer": {
        "aliases": ["backend developer", "back-end developer", "backend engineer", "software engineer",
                    "software developer"],
        "skills": ["Python", "SQL", "REST APIs", "FastAPI", "Git", "Docker", "Data Structures & Algorithms",
                   "System Design", "Linux", "AWS"]},
    "Frontend Developer": {
        "aliases": ["frontend developer", "front-end developer", "frontend engineer", "ui developer"],
        "skills": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Tailwind CSS", "REST APIs", "Git"]},
    "Cloud/DevOps Engineer": {
        "aliases": ["devops engineer", "cloud engineer", "devops", "sre", "site reliability engineer"],
        "skills": ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Git", "Python", "Bash/Shell"]},
}

_MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?"
DATE_RE = re.compile(
    rf"{_MONTH}(?:\s*(?:-|–|—|to)\s*{_MONTH})?\s*\d{{4}}(?:\s*(?:-|–|—|to)\s*(?:{_MONTH}\s*\d{{4}}|present|current))?"
    r"|\b\d{4}\s*(?:-|–|—)\s*(?:\d{4}|present|current)\b|\b\d+\+?\s*(?:years?|months?|yrs?)\b",
    re.IGNORECASE,
)
ROLE_RE = re.compile(
    r"\b(intern\w*|developer|engineer|analyst|scientist|consultant|associate|trainee|researcher|"
    r"designer|manager|architect|administrator)\b", re.IGNORECASE)
EDU_RE = re.compile(r"\b(b\.?tech|m\.?tech|bachelor\w*|master\w*|bca|mca|b\.?sc|m\.?sc|b\.?e\.?|mba|"
                    r"diploma|degree|university|college|institute|cgpa|gpa)\b", re.IGNORECASE)


def _compile(alias: str) -> "re.Pattern[str]":
    return re.compile(r"(?<![A-Za-z0-9+#.])" + re.escape(alias) + r"(?![A-Za-z0-9+#])", re.IGNORECASE)


_PATTERNS = [(name, [_compile(a) for a in aliases]) for name, aliases in SKILLS.items()]
_C_PATTERN = re.compile(r"(?<![A-Za-z0-9+#.])C(?![A-Za-z0-9+#])")
_ROLE_PATTERNS = sorted(
    [(alias, role, _compile(alias)) for role, d in ROLES.items() for alias in d["aliases"] + [role.lower()]],
    key=lambda t: -len(t[0]))


def extract_skills(text: str) -> List[str]:
    """Return canonical skills in order of first appearance."""
    found: List[Tuple[int, str]] = []
    for name, patterns in _PATTERNS:
        positions = [m.start() for p in patterns for m in [p.search(text)] if m]
        if positions:
            found.append((min(positions), name))
    m = _C_PATTERN.search(text)
    if m:
        found.append((m.start(), "C"))
    found.sort()
    return [n for _, n in found]


def resolve_role(*texts: str) -> Optional[str]:
    for text in texts:
        if not text:
            continue
        for _alias, role, pattern in _ROLE_PATTERNS:
            if pattern.search(text):
                return role
    return None


def _clean(s: str) -> str:
    return s.strip(" ()[]-–—:•*|,.\t")


def extract_experience(text: str) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    segments = [seg for raw in text.splitlines() for seg in re.split(r"(?<=[A-Za-z0-9])\.\s+|;", raw)]
    for raw in segments:
        line = raw.strip(" \t•*-–—")
        if not line or len(line) > 220 or not ROLE_RE.search(line):
            continue
        date = DATE_RE.search(line)
        duration = date.group(0).strip() if date else ""
        no_date = DATE_RE.sub("", line)
        parts = [_clean(p) for p in re.split(r"\s+at\s+|\s*@\s*|\s*\|\s*|\s+[-–—]\s+|,\s*", no_date)]
        parts = [p for p in parts if p]
        role = next((p for p in parts if ROLE_RE.search(p)), "")
        if not role or len(role.split()) > 7:
            continue
        org = next((p for p in parts if p != role and not ROLE_RE.search(p)), "")
        entries.append({"role": role, "organization": org, "duration": duration, "highlights": [line]})
        if len(entries) >= 5:
            break
    return entries


def extract_education(text: str) -> List[str]:
    out = []
    for raw in text.splitlines():
        line = raw.strip(" \t•*-–—")
        if line and len(line) <= 160 and EDU_RE.search(line) and line not in out:
            out.append(line)
        if len(out) >= 3:
            break
    return out


def build_milestones(role: str, gaps: List[str]) -> List[Dict[str, Any]]:
    milestones: List[Dict[str, Any]] = []
    week = 1
    for i in range(0, min(len(gaps), 15), 3):
        chunk = gaps[i:i + 3]
        actions = [f"Learn {s}: read the official docs and finish one guided tutorial" for s in chunk]
        actions.append(f"Build a small hands-on exercise that combines {', '.join(chunk)}")
        milestones.append({"title": f"Phase {len(milestones) + 1}: {', '.join(chunk)}",
                           "timeframe": f"Weeks {week}-{week + 2}", "actions": actions})
        week += 3
    target = role or "your target role"
    milestones.append({
        "title": "Portfolio and interview readiness",
        "timeframe": f"Weeks {week}-{week + 2}",
        "actions": [f"Build and deploy a capstone project that showcases skills for {target}",
                    "Publish it on GitHub with a clear README and screenshots",
                    f"Practise common interview questions for {target}",
                    "Update your resume with the new project and skills"]})
    return milestones


def _summary(skills: List[str], experience: List[Dict[str, Any]], education: List[str]) -> str:
    if not skills:
        return "No recognised technical skills were found in the text."
    parts = [f"Profile with {len(skills)} identified skills, led by {', '.join(skills[:5])}."]
    if experience:
        e = experience[0]
        parts.append(f"Experience includes {e['role']}" + (f" at {e['organization']}." if e["organization"] else "."))
    if education:
        parts.append(f"Education: {education[0]}.")
    return " ".join(parts)


def analyze(mode: str, input_text: str, profile_text: str = "", target_role: str = "") -> Dict[str, Any]:
    missing_info: List[str] = []
    job_match = {"matched_skills": [], "missing_skills": [], "match_percent": None, "match_summary": ""}

    if mode == "job_match":
        candidate_text, jd_text = profile_text, input_text
    else:
        candidate_text, jd_text = input_text, ""

    skills = extract_skills(candidate_text)
    experience = extract_experience(candidate_text)
    education = extract_education(candidate_text)
    role = resolve_role(target_role, jd_text if mode == "job_match" else candidate_text)
    role_display = role or target_role.strip()
    gaps: List[str] = []

    if mode == "job_match":
        jd_skills = extract_skills(jd_text)
        if not jd_skills:
            missing_info.append("No recognised skills were found in the job description; paste the full requirements.")
        have = {s.lower() for s in skills}
        matched = [s for s in jd_skills if s.lower() in have]
        missing = [s for s in jd_skills if s.lower() not in have]
        percent = round(100 * len(matched) / len(jd_skills)) if jd_skills else None
        gaps = missing
        if percent is None:
            summary = "Match could not be computed because no skills were detected in the job description."
        else:
            summary = (f"{len(matched)} of {len(jd_skills)} required skills are present ({percent}% match). "
                       + (f"Missing: {', '.join(missing)}." if missing else "No required skills are missing."))
        job_match = {"matched_skills": matched, "missing_skills": missing,
                     "match_percent": percent, "match_summary": summary}
    elif role:
        gaps = [s for s in ROLES[role]["skills"] if s.lower() not in {x.lower() for x in skills}]
    elif mode == "career_plan":
        missing_info.append("Target role not recognised. Try: " + ", ".join(ROLES) + ".")

    if not skills:
        missing_info.append("No recognised technical skills found; list your tools and technologies explicitly.")
    if mode in ("profile", "job_match") and not experience:
        missing_info.append("No work experience or internship entry detected.")
    if mode == "career_plan" and role and not gaps:
        missing_info.append("You already list every core skill tracked for this role; focus on projects.")

    milestones = build_milestones(role_display, gaps) if (mode != "profile" and (role or gaps)) else []
    return {
        "profile_summary": _summary(skills, experience, education),
        "skills": skills,
        "education": education,
        "experience": experience,
        "target_role": role_display,
        "skill_gaps": gaps,
        "milestones": milestones,
        "job_match": job_match,
        "missing_info": missing_info,
    }
