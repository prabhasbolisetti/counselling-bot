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


# =======================================================================
# BRANCH MODEL
#
# IMPORTANT: the previous version of this file assumed branch_code
# values like "AIML", "CSI", "IT" existed in the `cutoffs` table. They
# don't. The real table uses AP EAPCET's official codes (verified
# against colleges_rows.csv), e.g. "AIM" for AI & ML, "CSC"/"CS" for
# Cyber Security, "INF" for Information Technology (there is no "IT").
#
# Because of that mismatch, picking "AIML" used to search a family
# that silently excluded every actual AI&ML college in the state,
# starved the candidate pool, and forced the ranker to pad results
# with wildly irrelevant colleges just to reach 15.
#
# Fix: model branches as GROUPS of real DB codes that represent the
# same specialization (colleges label the same specialization
# differently), and maintain a separate alias table that maps
# whatever label the bot/UI sends (old or new) onto the correct group.
# =======================================================================

BRANCH_GROUPS: Dict[str, Dict] = {

    "CSE":  {"name": "Computer Science & Engineering",            "codes": ["CSE"]},
    "CSM":  {"name": "CSE (AI & ML)",                              "codes": ["CSM", "AIM"]},
    "CSD":  {"name": "CSE (Data Science)",                         "codes": ["CSD", "DS", "CDA", "CBA"]},
    "CAI":  {"name": "Artificial Intelligence",                    "codes": ["CAI", "AI"]},
    "AID":  {"name": "AI & Data Science",                          "codes": ["AID", "CAD"]},
    "CSC":  {"name": "Cyber Security",                             "codes": ["CSC", "CS", "CSS"]},
    "IOT":  {"name": "IoT & Smart Systems",                        "codes": ["IOT", "CSO", "CIA"]},
    "CIC":  {"name": "IoT, Cyber Security & Blockchain",           "codes": ["CIC", "CBC"]},
    "CSB":  {"name": "Computer Science & Business Systems",        "codes": ["CSB", "CSEB"]},
    "CSG":  {"name": "Computer Science & Design",                  "codes": ["CSG"]},
    "SWE":  {"name": "Software Engineering",                       "codes": ["SWE", "CSW"]},
    "CN":   {"name": "Computer Networking",                        "codes": ["CN"]},
    "CSBS": {"name": "Computer Science & Biosciences",             "codes": ["CSBS"]},
    "CCC":  {"name": "Cloud Computing",                            "codes": ["CCC"]},
    "CST":  {"name": "Computer Science & Technology",              "codes": ["CST"]},
    "INF":  {"name": "Information Technology",                     "codes": ["INF", "CIT"]},

    "ECE":  {"name": "Electronics & Communication Engineering",    "codes": ["ECE", "ECT", "EII"]},
    "ECM":  {"name": "Electronics & Computer Engineering",         "codes": ["ECM"]},
    "EVT":  {"name": "VLSI Design",                                "codes": ["ECV", "EVT"]},
    "EEE":  {"name": "Electrical & Electronics Engineering",       "codes": ["EEE"]},
    "EIE":  {"name": "Electronics & Instrumentation Engineering",  "codes": ["EIE"]},

    "MEC":  {"name": "Mechanical Engineering",                     "codes": ["MEC"]},
    "AUT":  {"name": "Automobile Engineering",                     "codes": ["AUT"]},
    "MIN":  {"name": "Mining Engineering",                         "codes": ["MIN"]},
    "CIV":  {"name": "Civil Engineering",                          "codes": ["CIV"]},
    "CHE":  {"name": "Chemical Engineering",                       "codes": ["CHE"]},
    "BIO":  {"name": "Biotechnology",                              "codes": ["BIO"]},
    "AGR":  {"name": "Agricultural Engineering",                   "codes": ["AGR"]},
    "PHM":  {"name": "Pharmacy (B.Pharm)",                         "codes": ["PHM"]},
    "PHD":  {"name": "Pharm.D",                                    "codes": ["PHD"]},
}


# What label does the bot/user actually send for "branch"? This maps
# every label we know of (old ones like AIML/CSI/IT included, so old
# clients don't break) onto the correct canonical group above.
USER_BRANCH_ALIASES: Dict[str, str] = {

    "CSE": "CSE",

    "CSM": "CSM",
    "AIML": "CSM",   # <- fix: AIML has no DB code of its own; it's the
    "AIM": "CSM",    #    same specialization as CSM (real code AIM)

    "CSD": "CSD",
    "DS": "CSD",

    "AI": "CAI",
    "CAI": "CAI",

    "AID": "AID",
    "CAD": "AID",

    "CSI": "CSC",    # <- fix: "CSI" doesn't exist in the DB; the real
    "CS": "CSC",     #    cyber-security codes are CSC / CS
    "CSC": "CSC",

    "IOT": "IOT",
    "CSO": "IOT",

    "CIC": "CIC",

    "CSB": "CSB",
    "CSG": "CSG",
    "SWE": "SWE",
    "CN": "CN",
    "CSBS": "CSBS",
    "CCC": "CCC",
    "CST": "CST",

    "IT": "INF",     # <- fix: "IT" doesn't exist in the DB; real code is INF
    "INF": "INF",

    "ECE": "ECE",
    "ECM": "ECM",
    "EEE": "EEE",
    "EIE": "EIE",

    "MEC": "MEC",
    "AUT": "AUT",
    "MIN": "MIN",
    "CIV": "CIV",
    "CHE": "CHE",
    "BIO": "BIO",
    "AGR": "AGR",
    "PHM": "PHM",
    "PHD": "PHD",
}


