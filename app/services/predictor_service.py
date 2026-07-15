from typing import Dict, List, Tuple
 
from app.db.database import supabase
 
 
VALID_COLUMNS = {
    "oc_boys",
    "oc_girls",
    "oc_ews_boys",
    "oc_ews_girls",
    "bca_boys",
    "bca_girls",
    "bcb_boys",
    "bcb_girls",
    "bcc_boys",
    "bcc_girls",
    "bcd_boys",
    "bcd_girls",
    "bce_boys",
    "bce_girls",
    "sc_boys",
    "sc_girls",
    "st_boys",
    "st_girls",
}
 
 
BRANCH_NAMES = {
    "CSE": "Computer Science & Engineering",
    "CSM": "CSE (AI & ML)",
    "CSD": "CSE (Data Science)",
    "CSI": "CSE (Cyber Security)",
    "CAI": "Artificial Intelligence",
    "AIML": "Artificial Intelligence & Machine Learning",
    "AID": "Artificial Intelligence & Data Science",
    "AI": "Artificial Intelligence",
    "IT": "Information Technology",
    "INF": "Information Technology",
    "ECE": "Electronics & Communication Engineering",
    "ECM": "Electronics & Computer Engineering",
    "EEE": "Electrical & Electronics Engineering",
    "MEC": "Mechanical Engineering",
    "CIV": "Civil Engineering",
    "CHE": "Chemical Engineering",
    "BIO": "Biotechnology",
}
 
 
# Explicit, hand-tuned branch affinity scores. Where a (user_branch,
# college_branch) pair isn't listed here, _branch_score() falls back to
# a position-in-family estimate using SEARCH_BRANCHES so every branch
# (including MEC/CIV/CHE/BIO) still gets a sensible score instead of 0.
BRANCH_SCORES = {
 
    "CSE": {
        "CSE":100,
        "CSM":95,
        "CSD":92,
        "CSI":90,
        "AIML":88,
        "AI":85,
        "AID":84,
        "CAI":82,
        "IT":75,
        "INF":70,
        "ECE":20,
        "ECM":18,
    },
 
    "CSM": {
        "CSM":100,
        "CSE":95,
        "CSD":92,
        "CSI":90,
        "AIML":88,
        "AI":85,
        "AID":84,
        "CAI":82,
        "IT":75,
        "INF":70,
    },
 
    "CSD": {
        "CSD":100,
        "CSE":95,
        "CSM":92,
        "CSI":90,
        "AIML":88,
        "AI":85,
        "AID":84,
        "CAI":82,
        "IT":75,
        "INF":70,
    },
 
    "CSI": {
        "CSI":100,
        "CSE":95,
        "CSM":92,
        "CSD":90,
        "AIML":88,
        "AI":85,
        "AID":84,
        "CAI":82,
        "IT":75,
        "INF":70,
    },
 
    "AIML": {
        "AIML":100,
        "AI":97,
        "AID":95,
        "CAI":92,
        "CSM":90,
        "CSE":88,
        "CSD":86,
        "CSI":84,
        "IT":75,
        "INF":70,
    },
 
    "AI": {
        "AI":100,
        "AIML":97,
        "AID":95,
        "CAI":92,
        "CSM":90,
        "CSE":88,
        "CSD":86,
        "CSI":84,
        "IT":75,
        "INF":70,
    },
 
    "AID": {
        "AID":100,
        "AIML":97,
        "AI":95,
        "CAI":92,
        "CSM":90,
        "CSE":88,
        "CSD":86,
        "CSI":84,
        "IT":75,
        "INF":70,
    },
 
    "CAI": {
        "CAI":100,
        "AIML":97,
        "AI":95,
        "AID":92,
        "CSM":90,
        "CSE":88,
        "CSD":86,
        "CSI":84,
        "IT":75,
        "INF":70,
    },
 
    "IT": {
        "IT":100,
        "INF":95,
        "CSE":90,
        "CSM":88,
        "CSD":85,
        "CSI":82,
        "AIML":80,
        "AI":78,
    },
 
    "INF": {
        "INF":100,
        "IT":95,
        "CSE":90,
        "CSM":88,
        "CSD":85,
        "CSI":82,
        "AIML":80,
        "AI":78,
    },
 
    "ECE":{
        "ECE":100,
        "ECM":95,
        "EEE":80,
    },
 
    "ECM":{
        "ECM":100,
        "ECE":95,
        "EEE":80,
    },
 
    "EEE":{
        "EEE":100,
        "ECE":80,
        "ECM":75,
    },
}
 
 
SEARCH_BRANCHES = {
 
    # CS Family
    "CSE": [
        "CSE", "CSM", "CSD", "CSI",
        "AIML", "AI", "AID", "CAI",
        "IT", "INF",
    ],
 
    "CSM": [
        "CSM", "CSE", "CSD", "CSI",
        "AIML", "AI", "AID", "CAI",
        "IT", "INF",
    ],
 
    "CSD": [
        "CSD", "CSE", "CSM", "CSI",
        "AIML", "AI", "AID", "CAI",
        "IT", "INF",
    ],
 
    "CSI": [
        "CSI", "CSE", "CSM", "CSD",
        "AIML", "AI", "AID", "CAI",
        "IT", "INF",
    ],
 
    # AI Family
    "AIML": [
        "AIML", "AI", "AID", "CAI",
        "CSM", "CSE", "CSD", "CSI",
        "IT", "INF",
    ],
 
    "AI": [
        "AI", "AIML", "AID", "CAI",
        "CSM", "CSE", "CSD", "CSI",
        "IT", "INF",
    ],
 
    "AID": [
        "AID", "AI", "AIML", "CAI",
        "CSM", "CSE", "CSD", "CSI",
        "IT", "INF",
    ],
 
    "CAI": [
        "CAI", "AI", "AIML", "AID",
        "CSM", "CSE", "CSD", "CSI",
        "IT", "INF",
    ],
 
    # IT
    "IT": [
        "IT", "INF",
        "CSE", "CSM", "CSD", "CSI",
        "AIML", "AI", "AID", "CAI",
    ],
 
    "INF": [
        "INF", "IT",
        "CSE", "CSM", "CSD", "CSI",
        "AIML", "AI", "AID", "CAI",
    ],
 
    # Electronics
    "ECE": [
        "ECE", "ECM", "EEE",
    ],
 
    "ECM": [
        "ECM", "ECE", "EEE",
    ],
 
    "EEE": [
        "EEE", "ECE", "ECM",
    ],
 
    "MEC": ["MEC"],
    "CIV": ["CIV"],
    "CHE": ["CHE"],
    "BIO": ["BIO"],
}
 
 
# ---------------------------------------------------------------------
# Reputation hook (#5 in the accuracy roadmap).
#
# This is intentionally a no-op-by-default lookup (everything gets a
# neutral 50/100) because we don't yet have real signal (placement %,
# NAAC/NBA accreditation, autonomous status, package data) wired in.
# Populate this dict (instcode -> 0-100) or, better, add a
# `reputation` column to the `cutoffs`/`colleges` table and read it
# in _fetch_candidates() once that data exists.
# ---------------------------------------------------------------------
REPUTATION_SCORES: Dict[str, int] = {
    # "AND1": 90,   # example: strong autonomous college
    # "SRKR": 85,
}
 
