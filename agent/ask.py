"""Answer a single, precisely worded question with one SQL query (used by the SQL accuracy test)."""
from agent.sql import write_and_run

WINDOW = {"start": "2019-01-01", "end": "2026-09-30", "explanation": "Use the dates stated in the question."}


def answer_question(question: str, dataset: str) -> dict:
    metric = {"name": "Question", "question_answered": question,
              "formula": question + " Return exactly one row with a single column named answer: a number, or a "
                                    "text label when the question asks for a name. Rates and shares as fractions.",
              "grain": "One row", "breakdowns": [], "filters": [], "time_logic": "As stated in the question.",
              "cleaning_rules": [], "excluded_example": "", "chart_hint": "card"}
    result = write_and_run(metric, {"time_window": WINDOW, "shared_rules": []}, dataset=dataset)
    value = None
    if result["ok"] and "answer" in result["df"].columns and len(result["df"]) >= 1:
        value = result["df"]["answer"].iloc[0]
    return {"value": value, "sql": result["sql"], "attempts": len(result["attempts"]), "ok": result["ok"]}
