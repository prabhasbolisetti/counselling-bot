from app.services.predictor_service import predict_colleges
from app.services.session_service import get_session, reset_session


MIN_RANK = 1
MAX_RANK = 200000


MENU = """
👋 Welcome to AP EAPCET Counselling Bot

1️⃣ College Predictor
2️⃣ Category-wise Cutoff PDF
3️⃣ Counselling Documents

Reply with 1, 2 or 3.
"""

CATEGORY_MENU = """
Select your Category

1. OC
2. OC_EWS
3. BCA
4. BCB
5. BCC
6. BCD
7. BCE
8. SC
9. ST
"""

GENDER_MENU = """
Select Gender

1. Boys
2. Girls
"""

BRANCH_MENU = """
Select Preferred Branch

1. CSE
2. CSM (AI & ML)
3. CSD (Data Science)
4. CSI (Cyber Security)
5. CAI
6. AIML
7. AID
8. AI
9. INF
10. IT
11. ECE
12. ECM
13. EEE
14. MEC
15. CIV
16. CHE
17. BIO
"""


CATEGORY_MAP = {
    "1": "oc",
    "2": "oc_ews",
    "3": "bca",
    "4": "bcb",
    "5": "bcc",
    "6": "bcd",
    "7": "bce",
    "8": "sc",
    "9": "st",
}


GENDER_MAP = {
    "1": "boys",
    "2": "girls",
}


BRANCH_MAP = {
    "1": "CSE",
    "2": "CSM",
    "3": "CSD",
    "4": "CSI",
    "5": "CAI",
    "6": "AIML",
    "7": "AID",
    "8": "AI",
    "9": "INF",
    "10": "IT",
    "11": "ECE",
    "12": "ECM",
    "13": "EEE",
    "14": "MEC",
    "15": "CIV",
    "16": "CHE",
    "17": "BIO",
}


def _validate_rank(text: str):

    text = text.strip()

    if not text:
        return (
            False,
            "❌ Rank cannot be empty.\n\nPlease enter your AP EAPCET Rank."
        )

    if not text.isdigit():

        return (
            False,
            "❌ Invalid rank.\n\n"
            "Please enter numbers only.\n\n"
            "Example: 12345"
        )

    rank = int(text)

    if rank < MIN_RANK:

        return (
            False,
            f"❌ Invalid rank.\n\n"
            f"Rank should be between {MIN_RANK} and {MAX_RANK}."
        )

    if rank > MAX_RANK:

        return (
            False,
            f"❌ Invalid rank.\n\n"
            f"Rank should be between {MIN_RANK} and {MAX_RANK}."
        )

    return True, rank


def _validate_menu_choice(
    text: str,
    mapping: dict,
    menu: str,
    field: str,
):

    text = text.strip()

    if text not in mapping:

        return (
            False,
            f"❌ Invalid {field}.\n\n{menu}"
        )

    return (
        True,
        mapping[text],
    )

async def process_message(
    phone: str,
    message: str,
):

    session = get_session(phone)

    text = message.strip().lower()

    # ------------------------
    # GLOBAL COMMANDS
    # ------------------------

    if text in {
        "hi",
        "hello",
        "menu",
        "start",
    }:

        reset_session(phone)

        return MENU

    state = session["state"]

    # ------------------------
    # MAIN MENU
    # ------------------------

    if state == "MAIN_MENU":

        if text in {"1", "predictor"}:

            session["state"] = "WAITING_RANK"

            return "Please enter your AP EAPCET Rank."

        if text in {"2", "cutoff"}:

            return (
                "📄 *AP EAPCET Category-wise Cutoff PDF*\n\n"
                "Download here:\n"
                "https://drive.google.com/file/d/1pleb5J0VRxLLyWEW4OuNMTwY1AWosaOi/view?usp=sharing\n\n"
                "Reply *MENU* to return to the main menu."
            )

        if text in {"3", "documents"}:

            return (
                "📑 *AP EAPCET Counselling Documents*\n\n"
                "Download here:\n"
                "https://drive.google.com/file/d/16Oy9Je2pSTdFlE5mfsHVPzviOEkc40l-/view?usp=drivesdk\n\n"
                "Reply *MENU* to return to the main menu."
            )

        return (
            "❌ Invalid option.\n\n"
            + MENU
        )

    # ------------------------
    # WAITING RANK
    # ------------------------

    if state == "WAITING_RANK":

        valid, value = _validate_rank(text)

        if not valid:
            return value

        session["rank"] = value

        session["state"] = "WAITING_CATEGORY"

        return CATEGORY_MENU

    # ------------------------
    # WAITING CATEGORY
    # ------------------------

    if state == "WAITING_CATEGORY":

        valid, value = _validate_menu_choice(
            text=text,
            mapping=CATEGORY_MAP,
            menu=CATEGORY_MENU,
            field="category",
        )

        if not valid:
            return value

        session["category"] = value

        session["state"] = "WAITING_GENDER"

        return GENDER_MENU

    # ------------------------
    # WAITING GENDER
    # ------------------------

    if state == "WAITING_GENDER":

        valid, value = _validate_menu_choice(
            text=text,
            mapping=GENDER_MAP,
            menu=GENDER_MENU,
            field="gender",
        )

        if not valid:
            return value

        session["gender"] = value

        session["state"] = "WAITING_BRANCH"

        return BRANCH_MENU

    # ------------------------
    # WAITING BRANCH
    # ------------------------

    if state == "WAITING_BRANCH":

        valid, value = _validate_menu_choice(
            text=text,
            mapping=BRANCH_MAP,
            menu=BRANCH_MENU,
            field="branch",
        )

        if not valid:
            return value

        session["branch"] = value

        try:

            colleges = await predict_colleges(
                rank=session["rank"],
                category=session["category"],
                gender=session["gender"],
                branch=session["branch"],
            )

        except Exception:

            reset_session(phone)

            return (
                "⚠️ Unable to process your request right now.\n\n"
                "Please try again later."
            )

        if not colleges:

            reset_session(phone)

            return (
                "❌ No colleges found for your criteria.\n\n"
                "Reply *MENU* to search again."
            )

        lines = []

        lines.append("🎯 *Top 15 Recommended Colleges*")
        lines.append("")
        lines.append(f"📌 Rank : {session['rank']}")
        lines.append(f"📌 Category : {session['category'].upper()}")
        lines.append(f"📌 Gender : {session['gender'].title()}")
        lines.append(f"📌 Preferred Branch : {session['branch']}")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("")

        for index, college in enumerate(colleges, start=1):

            lines.append(f"{index}. *{college['college']}*")
            lines.append(f"   • {college['branch']}")
            lines.append(
                f"   • Closing Rank: {college['closing_rank']}"
            )
            lines.append("")

        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("Reply *MENU* to search again.")

        reset_session(phone)

        return "\n".join(lines)

    # ------------------------
    # UNKNOWN STATE
    # ------------------------

    reset_session(phone)

    return (
        "⚠️ Your previous session has expired or became invalid.\n\n"
        + MENU
    )