DEFAULT_REPUTATION = 50
 
 
def _reputation(instcode: str) -> int:
    return REPUTATION_SCORES.get(instcode, DEFAULT_REPUTATION)
 
 
# ---------------------------------------------------------------------
# Dynamic rank window (#1 + #3 combined).
#
# Instead of scoring on raw |cutoff - rank| (which unfairly punishes
# high-rank students, since a 500-rank gap means very different things
# at rank 2,000 vs rank 80,000), we compute a "good match window" that
# scales with the user's rank, then score based on how many window
# -widths away a college's cutoff is. This is a relative-distance
# measure, so it naturally normalizes across rank ranges.
# ---------------------------------------------------------------------
_WINDOW_POINTS: List[Tuple[int, int]] = [
    (500, 100),
    (2000, 300),
    (10000, 1000),
    (25000, 2500),
    (50000, 5000),
    (80000, 8000),
    (120000, 12000),
]
 
 
def _dynamic_window(rank: int) -> float:
 
    if rank <= 0:
        return _WINDOW_POINTS[0][1]
 
    first_rank, first_window = _WINDOW_POINTS[0]
 
    if rank <= first_rank:
        # Scale proportionally for very low ranks, with a small floor
        # so the window never collapses to ~0.
        return max(50.0, first_window * (rank / first_rank))
 
    last_rank, _last_window = _WINDOW_POINTS[-1]
 
    if rank >= last_rank:
        # Beyond the table, converge to a ~10% relative window.
        return rank * 0.10
 
    for (r1, w1), (r2, w2) in zip(_WINDOW_POINTS, _WINDOW_POINTS[1:]):
        if r1 <= rank <= r2:
            frac = (rank - r1) / (r2 - r1)
            return w1 + frac * (w2 - w1)
 
    return rank * 0.10  # unreachable, but keeps type-checkers happy
 
 
