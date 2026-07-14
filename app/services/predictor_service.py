from collections import defaultdict

from app.db.database import supabase


COLUMN_MAP = {
    ("OC", "BOYS"): "oc_boys",
    ("OC", "GIRLS"): "oc_girls",

    ("OC_EWS", "BOYS"): "oc_ews_boys",
    ("OC_EWS", "GIRLS"): "oc_ews_girls",

    ("BCA", "BOYS"): "bca_boys",
    ("BCA", "GIRLS"): "bca_girls",

    ("BCB", "BOYS"): "bcb_boys",
    ("BCB", "GIRLS"): "bcb_girls",

    ("BCC", "BOYS"): "bcc_boys",
    ("BCC", "GIRLS"): "bcc_girls",

    ("BCD", "BOYS"): "bcd_boys",
    ("BCD", "GIRLS"): "bcd_girls",

    ("BCE", "BOYS"): "bce_boys",
    ("BCE", "GIRLS"): "bce_girls",

    ("SC", "BOYS"): "sc_boys",
    ("SC", "GIRLS"): "sc_girls",

    ("ST", "BOYS"): "st_boys",
    ("ST", "GIRLS"): "st_girls",
}


async def predict_colleges(rank: int, category: str, gender: str):
    column = COLUMN_MAP[(category, gender)]

    response = (
        supabase
        .table("cutoffs")
        .select(f"instcode,name,branch_code,{column}")
        .not_.is_(column, "null")
        .gte(column, rank)
        .order(column)
        .execute()
    )

    grouped = defaultdict(
        lambda: {
            "college": "",
            "best_gap": float("inf"),
            "branches": []
        }
    )

    for row in response.data:

        cutoff = row[column]

        gap = cutoff - rank

        college = grouped[row["instcode"]]

        college["college"] = row["name"]

        if gap < college["best_gap"]:
            college["best_gap"] = gap

        college["branches"].append({
            "branch": row["branch_code"],
            "closing_rank": cutoff
        })

    colleges = sorted(
        grouped.values(),
        key=lambda x: x["best_gap"]
    )

    results = []

    for college in colleges[:15]:

        college["branches"].sort(
            key=lambda x: x["closing_rank"]
        )

        results.append({
            "college": college["college"],
            "branches": college["branches"]
        })

    return results