# Group-level relevance ordering: for a user who wants group X, which
# other groups are the closest substitutes, in order of preference?
FAMILY_ORDER: Dict[str, List[str]] = {

    "CSE":  ["CSE", "CSM", "CSD", "CAI", "AID", "INF", "CSC", "CSB", "SWE", "IOT", "CN", "CCC", "CSG"],
    "CSM":  ["CSM", "CAI", "AID", "CSD", "CSE", "CSC", "INF", "IOT"],
    "CSD":  ["CSD", "CSE", "CSM", "CAI", "AID", "CSC", "INF"],
    "CAI":  ["CAI", "AID", "CSM", "CSD", "CSE", "CSC", "INF"],
    "AID":  ["AID", "CAI", "CSM", "CSD", "CSE", "CSC", "INF"],
    "CSC":  ["CSC", "IOT", "CIC", "CSM", "CSE", "INF"],
    "IOT":  ["IOT", "CSC", "CIC", "CSE", "INF"],
    "CIC":  ["CIC", "IOT", "CSC", "CSE"],
    "CSB":  ["CSB", "CSE", "CSM", "INF"],
    "CSG":  ["CSG", "CSE", "CSM"],
    "SWE":  ["SWE", "CSE", "CSM", "INF"],
    "CN":   ["CN", "CSE", "INF"],
    "CSBS": ["CSBS", "BIO", "CSE"],
    "CCC":  ["CCC", "CSE", "INF"],
    "CST":  ["CST", "CSE", "INF"],
    "INF":  ["INF", "CSE", "CSM", "CSD", "CSC"],

    "ECE":  ["ECE", "ECM", "EVT", "EEE", "EIE"],
    "ECM":  ["ECM", "ECE", "EVT", "EEE"],
    "EVT":  ["EVT", "ECE", "ECM"],
    "EEE":  ["EEE", "ECE", "ECM", "EIE"],
    "EIE":  ["EIE", "EEE", "ECE"],

    "MEC":  ["MEC", "AUT", "MIN"],
    "AUT":  ["AUT", "MEC"],
    "MIN":  ["MIN", "MEC", "CIV"],
    "CIV":  ["CIV"],
    "CHE":  ["CHE"],
    "BIO":  ["BIO", "CSBS"],
    "AGR":  ["AGR"],
    "PHM":  ["PHM", "PHD"],
    "PHD":  ["PHD", "PHM"],
}


def _all_group_keys() -> List[str]:
    return list(BRANCH_GROUPS.keys())


# real DB branch_code -> canonical group key (built once at import time)
_REAL_CODE_TO_GROUP: Dict[str, str] = {}
for _group_key, _group in BRANCH_GROUPS.items():
    for _code in _group["codes"]:
        _REAL_CODE_TO_GROUP[_code] = _group_key


def _group_for_real_code(code: str) -> str:
    """
    Canonical group for a raw DB branch_code. Falls back to treating
    an unrecognized code as its own singleton group so nothing ever
    crashes on data we haven't explicitly catalogued (rare/new codes).
    """
    return _REAL_CODE_TO_GROUP.get(code, code)


def _display_name_for_real_code(code: str) -> str:
    group_key = _group_for_real_code(code)
    group = BRANCH_GROUPS.get(group_key)
    if group:
        return group["name"]
    return code


def _normalize_user_branch(branch: str) -> str:
    """
    Turns whatever the bot passes in ("AIML", "CSI", "csm", "AIM", ...)
    into the canonical group key used internally.
    """
    key = (branch or "").strip().upper()

    if key in USER_BRANCH_ALIASES:
        return USER_BRANCH_ALIASES[key]

    if key in BRANCH_GROUPS:
        return key

    # Unrecognized input: treat it as a raw code / its own group so we
    # degrade gracefully instead of raising.
    return _group_for_real_code(key)


def _real_codes_for_group(group_key: str) -> List[str]:
    """
    Flattens a group's whole search family (per FAMILY_ORDER) into the
    actual DB branch_code values to query for, preserving relevance
    order and de-duplicating.
    """
    family = FAMILY_ORDER.get(group_key, [group_key])

    codes: List[str] = []
    seen = set()

    for fam_group in family:
        for code in BRANCH_GROUPS.get(fam_group, {}).get("codes", [fam_group]):
            if code not in seen:
                seen.add(code)
                codes.append(code)

    return codes


