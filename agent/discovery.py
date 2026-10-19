"""Stage 2: data discovery. Maps each item in the brief to tables and columns, and flags gaps.

Every column the model names is checked against the real schema. If it names a column that does
not exist, it gets the list of bad names and one chance to fix them.
"""
import re

from agent import llm
from agent.config import prompt
from agent.schema import column_set, schema_text

MAPPING_SCHEMA = {
    "type": "object",
    "properties": {
        "mappings": {"type": "array", "items": {"type": "object", "properties": {
            "item": {"type": "string", "description": "KPI, dimension, filter or time range, as named in the brief"},
            "item_type": {"type": "string", "enum": ["kpi", "dimension", "filter", "time_range"]},
            "columns": {"type": "array", "items": {"type": "string"}, "description": "table.column names"},
            "logic": {"type": "string", "description": "How these columns produce the item"},
        }, "required": ["item", "item_type", "columns", "logic"]}},
        "joins": {"type": "array", "items": {"type": "string"}, "description": "e.g. order_items.product_id = products.id"},
        "gaps": {"type": "array", "items": {"type": "object", "properties": {
            "item": {"type": "string"}, "reason": {"type": "string"},
            "substitute": {"type": "string", "description": "Closest available alternative, or 'none'"},
        }, "required": ["item", "reason", "substitute"]}},
        "data_notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["mappings", "joins", "gaps", "data_notes"],
}

TOOLS = [{"name": "submit_mapping", "description": "Submit the mapping of the brief to the data.",
          "input_schema": MAPPING_SCHEMA}]

COLUMN_REF = re.compile(r"\b(orders|order_items|products|users)\.([a-z_]+)\b")


def invalid_columns(mapping: dict) -> list:
    """table.column names used in mappings or joins that do not exist in the schema."""
    valid = column_set()
    used = [c for m in mapping["mappings"] for c in m["columns"]]
    for j in mapping["joins"]:
        used += [f"{t}.{c}" for t, c in COLUMN_REF.findall(j)]
    return sorted({c for c in used if c not in valid})


def discover(brief: dict) -> dict:
    system = prompt("system") + "\n\n" + prompt("discovery").format(schema=schema_text())
    messages = [{"role": "user", "content": f"Approved brief:\n{brief}"}]
    response, _, mapping, tool_id = llm.call_tool(system, messages, TOOLS, max_tokens=8000)

    bad = invalid_columns(mapping)
    if bad:  # one correction round
        messages += [{"role": "assistant", "content": response.content},
                     {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_id, "is_error": True,
                      "content": f"These columns do not exist: {', '.join(bad)}. "
                                 "Use only names from the schema, or move the item to gaps. Submit again."}]}]
        response, _, mapping, _ = llm.call_tool(system, messages, TOOLS, max_tokens=8000)
        bad = invalid_columns(mapping)

    mapping["invalid_columns"] = bad  # should be empty; kept for the audit trail
    return mapping


def mapping_markdown(mapping: dict) -> str:
    rows = "\n".join(f"| {m['item']} | {m['item_type']} | {', '.join(f'`{c}`' for c in m['columns'])} | {m['logic']} |"
                     for m in mapping["mappings"])
    gaps = "\n".join(f"- **{g['item']}:** {g['reason']} *Substitute:* {g['substitute']}" for g in mapping["gaps"]) or "- None"
    notes = "\n".join(f"- {n}" for n in mapping["data_notes"]) or "- None"
    joins = "\n".join(f"- `{j}`" for j in mapping["joins"]) or "- None"
    check = "All columns exist in the schema." if not mapping.get("invalid_columns") else \
        f"WARNING: unknown columns {mapping['invalid_columns']}"
    return f"""# Data Mapping

| Item | Type | Columns | Logic |
|---|---|---|---|
{rows}

## Joins

{joins}

## Gaps

{gaps}

## Data notes

{notes}

*Column check: {check}*
"""
