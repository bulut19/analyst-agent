"""Analyst Agent: from a plain-English request to an audited dashboard.

Run locally from the project folder:  streamlit run app/app.py
"""
import json
import os
import sys
import time
from io import StringIO
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# On Streamlit Cloud, keys come from st.secrets; locally they come from .env (read by agent.config).
try:
    for key in ("ANTHROPIC_API_KEY", "GCP_PROJECT_ID", "ACTIVE_DATASET", "MAX_RUNS_PER_DAY"):
        if key in st.secrets:
            os.environ.setdefault(key, str(st.secrets[key]))
    if "gcp_service_account" in st.secrets:
        os.environ.setdefault("GCP_SERVICE_ACCOUNT_JSON", json.dumps(dict(st.secrets["gcp_service_account"])))
except FileNotFoundError:
    pass

from agent import llm  # noqa: E402
from agent.audit import audit_markdown  # noqa: E402
from agent.charts import figure, prepare, table  # noqa: E402
from agent.config import OUTPUTS  # noqa: E402
from agent import filters  # noqa: E402
from agent.charts import humanize  # noqa: E402
from agent.dashboard import bold_numbers, build as build_dashboard, fmt, headline_value, to_html  # noqa: E402
from agent.metrics import plan_markdown  # noqa: E402
from agent.pipeline import (check_in_questions, stage_audit, stage_check_in, stage_discovery,  # noqa: E402
                            stage_metric_plan, stage_sql)
from agent.requirements import RequirementsInterview, brief_markdown  # noqa: E402
from agent.simulator import answer as simulated_answer, personas  # noqa: E402
from agent.state import ProjectState  # noqa: E402

st.set_page_config(page_title="Analyst Agent", page_icon="📊", layout="wide")

MAX_RUNS_PER_DAY = int(os.environ.get("MAX_RUNS_PER_DAY", "20"))
EXAMPLES = ROOT / "app" / "examples"
STEPS = ["Request", "Interview", "Approve brief", "Audit", "Check in and approve metrics", "Dashboard"]
PERSONAS = {p["id"]: p for p in personas()}
SAMPLES = {"Returns": "returns", "Revenue for the board": "finance", "Marketing channels": "marketing",
           "Discontinue products": "merchandising", "Repeat purchases": "repeat_customers"}

ss = st.session_state
ss.setdefault("step", 0)


# --- helpers --------------------------------------------------------------------

def runs_today() -> int:
    path = OUTPUTS / "usage.json"
    try:
        usage = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        usage = {}
    return usage.get(time.strftime("%Y-%m-%d"), 0)


def count_run():
    path = OUTPUTS / "usage.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        usage = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        usage = {}
    today = time.strftime("%Y-%m-%d")
    usage[today] = usage.get(today, 0) + 1
    path.write_text(json.dumps(usage))


def safe(label, fn, *args):
    """Run an agent step with a spinner; show a friendly error instead of a stack trace."""
    try:
        with st.spinner(label):
            return fn(*args)
    except Exception as e:  # noqa: BLE001
        st.error(f"Something went wrong: {str(e)[:300]}. Click the button again to retry, or Start over.")
        st.stop()


def reset():
    for key in list(ss.keys()):
        del ss[key]
    ss.step = 0


def chat(questions, request):
    if request:
        with st.chat_message("user"):
            st.write(request)
    for q in questions:
        with st.chat_message("assistant", avatar="📊"):
            st.write(q["question"])
        if q.get("answer"):
            with st.chat_message("user"):
                st.write(q["answer"])


def show_audit(audit):
    real = [i for i in audit["issues"] if i["verdict"] == "real_issue"]
    st.write(audit["summary"])
    cols = st.columns(3)
    cols[0].metric("Real issues", len(real))
    cols[1].metric("High or medium severity", sum(i["severity"] in ("high", "medium") for i in real))
    cols[2].metric("Flagged but fine", len(audit["issues"]) - len(real))
    with st.expander("Full audit report"):
        st.markdown(audit_markdown(audit))


