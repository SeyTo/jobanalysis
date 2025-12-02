import re

from rank_bm25 import BM25Okapi
from rapidfuzz import fuzz
from rapidfuzz import process as rf_process

from config.job_scoring_config import (EXAMPLE_CUES, HARD_AVOID,
                                       KEYWORDS_CONFIG, MUST_HAVE,
                                       SECTION_HEADERS, SOFT_CUES, STRONG_CUES)
from models.job_analysis import ScoreResult

NORMALIZE_VARIANTS = [
    (re.compile(r"\bci\s*/\s*cd\b", re.I), "cicd"),
    (re.compile(r"\bci\s*-\s*cd\b", re.I), "cicd"),
    (re.compile(r"\bci\s+cd\b", re.I), "cicd"),
    (re.compile(r"\bnode\.?js\b", re.I), "node"),
    (re.compile(r"\bc#\b", re.I), "csharp"),
]


def sentence_strength_multiplier(text: str) -> float:
    """We want to give more/less weight to each sentence additional weight based on
    cues we find in it.
    for example:
    'strong experience with python' will have multiplayer of 1.0 - so it will get the full weight of the word python
    'nice to have experience with python' will have a multiplayer of 0.35 - so the weight of the python keyword
    will be lowered
    """
    mult = 1.0
    if SOFT_CUES.search(text):
        mult *= 0.35
    if STRONG_CUES.search(text):
        pass  # leave at 1.0
    if EXAMPLE_CUES.search(text) or ("(" in text and ")" in text):
        mult *= 0.5
    return mult


def split_requirement_sentences(req_text: str) -> list[str]:
    """Simply split the requirements part of the job desc into sentences
    first it breaks the text by common used list delimiters
    then it splits the lines into sentences

    Example:
        "• 3–5 years experience\\n- React/Next.js. * Node.js, Python? REST/GraphQL"
        will return
        ['3–5 years experience', 'React/Next.js.', 'Node.js, Python?', 'REST/GraphQL']
    """
    lines = re.split(r"(?:\n|\r|•|\*|- )+", req_text)
    sentences = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        parts = re.split(r"(?<=[.!?])\s+", ln)
        sentences.extend(p for p in parts if p)
    return sentences


def adjust_negative_for_or_group(sent: str, base_penalty: float) -> float:
    """This will adjust back up a score weight of an or group
    example: 'java or python'
    """
    if re.search(r"\bor\b", sent, re.I):
        return base_penalty * 0.5
    return base_penalty


def soft_cap_negative(pen: float, is_soft: bool, cap: float = 50.0) -> float:
    """This will cap the negative value of a keyword if the sentence has a soft cue
    example:
    "familiarity with java"
    java has weight of -70 but since the sentence has a soft cue it will only score as -50
    """
    if is_soft:
        return -min(abs(pen), cap)
    return pen