def _branch_score(user_branch: str, college_branch: str) -> int:
 
    explicit = BRANCH_SCORES.get(user_branch, {})
 
    if college_branch in explicit:
        return explicit[college_branch]
 
    if college_branch == user_branch:
        return 100
 
    family = SEARCH_BRANCHES.get(user_branch, [])
 
    if college_branch in family:
        idx = family.index(college_branch)
        return max(0, 100 - idx * 8)
 
    return 0
 
 
def _chance_label(signed_window_ratio: float) -> Tuple[str, int]:
    """
    signed_window_ratio = (cutoff - rank) / window(rank)
 
    Negative => college's cutoff is *better* (lower) than the user's
    rank, i.e. a stretch. Positive => college accepts a worse rank
    than the user has, i.e. comfortably within reach.
    """
 
    if signed_window_ratio < -1.5:
        return "Very Competitive", 20
 
    if signed_window_ratio < 0:
        return "Dream", 40
 
    if signed_window_ratio <= 0.5:
        return "Excellent", 100
 
    if signed_window_ratio <= 1.5:
        return "Very Good", 90
 
    if signed_window_ratio <= 3.0:
        return "Good", 75
 
    if signed_window_ratio <= 6.0:
        return "Possible", 60
 
    return "Safe", 65
 
 
def _bucket_from_chance(chance: str) -> str:
 
    if chance in ("Very Competitive", "Dream"):
        return "Dream"
 
    if chance in ("Excellent", "Very Good", "Good"):
        return "Match"
 
    return "Safe"
 
 
def _fetch_candidates(
    *,
    column: str,
    user_branch: str,
):
    """
    Single optimized database query.
    Fetch only candidates within the user's branch family,
    instead of every branch in the table.
    """
 
    branch_codes = SEARCH_BRANCHES.get(
        user_branch,
        [user_branch],
    )
 
    response = (
        supabase
        .table("cutoffs")
        .select(
            f"instcode,name,branch_code,{column}"
        )
        .in_("branch_code", branch_codes)
        .not_.is_(column, "null")
        .execute()
    )
 
    return response.data
 
 
def _calculate_score(
    *,
    user_rank: int,
    cutoff: int,
    user_branch: str,
    college_branch: str,
    reputation: int,
):
 
    distance = abs(cutoff - user_rank)
    window = _dynamic_window(user_rank)
    window_ratio = distance / window if window > 0 else float(distance)
 
    # ----------------------------
    # Rank Proximity Score (0-100)
    # based on how many "window widths" away the college is.
    # ----------------------------
 
    if window_ratio <= 0.5:
        rank_score = 100
    elif window_ratio <= 1.0:
        rank_score = 90
    elif window_ratio <= 1.5:
        rank_score = 75
    elif window_ratio <= 2.5:
        rank_score = 55
    elif window_ratio <= 4.0:
        rank_score = 35
    elif window_ratio <= 6.0:
        rank_score = 15
    else:
        rank_score = 5
 
    # ----------------------------
    # Branch Similarity Score
    # ----------------------------
 
    branch_score = _branch_score(user_branch, college_branch)
 
    # ----------------------------
    # Chance Category (used both for the label shown to the user
    # and as a small scoring signal)
    # ----------------------------
 
    signed_window_ratio = (cutoff - user_rank) / window if window > 0 else float(cutoff - user_rank)
    chance, chance_score = _chance_label(signed_window_ratio)
 
    # ----------------------------
    # Final weighted score
    # 60% rank proximity, 25% branch similarity,
    # 10% college reputation, 5% chance category.
    # ----------------------------
 
    final_score = (
        rank_score * 0.60
        + branch_score * 0.25
        + reputation * 0.10
        + chance_score * 0.05
    )
 
    return final_score, distance, window_ratio, branch_score, chance
 
 
def _normalize_college_name(name: str) -> str:
 
    normalized = name.upper()
 
    for token in (
        "(SELF SUPPORTING)",
        "SELF-SUPPORTING",
        "SELF SUPPORTING",
        "(AUTONOMOUS)",
        "AUTONOMOUS",
        "-",
    ):
        normalized = normalized.replace(token, " ")
 
    return " ".join(normalized.split())
 
 