def show_dashboard(brief, plan, spec, results, audit, key="live"):
    h = spec["headline"]
    left, right = st.columns([1, 2])
    with left:
        st.caption(h["label"])
        st.markdown(f"<div style='font-size:52px;font-weight:600;line-height:1.1'>"
                    f"{fmt(headline_value(spec, results), h['format'])}</div>", unsafe_allow_html=True)
        st.caption(h["context"])
    with right:
        st.markdown("**Findings**")
        # "$" is escaped so Streamlit does not read dollar amounts as math
        st.markdown("\n".join(f"- {bold_numbers(f, html_out=False).replace('$', chr(92) + '$')}" for f in spec["findings"]))

    # One row of filters that scope every chart and table below (the headline and findings cover everything).
    opts = filters.options(results, spec["charts"])
    selection = {"months": None, "dims": {}}
    if opts["months"] or opts["dims"]:
        st.markdown("**Filters**")
        cols = st.columns(1 + len(opts["dims"]))
        if len(opts["months"]) > 1:
            with cols[0]:
                selection["months"] = st.select_slider("Months", options=opts["months"], key=f"{key}-months",
                                                       value=(opts["months"][0], opts["months"][-1]))
        for col, (dim, values) in zip(cols[1:], opts["dims"].items()):
            with col:
                selection["dims"][dim] = st.multiselect(humanize(dim), values, key=f"{key}-{dim}",
                                                        placeholder="All")
        st.caption("Filters apply to the charts and tables. The headline number and findings describe the full selection.")

    filtered = [{**r, "df": filters.apply(r["df"], selection)} for r in results]  # for the HTML download
    for c in spec["charts"]:
        full = results[c["result_index"]]["df"]
        if full is None:
            continue
        df = filters.apply(full, filters.for_chart(full, c, selection))
        with st.container(border=True):
            if df is None or df.empty:
                st.markdown(f"**{c['title']}**")
                st.info("No data for this filter selection.")
                continue
            # colors come from the chart's unfiltered rows, so filtering never repaints a series
            domain = prepare(full, c)[c["color"]].dropna().astype(str).unique() if c.get("color") else None
            st.plotly_chart(figure(df, c, color_domain=domain), width="stretch", config={"displayModeBar": False},
                            key=f"{key}-chart-{spec['charts'].index(c)}")
            with st.expander("Table view"):
                st.dataframe(table(df, c), hide_index=True)
    with st.expander("Decisions behind these numbers"):
        if plan.get("decisions_confirmed"):
            st.markdown("**Confirmed with the stakeholder**\n\n" + "\n".join(f"- {d}" for d in plan["decisions_confirmed"]))
        st.markdown("**Assumed by the agent** (say so if any are wrong)\n\n" + "\n".join(f"- {d}" for d in plan["decisions_assumed"]))
    html = to_html("Analyst Agent dashboard", brief, plan, spec, filtered, audit, headline_results=results)
    st.download_button("Download this view (HTML)", html, file_name="dashboard.html", mime="text/html", key=f"{key}-dl")


def show_sql(records):
    for r in records:
        status = "✅" if r["ok"] else "❌"
        with st.expander(f"{status} {r['metric']} ({len(r['attempts'])} attempt(s))"):
            st.code(r["sql"], language="sql")
            if len(r["attempts"]) > 1:
                st.caption("Earlier attempts failed validation: " +
                           " | ".join(a["error"][:200] for a in r["attempts"] if a["error"]))


# --- sidebar --------------------------------------------------------------------

with st.sidebar:
    st.title("📊 Analyst Agent")
    mode = st.radio("Mode", ["See a finished example", "Run it live"], key="mode",
                    help="Examples replay saved runs instantly. Live runs call the AI and BigQuery (about 5 minutes).")
    if mode == "Run it live":
        st.divider()
        for i, name in enumerate(STEPS):
            mark = "✅" if i < ss.step else ("▶️" if i == ss.step else "◻️")
            st.write(f"{mark} {name}")
        st.divider()
        st.caption(f"AI cost this session: ${llm.costs.usd:.3f}")
        st.caption(f"Live runs today: {runs_today()} of {MAX_RUNS_PER_DAY}")
        if st.button("Start over"):
            reset()
            st.rerun()