def _branch_score(user_group: str, college_real_code: str) -> int:

    college_group = _group_for_real_code(college_real_code)

    if college_group == user_group:
        return 100

    family = FAMILY_ORDER.get(user_group, [user_group])

    if college_group in family:
        idx = family.index(college_group)
        return max(0, 100 - idx * 8)

    # Fetched via a family we didn't explicitly rank (shouldn't
    # normally happen since we only fetch codes within the family) —
    # still give it a low-but-nonzero score rather than 0.
    return 10


# ---------------------------------------------------------------------
# Reputation (#5 in the accuracy roadmap), now backed by the real
# `type` column instead of a hand-maintained stub dict.
#
# PVT = private, PU = private university, UNIV = govt/university
# constituent college, SF/SS = self-financing streams at a
# govt-affiliated institution. This is a coarse heuristic — refine it
# further (placements, accreditation, fee) once that data is
# available — but it's a real signal instead of a constant no-op.
# ---------------------------------------------------------------------
TYPE_REPUTATION: Dict[str, int] = {
    "UNIV": 85,
    "PU": 60,
    "SF": 55,
    "SS": 55,
    "PVT": 50,
}

DEFAULT_REPUTATION = 50

# Optional manual overrides for specific colleges (instcode -> 0-100),
# for cases where you know a college outperforms/underperforms its
# `type` category.
REPUTATION_OVERRIDES: Dict[str, int] = {
    # "SRKR": 80,
}


def _reputation(instcode: str, college_type: str) -> int:
    if instcode in REPUTATION_OVERRIDES:
        return REPUTATION_OVERRIDES[instcode]
    return TYPE_REPUTATION.get((college_type or "").strip().upper(), DEFAULT_REPUTATION)


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
        return max(50.0, first_window * (rank / first_rank))

    last_rank, _last_window = _WINDOW_POINTS[-1]

    if rank >= last_rank:
        return rank * 0.10

    for (r1, w1), (r2, w2) in zip(_WINDOW_POINTS, _WINDOW_POINTS[1:]):
        if r1 <= rank <= r2:
            frac = (rank - r1) / (r2 - r1)
            return w1 + frac * (w2 - w1)

    return rank * 0.10  # unreachable, but keeps type-checkers happy


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
    user_group: str,
):
    """
    Single optimized database query.
    Fetches only branch codes that actually exist in the DB and are
    relevant to the user's chosen specialization group.
    """

    branch_codes = _real_codes_for_group(user_group)

    response = (
        supabase
        .table("cutoffs")
        .select(
            f"instcode,name,branch_code,type,{column}"
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
    user_group: str,
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

    branch_score = _branch_score(user_group, college_branch)

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
    user_group,
):

    colleges: Dict[str, dict] = {}

    for row in rows:

        cutoff = row[column]

        if cutoff is None:
            continue

        cutoff = int(cutoff)
        instcode = row["instcode"]
        reputation = _reputation(instcode, row.get("type"))

        score, distance, window_ratio, branch_score, chance = _calculate_score(
            user_rank=rank,
            cutoff=cutoff,
            user_group=user_group,
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

                "branch": _display_name_for_real_code(row["branch_code"]),

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


MAX_RESULTS = 15

# Safety net (this is what was missing before): never show a college
# whose cutoff is absurdly far from the user's rank (e.g. 15x+ the
# dynamic window) just to pad the list up to MAX_RESULTS. It's better
# to return fewer than 15 genuinely relevant colleges than to include
# ones like a 150,000 closing rank for a rank-9,789 student. In
# practice, once the branch-code fix above widens the candidate pool
# correctly, this cap is rarely the limiting factor.
OUTLIER_WINDOW_RATIO_CAP = 15.0


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

    user_group = _normalize_user_branch(branch)

    rows = _fetch_candidates(
        column=column,
        user_group=user_group,
    )

    if not rows:
        return []

    colleges = _merge_candidates(
        rows=rows,
        column=column,
        rank=rank,
        user_group=user_group,
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

    reasonable = [c for c in ranked if c["window_ratio"] <= OUTLIER_WINDOW_RATIO_CAP]

    if len(reasonable) >= MAX_RESULTS:
        selected = reasonable[:MAX_RESULTS]
    elif reasonable:
        # Fewer than MAX_RESULTS genuinely reasonable matches exist —
        # return what's actually reasonable rather than padding with
        # outliers.
        selected = reasonable
    else:
        # Nothing within a sane window at all (extremely narrow/rare
        # branch): fall back to whatever exists so the user isn't
        # left with an empty response.
        selected = ranked[:MAX_RESULTS]

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