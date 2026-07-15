from app.services.predictor_service import predict_colleges
from app.services.session_service import get_session, reset_session


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


async def process_message(phone: str, message: str):

    session = get_session(phone)
    text = message.strip().lower()

    # ------------------------
    # GLOBAL COMMANDS
    # ------------------------

    if text in {"hi", "hello", "menu", "start"}:
        reset_session(phone)
        return MENU

    state = session["state"]

    # ------------------------
    # MAIN MENU
    # ------------------------

    if state == "MAIN_MENU":

        if text == "1":
            session["state"] = "WAITING_RANK"
            return "Please enter your AP EAPCET Rank."

        if text == "2":
            return "__SEND_CUTOFF_PDF__"

        if text == "3":
            return "__SEND_DOCUMENTS_PDF__"

        return MENU

    # ------------------------
    # WAITING RANK
    # ------------------------

    if state == "WAITING_RANK":

        if not text.isdigit():
            return "❌ Please enter a valid rank."

        session["rank"] = int(text)
        session["state"] = "WAITING_CATEGORY"

        return CATEGORY_MENU

    # ------------------------
    # WAITING CATEGORY
    # ------------------------

    if state == "WAITING_CATEGORY":

        if text not in CATEGORY_MAP:
            return "❌ Invalid category.\n\n" + CATEGORY_MENU

        session["category"] = CATEGORY_MAP[text]
        session["state"] = "WAITING_GENDER"

        return GENDER_MENU

    # ------------------------
    # WAITING GENDER
    # ------------------------

    if state == "WAITING_GENDER":

        if text not in GENDER_MAP:
            return "❌ Invalid gender.\n\n" + GENDER_MENU

        session["gender"] = GENDER_MAP[text]
        session["state"] = "WAITING_BRANCH"

        return BRANCH_MENU

    # ------------------------
    # WAITING BRANCH
    # ------------------------

    if state == "WAITING_BRANCH":

        if text not in BRANCH_MAP:
            return "❌ Invalid branch.\n\n" + BRANCH_MENU

        session["branch"] = BRANCH_MAP[text]

        colleges = await predict_colleges(
            rank=session["rank"],
            category=session["category"],
            gender=session["gender"],
            branch=session["branch"],
        )

        if not colleges:
            reset_session(phone)
            return (
                "❌ No colleges found for your criteria.\n\n"
                "Reply MENU to try again."
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
            lines.append(f"   • Closing Rank: {college['closing_rank']}")
            lines.append("")

        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("Reply *MENU* to search again.")

        reset_session(phone)

        return "\n".join(lines)

    # ------------------------
    # FALLBACK
    # ------------------------

    reset_session(phone)
    return MENU