def _dedupe_near_duplicate_campuses(colleges: Dict[str, dict]) -> Dict[str, dict]:
    """
    Collapses near-identical campus entries (#9): same normalized name
    and closing ranks within ~3% (and 300 ranks) of each other. Keeps
    the higher-scoring one. Genuinely distinct counseling options
    (different quotas, meaningfully different cutoffs) are left alone.
    """
 
    groups: Dict[str, list] = {}
 
    for instcode, data in colleges.items():
        key = _normalize_college_name(data["college"])
        groups.setdefault(key, []).append((instcode, data))
 
    deduped: Dict[str, dict] = {}
 
    for entries in groups.values():
 
        if len(entries) == 1:
            instcode, data = entries[0]
            deduped[instcode] = data
            continue
 
        entries.sort(key=lambda e: -e[1]["score"])
 
        kept: list = []
 
        for instcode, data in entries:
 
            is_duplicate = False
 
            for _, kept_data in kept:
                rank_diff = abs(data["closing_rank"] - kept_data["closing_rank"])
                rel_diff = rank_diff / max(1, kept_data["closing_rank"])
 
                if rel_diff <= 0.03 and rank_diff <= 300:
                    is_duplicate = True
                    break
 
            if not is_duplicate:
                kept.append((instcode, data))
 
        for instcode, data in kept:
            deduped[instcode] = data
 
    return deduped
 
 
def _merge_candidates(
    rows,
    column,
    rank,
    branch,
):
 
    colleges: Dict[str, dict] = {}
 
    for row in rows:
 
        cutoff = row[column]
 
        if cutoff is None:
            continue
 
        cutoff = int(cutoff)
        instcode = row["instcode"]
        reputation = _reputation(instcode)
 
        score, distance, window_ratio, branch_score, chance = _calculate_score(
            user_rank=rank,
            cutoff=cutoff,
            user_branch=branch,
            college_branch=row["branch_code"],
            reputation=reputation,
        )
 
        existing = colleges.get(instcode)
 
        if (
            existing is None
            or score > existing["score"]
        ):
 
            colleges[instcode] = {
 
                "college": row["name"],
 
                "branch": BRANCH_NAMES.get(
                    row["branch_code"],
                    row["branch_code"],
                ),
 
                "closing_rank": cutoff,
 
                "distance": distance,
 
                "window_ratio": window_ratio,
 
                "branch_score": branch_score,
 
                "reputation": reputation,
 
                "chance": chance,
 
                "bucket": _bucket_from_chance(chance),
 
                "score": score,
            }
 
    return colleges
 
 
# Adaptive result sizing (#7): don't pad out to MAX_RESULTS with
# poor matches just to hit a round number.
MIN_SCORE_THRESHOLD = 40
MIN_RESULTS = 5
MAX_RESULTS = 15
 
 
async def predict_colleges(
    rank: int,
    category: str,
    gender: str,
    branch: str,
):
 
    column = f"{category}_{gender}"
 
    if column not in VALID_COLUMNS:
        raise ValueError(
            f"Invalid category/gender combination: {column}"
        )
 
    rows = _fetch_candidates(
        column=column,
        user_branch=branch,
    )
 
    if not rows:
        return []
 
    colleges = _merge_candidates(
        rows=rows,
        column=column,
        rank=rank,
        branch=branch,
    )
 
    colleges = _dedupe_near_duplicate_campuses(colleges)
 
    ranked = sorted(
        colleges.values(),
        key=lambda x: (
            -x["score"],
            x["window_ratio"],
            -x["branch_score"],
            -x["reputation"],
            x["college"],
        ),
    )
 
    # Adaptive count: prefer genuinely relevant matches over hitting
    # a fixed number of results.
    strong_matches = [c for c in ranked if c["score"] >= MIN_SCORE_THRESHOLD]
 
    if len(strong_matches) >= MIN_RESULTS:
        selected = strong_matches[:MAX_RESULTS]
    else:
        selected = ranked[:MIN_RESULTS]
 
    results = []
 
    for college in selected:
 
        results.append(
            {
                "college": college["college"],
                "branch": college["branch"],
                "closing_rank": college["closing_rank"],
                "chance": college["chance"],
                "bucket": college["bucket"],
                "score": round(college["score"], 2),
            }
        )
 
    return results