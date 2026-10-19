"""Stage 1: the requirements interview.

The agent either asks one clarifying question or submits a requirements brief, using two tools.
After MAX_QUESTIONS questions, it is forced to submit the brief.

Usage:
    interview = RequirementsInterview("Returns are killing us. I need to see what's going on.")
    step = interview.next()            # {"type": "question", "text": ...} or {"type": "brief", "brief": {...}}
    while step["type"] == "question":
        step = interview.answer(input(step["text"]))
"""
from agent import llm
from agent.config import MAX_QUESTIONS, prompt

KPI = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "plain_definition": {"type": "string", "description": "What is counted, what is excluded, over what period"},
    },
    "required": ["name", "plain_definition"],
}

BRIEF_SCHEMA = {
    "type": "object",
    "properties": {
        "business_question": {"type": "string", "description": "The question the dashboard answers, in one sentence"},
        "audience": {"type": "string"},
        "decision_supported": {"type": "string", "description": "The decision the reader will make with it"},
        "kpis": {"type": "array", "items": KPI},
        "dimensions": {"type": "array", "items": {"type": "string"}, "description": "Breakdowns, e.g. by category"},
        "filters": {"type": "array", "items": {"type": "string"}},
        "time_range": {"type": "string"},
        "comparison": {"type": "string", "description": "e.g. year over year, vs. prior 12 months, or none"},
        "open_assumptions": {"type": "array", "items": {"type": "string"},
                             "description": "Things assumed rather than confirmed, for the stakeholder to approve"},
        "out_of_scope": {"type": "array", "items": {"type": "string"},
                         "description": "Requested items the data cannot answer, each with the reason"},
    },
    "required": ["business_question", "audience", "decision_supported", "kpis", "dimensions",
                 "filters", "time_range", "comparison", "open_assumptions", "out_of_scope"],
}

TOOLS = [
    {
        "name": "ask_question",
        "description": "Ask the stakeholder one clarifying question.",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The question, as the stakeholder will see it"},
                "why": {"type": "string", "description": "Internal note: what this question resolves"},
            },
            "required": ["question", "why"],
        },
    },
    {
        "name": "submit_brief",
        "description": "Submit the requirements brief once the request is clear enough to build.",
        "input_schema": BRIEF_SCHEMA,
    },
]


class RequirementsInterview:
    def __init__(self, request: str, max_questions: int = MAX_QUESTIONS):
        self.request = request
        self.max_questions = max_questions
        self.messages = [{"role": "user", "content": request}]
        self.questions = []  # [{"question", "why", "answer"}]
        self.brief = None
        self._pending_tool_id = None
        self.system = prompt("system") + "\n\n" + prompt("requirements").format(max_questions=max_questions)

    def next(self, pending_turn=None) -> dict:
        """Ask the model for its next move: a question or the brief.

        Works on a copy of the conversation and commits only when the call succeeds, so an interrupted
        or failed call (for example the app rerunning mid-request) never leaves a half-recorded turn.
        """
        msgs = list(self.messages) + ([pending_turn] if pending_turn else [])
        response, name, data, tool_id = llm.call_tool(self.system, msgs, TOOLS, max_tokens=8000)
        msgs.append({"role": "assistant", "content": response.content})
        if name == "ask_question" and len(self.questions) >= self.max_questions:
            # Question limit reached: tell the model and ask again.
            self.messages = msgs
            return self.next({"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_id,
                "content": "The question limit is reached. Do not ask more. Call submit_brief now, "
                           "recording anything still unclear under open_assumptions."}]})
        self.messages = msgs

        if name == "submit_brief":
            self.brief = data
            self._pending_tool_id = tool_id
            return {"type": "brief", "brief": data}

        self._pending_tool_id = tool_id
        self.questions.append({"question": data["question"], "why": data["why"], "answer": None})
        return {"type": "question", "text": data["question"]}

    def answer(self, text: str) -> dict:
        """Give the stakeholder's answer to the last question, then get the next move."""
        content = text
        if len(self.questions) >= self.max_questions:
            content += "\n\n(Note to analyst: that was your last question. Call submit_brief next.)"
        step = self.next({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": self._pending_tool_id, "content": content}]})
        self.questions[-2 if step["type"] == "question" else -1]["answer"] = text
        return step

    def revise(self, feedback: str) -> dict:
        """The stakeholder asked for changes to the brief: send them back and get a revised brief."""
        return self.next({"role": "user", "content": [{"type": "tool_result", "tool_use_id": self._pending_tool_id,
            "content": f"The stakeholder asked for these changes to the brief: {feedback}\n"
                       "Revise the brief and call submit_brief again. Ask one question only if it is essential."}]})

    def transcript(self) -> list:
        return [{"request": self.request}, *self.questions]


def brief_markdown(brief: dict) -> str:
    """The brief as a readable one-page document."""
    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- None"

    kpis = "\n".join(f"| {k['name']} | {k['plain_definition']} |" for k in brief["kpis"])
    return f"""# Requirements Brief

**Business question:** {brief['business_question']}

**Audience:** {brief['audience']}

**Decision it supports:** {brief['decision_supported']}

## KPIs

| KPI | Definition |
|---|---|
{kpis}

## Scope

- **Breakdowns:** {', '.join(brief['dimensions']) or 'None'}
- **Filters:** {', '.join(brief['filters']) or 'None'}
- **Time range:** {brief['time_range']}
- **Comparison:** {brief['comparison']}

## Assumptions to approve

{bullets(brief['open_assumptions'])}

## Out of scope

{bullets(brief['out_of_scope'])}
"""
