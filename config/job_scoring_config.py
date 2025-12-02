import re

from models.job_analysis import JobDescpSection

# region Keywords
# Used to split job descp to sections that will be scored differently based on importance
# I've let gpt generate optional headers, maybe in the future should auto generate into a file more headers based on
# missing them in job descp
SECTION_HEADERS: dict[str, JobDescpSection] = {
    "requirements": JobDescpSection(
        weight=1.0,
        headers=[
            "requirements",
            "qualifications",
            "must have",
            "what we’re looking for",
            "what we're looking for",
        ],
    ),
    "responsibilities": JobDescpSection(
        weight=0.7,
        headers=["responsibilities", "what you’ll do", "what you'll do", "your role"],
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
        ],
    ),
}

# those wordings affect score
KEYWORDS_CONFIG: dict[str, int] = {
    # ------ Backend -------
    "python": 50,
    "flask": 40,
    "redis": 35,
    "microservices": 45,
    "backend": 40,
    "mysql": 25,
    "sql": 30,
    "lambda": 15,
    "api": 10,
    "postgresql": 15,
    "rest": 10,
    "node": -10,
    "go": -50,
    "java": -50,
    "csharp": -50,
    # ----- Frontend -----
    "react": 25,
    "ember": 10,
    "javascript": 15,
    "vue": -50,
    # ----- Other
    "aws": 45,
    "cicd": 35,
    "circleci": 25,
    "cloud": 30,
    "heroku": 15,
    "serverless": 15,
    "typescript": 20,
    "fullstack": 15,
    "gcp": -10,
    "kubernetes": -100,
}
MUST_HAVE: set[str] = {"python"}
HARD_AVOID: set[str] = {"angular", "php", "wordpress", "drupal", "ruby", "web3"}
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