st.title("From a plain-English request to an audited dashboard")
st.caption("The agent interviews the stakeholder, audits the data, agrees on metric definitions, "
           "writes and checks the SQL, then builds the dashboard. A person approves the brief and the metrics.")

# --- example mode -----------------------------------------------------------------

if mode == "See a finished example":
    names = {"Returns are killing us": "returns", "Revenue dashboard for the board": "finance",
             "Why did repeat purchases drop this year?": "repeat_customers"}
    choice = st.selectbox("Example request", list(names))
    ex = json.loads((EXAMPLES / f"{names[choice]}.json").read_text())
    results = [{"metric": r["metric"], "df": None if r["csv"] is None else pd.read_csv(StringIO(r["csv"]))}
               for r in ex["results"]]
    for r in results:
        for c in ([] if r["df"] is None else r["df"].columns):
            if pd.api.types.is_string_dtype(r["df"][c]) and r["df"][c].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}").all():
                r["df"][c] = pd.to_datetime(r["df"][c])
    tabs = st.tabs(["1. Interview", "2. Brief", "3. Data audit", "4. Check-in and metrics", "5. SQL", "6. Dashboard"])
    with tabs[0]:
        chat(ex["questions"], ex["request"])
    with tabs[1]:
        st.markdown(brief_markdown(ex["brief"]))
    with tabs[2]:
        show_audit(ex["audit"])
    with tabs[3]:
        if ex.get("check_in"):
            st.markdown("**Before building, the agent checked in on the choices that change the numbers:**")
            chat(ex["check_in"], None)
        st.markdown(plan_markdown(ex["metric_plan"]))
    with tabs[4]:
        show_sql(ex["sql"])
    with tabs[5]:
        show_dashboard(ex["brief"], ex["metric_plan"], ex["dashboard"], results, ex["audit"], key=ex["id"])
    st.stop()

# --- live mode ----------------------------------------------------------------------

if ss.step == 0:  # request
    st.subheader("What do you need to know?")
    cols = st.columns(len(SAMPLES))
    for col, (label, pid) in zip(cols, SAMPLES.items()):
        if col.button(label, use_container_width=True):
            ss.request_text = PERSONAS[pid]["opening_request"]
            ss.persona = pid
    request = st.text_area("Request", value=ss.get("request_text", ""), height=90,
                           placeholder="For example: Which products should we stop selling?")
    auto = False
    if ss.get("persona") and request == PERSONAS[ss.persona]["opening_request"]:
        auto = st.checkbox("Let an AI stakeholder answer the questions (it knows what this manager really wants)", value=True)
    if st.button("Start", type="primary", disabled=not request.strip()):
        if runs_today() >= MAX_RUNS_PER_DAY:
            st.error("The daily limit for live runs is reached. Try a finished example instead.")
            st.stop()
        count_run()
        ss.auto = auto
        ss.interview = RequirementsInterview(request.strip())
        ss.last = safe("Reading the request...", ss.interview.next)
        ss.step = 1
        st.rerun()

elif ss.step == 1:  # interview
    iv = ss.interview
    chat(iv.questions, iv.request)
    if ss.last["type"] == "brief":
        ss.step = 2
        st.rerun()
    if ss.auto:
        if st.button("Let the stakeholder answer", type="primary"):
            reply = safe("The stakeholder is answering...", simulated_answer, PERSONAS[ss.persona], ss.last["text"], iv.questions)
            ss.last = safe("The analyst is thinking...", iv.answer, reply)
            st.rerun()
    elif reply := st.chat_input("Your answer"):
        ss.last = safe("The analyst is thinking...", iv.answer, reply)
        st.rerun()