def normalize_text(text: str) -> str:
    t = text.lower()
    for rx, repl in NORMALIZE_VARIANTS:
        t = rx.sub(repl, t)
    t = re.sub(r"[^a-z0-9#+/]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def tokenize(text: str) -> list[str]:
    return normalize_text(text).split()


def split_sections(raw_text: str) -> dict[str, str]:
    """split the job description the sections based on SECTION_HEADERS so we can give weight adjustments
    to keyword based on the section.
    for example:
    about the job:
    aaa
    requirements:
    bbb

    will return {"about": "aaa", "requirements: "bbb"}
    """

    lower = raw_text.lower()
    sections = {key: "" for key in SECTION_HEADERS.keys()}
    header_map = {
        h: sec for sec, job_descp in SECTION_HEADERS.items() for h in job_descp.headers
    }
    pattern = r"(" + "|".join(re.escape(h.lower()) for h in header_map) + r")"
    parts = re.split(pattern, lower)

    current_sec = "about"
    buffer = []

    for part in parts:
        if part in header_map:
            sections[current_sec] += " " + " ".join(buffer)
            buffer = []
            current_sec = header_map[part]
        else:
            buffer.append(part)
    sections[current_sec] += " " + " ".join(buffer)
    return {k: v.strip() for k, v in sections.items()}


def keyword_hits(
    text: str, keywords: dict[str, int], fuzzy_threshold: int = 90
) -> dict[str, int]:
    """Find keyword hits in text, also use fuzzy matching to avoid scoring same positive keyword multiple times"""
    tokens = set(tokenize(text))
    hits: dict[str, int] = {}

    for keyword, weight in keywords.items():
        if keyword in tokens:
            hits[keyword] = weight

    candidates = [
        keyword
        for keyword, weight in keywords.items()
        if weight > 0 and keyword not in hits
    ]
    for tok in tokens:
        match = None
        score = 0
        res = rf_process.extractOne(tok, candidates, scorer=fuzz.token_set_ratio)
        if res:
            match, score, _ = res
        if match and score >= fuzzy_threshold:
            hits.setdefault(match, keywords[match])
    return hits


def score_requirements_section(req_text: str, keywords: dict[str, int]) -> float:
    total = 0.0
    sentences = split_requirement_sentences(req_text)
    for sent in sentences:
        mult = sentence_strength_multiplier(sent)
        is_soft = mult < 1.0
        hits = keyword_hits(sent, keywords)
        for kw, w in hits.items():
            adj = w * mult
            if w < 0:
                adj = adjust_negative_for_or_group(sent, adj)
                adj = soft_cap_negative(adj, is_soft, cap=50.0)
            total += adj
    return total


def bm25f_score(sections: dict[str, str], query_terms: list[str]) -> float:
    """I'm using BM25 per section to also help with the score"""
    total = 0.0

    for sec, text in sections.items():
        if len(text) == 0:
            continue
        toks = tokenize(text)
        bm25 = BM25Okapi([toks])
        sec_score = bm25.get_scores(query_terms)[0]
        total += SECTION_HEADERS.get(sec, 1.0).weight * float(sec_score)

    return total


def score_job_description(
    raw_text: str,
    keywords: dict[str, int] = KEYWORDS_CONFIG,
    must_have: set[str] = MUST_HAVE,
    hard_avoid: set[str] = HARD_AVOID,
) -> ScoreResult:
    sections = split_sections(raw_text)

    # First gate the check if raw text has and avoid keyword
    # todo - it may be better the only hard avoid if the keyword is in the requirements
    tokens = set(tokenize(raw_text))
    for term in hard_avoid:
        if term in tokens:
            return ScoreResult(-1000.0, False, f"hard_avoid:{term}", {}, 0.0)

    # Another gate here if my "must have" requirements are missing from the requirements section
    # currently it's only to check if the job has python in the description but I may evolve on this if
    # I see good scores on jobs I really don't want
    req_tokens = set(tokenize(sections.get("requirements", "")))
    if not must_have.issubset(req_tokens):
        return ScoreResult(-1000.0, False, "missing_must_have", {}, 0.0)

    matched_by_section: dict[str, dict[str, int]] = {}
    # score the "requirements" section
    req_score = score_requirements_section(sections.get("requirements", ""), keywords)
    matched_by_section["requirements"] = keyword_hits(
        sections.get("requirements", ""), keywords
    )

    other = 0.0
    # score the other two sections
    for sec in ("responsibilities", "about"):
        hits = keyword_hits(sections.get(sec, ""), keywords)
        mult = SECTION_HEADERS.get(sec).weight
        other += sum(mult * w for w in hits.values() if w > -1000)
        matched_by_section[sec] = hits

    kw_score = req_score + other
    query_terms = [k for k, w in keywords.items() if w > 0]
    bm25f = bm25f_score(sections, query_terms)
    alpha = 0.4
    # mix kw_score with the bm25 result
    final = alpha * kw_score + (1 - alpha) * bm25f
    return ScoreResult(final, True, None, matched_by_section, bm25f)


if __name__ == "__main__":
    descp = """"""
    score = score_job_description(raw_text=descp)
    print(score.score)
