import re

from models.job_analysis import JobDescpSection

# region Keywords
# Used to split job descp to sections that will be scored differently based on importance
# I've let gpt generate optional headers, maybe in the future should auto generate into a file more headers based on
# missing them in job descp
SECTION_HEADERS: dict[str, JobDescpSection] = {
    "meta": JobDescpSection(
        weight=1.0, headers=["job title", "department", "location"]
    ),
    "requirements": JobDescpSection(
        weight=1.0,
        headers=[
            "job description",
            "requirements",
            "qualifications",
            "must have",
            "what we’re looking for",
            "all about the role",
            "Knowledge, Skills & Abilities",
        ],
    ),
    "responsibilities": JobDescpSection(
        weight=0.7,
        headers=[
            "responsibilities",
            "what you’ll do",
            "your role",
            "What You’ll Bring",
            "all about you",
            "About the Position, Duties/Responsibilities",
            "Basic Function",
            "What you'll be building",
            "You will…",
        ],
    ),
    "about": JobDescpSection(
        weight=0.3,
        headers=[
            "about",
            "about us",
            "who we are",
            "tech stack",
            "our stack",
            "our technology stack",
            "technologies",
        ],
    ),
    "company": JobDescpSection(
        weight=0.3,
        headers=[
            "company",
            "Who we are",
            "about the company",
        ],
    ),
    "benefits": JobDescpSection(
        weight=0.3,
        headers=[
            "benefits",
            "working conditions",
            "What's In It For You",
            "Additional Benefits",
        ],
    ),
}

# those wordings affect score
KEYWORDS_CONFIG: dict[str, int] = {
    # ------ Backend -------
    "typescript": 90,
    "ownership": 90,
    "python": 20,
    "flask": 40,
    "redis": 35,
    "microservices": 45,
    "backend": 40,
    "mysql": 10,
    "sql": 30,
    "lambda": 15,
    "api": 10,
    "postgresql": 85,
    "rest": 10,
    "node": -10,
    "go": -50,
    "java": -50,
    "csharp": -50,
    "backend": 70,
    # ----- Frontend -----
    "react": 90,
    "ember": -10,
    "javascript": 85,
    "vue": -50,
    # ----- Other
    "aws": 25,
    "cicd": 65,
    "circleci": 25,
    "cloud": 30,
    "serverless": 45,
    "fullstack": 45,
    "gcp": -10,
    "kubernetes": 70,
    "wordpress": -100,
    "drupal": -100,
    "ruby": -100,
    "web3": -100,
    "defi": -100,
}
MUST_HAVE: set[str] = set()
HARD_AVOID: set[str] = set()
# endregion

# region Cues
# I've let gpt generate those, maybe need to add more when I have time
STRONG_CUES = re.compile(
    r"\b(required|must[-\s]*have|hands[-\s]*on|proficient|experience with|strong)\b",
    re.I,
)
SOFT_CUES = re.compile(
    r"\b(familiarity|exposure|nice to have|preferred|bonus|a plus)\b", re.I
)
EXAMPLE_CUES = re.compile(r"\b(e\.g\.|such as|including)\b", re.I)
# endregion