elif ss.step == 2:  # approve brief
    with st.expander("Interview", expanded=False):
        chat(ss.interview.questions, ss.interview.request)
    st.markdown(brief_markdown(ss.last["brief"]))
    feedback = st.text_input("Want changes? Describe them here, or approve.")
    c1, c2 = st.columns([1, 4])
    if c1.button("Approve brief", type="primary"):
        ss.state = ProjectState(brief=ss.last["brief"], request=ss.interview.request,
                                interview=ss.interview.questions).save()
        ss.step = 3
        st.rerun()
    if c2.button("Revise", disabled=not feedback):
        ss.last = safe("Revising the brief...", ss.interview.revise, feedback)
        if ss.last["type"] == "question":
            ss.step = 1
        st.rerun()

elif ss.step == 3:  # discovery, audit, metric plan
    with st.status("Working on it (about 2 minutes)...", expanded=True) as status:
        st.write("Mapping the brief to tables and columns...")
        stage_discovery(ss.state)
        st.write("Running data quality checks and reviewing the findings...")
        stage_audit(ss.state)
        st.write("Writing exact metric definitions...")
        stage_metric_plan(ss.state)
        status.update(label="Ready for your review", state="complete")
    ss.step = 4
    st.rerun()

elif ss.step == 4:  # approve metrics
    s = ss.state
    st.subheader("Data quality audit")
    show_audit(s["audit"])
    if s["mapping"]["gaps"]:
        with st.expander(f"What the data cannot answer ({len(s['mapping']['gaps'])})"):
            st.markdown("\n".join(f"- **{g['item']}:** {g['reason']}" for g in s["mapping"]["gaps"]))
    pending = check_in_questions(s) if "check_in" not in s else []
    if pending:  # the agent checks in before building, like an analyst would
        st.subheader("Before I build this, a quick check")
        st.caption("These choices change what shows up on the dashboard, so the agent asks instead of assuming.")
        if ss.auto:
            for q in pending:
                st.markdown(f"- {q}")
            if st.button("Let the stakeholder answer", type="primary"):
                history = list(ss.interview.questions)
                answers = []
                for q in pending:
                    a = safe("The stakeholder is answering...", simulated_answer, PERSONAS[ss.persona], q, history)
                    history.append({"question": q, "answer": a})
                    answers.append(a)
                safe("Updating the metric definitions...", stage_check_in, s, answers)
                st.rerun()
        else:
            with st.form("check_in"):
                replies = [st.text_input(q, placeholder="Leave blank to go with the suggestion", key=f"ci{i}")
                           for i, q in enumerate(pending)]
                if st.form_submit_button("Send answers", type="primary"):
                    answers = [r.strip() or "Go with your suggestion." for r in replies]
                    safe("Updating the metric definitions...", stage_check_in, s, answers)
                    st.rerun()
        st.stop()
    if s.get("check_in"):
        with st.expander(f"Check-in ({len(s['check_in'])} question(s))", expanded=True):
            chat(s["check_in"], None)
    st.subheader("Metric definitions")
    st.markdown(plan_markdown(s["metric_plan"]))
    if st.button("Approve metrics and build the dashboard", type="primary"):
        ss.step = 5
        ss.building = True
        st.rerun()

elif ss.step == 5:  # SQL + dashboard
    s = ss.state
    if ss.get("building"):
        with st.status("Writing and checking SQL, then building the dashboard...", expanded=True) as status:
            stage_sql(s, on_result=lambda r: st.write(f"{'✅' if r['ok'] else '❌'} {r['metric']}"))
            st.write("Choosing charts and writing findings...")
            ss.spec = build_dashboard(s["brief"], s["metric_plan"], s.results)
            s.set("dashboard", ss.spec)
            status.update(label="Done", state="complete")
        ss.building = False
    show_dashboard(s["brief"], s["metric_plan"], ss.spec, s.results, s["audit"])
    with st.expander("SQL the agent wrote"):
        show_sql(s["sql"])
    st.download_button("Download the full run (JSON)", json.dumps(dict(s), indent=1, default=str),
                       file_name="analyst_agent_run.json", mime="application/json")
