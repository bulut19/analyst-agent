"""Thin wrapper around the Anthropic API: forced tool calls for structured output, plus cost tracking."""
import anthropic

from agent.config import MODEL

# USD per million tokens (input, output). Check claude.com/pricing if these change.
PRICES = {"claude-sonnet-5-5": (2.0, 10.0), "claude-haiku-5-5": (0.10, 0.50), "claude-opus-5-5": (4.0, 20.0)}

_client = anthropic.Anthropic()


class CostTracker:
    def __init__(self):
        self.calls, self.input_tokens, self.output_tokens, self.usd = 0, 0, 0, 0.0

    def add(self, model, usage):
        p_in, p_out = PRICES.get(model, (2.0, 10.0))
        self.calls += 1
        self.input_tokens += usage.input_tokens
        self.output_tokens += usage.output_tokens
        self.usd += usage.input_tokens / 1e6 * p_in + usage.output_tokens / 1e6 * p_out

    def __str__(self):
        return f"{self.calls} calls, {self.input_tokens:,} in / {self.output_tokens:,} out tokens, ${self.usd:.3f}"


costs = CostTracker()


def call(system, messages, tools=None, tool_choice=None, model=MODEL, max_tokens=2000):
    """One Claude call. Returns the full response; usage is added to `costs`."""
    kwargs = dict(model=model, system=system, messages=messages, max_tokens=max_tokens)
    if tools:
        kwargs["tools"] = tools
        if tool_choice:  # newer models only accept "auto"; callers nudge instead of forcing
            kwargs["tool_choice"] = tool_choice
    response = _client.messages.create(**kwargs)
    if response.stop_reason == "max_tokens":
        print(f"Warning: {model} hit max_tokens={max_tokens}; output may be cut off.")
    costs.add(model, response.usage)
    return response


def text(system, user, model=MODEL, max_tokens=2000) -> str:
    """Plain text reply to a single user message."""
    response = call(system, [{"role": "user", "content": user}], model=model, max_tokens=max_tokens)
    return "".join(b.text for b in response.content if b.type == "text").strip()


def tool_use(response):
    """The first tool call in a response, as (name, input, id), or None if the model only wrote text."""
    block = next((b for b in response.content if b.type == "tool_use"), None)
    return (block.name, block.input, block.id) if block else None


def call_tool(system, messages, tools, model=MODEL, max_tokens=2000, attempts=3):
    """Call Claude until it uses one of `tools`. Returns (response, name, input, id).

    Newer models do not support forcing a tool, so if the model replies with text only, we add a short
    reminder and ask again. Those reminder turns are appended to `messages` IN PLACE: the final reply's
    thinking is tied to the exact conversation it saw, so a caller that continues the conversation must
    keep them.
    """
    for _ in range(attempts):
        response = call(system, messages, tools=tools, model=model, max_tokens=max_tokens)
        found = tool_use(response)
        if found:
            return (response, *found)
        messages += [{"role": "assistant", "content": response.content},
                     {"role": "user", "content": "Please respond by calling one of the available tools."}]
    raise RuntimeError("Model did not call a tool after several attempts.")
