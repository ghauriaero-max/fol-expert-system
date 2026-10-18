
import json
from pathlib import Path

import streamlit as st

from knowledge_base import FACTS as LOCAL_FACTS, RULES as LOCAL_RULES
from inference_engine import forward_chain
from mysql_db import load_facts, load_rules, get_database_counts


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FOL University Admission Expert System",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 University Admission Expert System")
st.caption(
    "A First-Order Logic (FOL) based expert system using "
    "MySQL, Python and forward-chaining inference."
)


# ============================================================
# KNOWLEDGE BASE: MYSQL WITH LOCAL FALLBACK
# ============================================================

def normalize_fact(fact):
    """Convert database-loaded fact arguments to tuple form."""
    if isinstance(fact, tuple):
        return fact

    if isinstance(fact, list):
        return tuple(fact)

    if isinstance(fact, dict):
        predicate = fact.get("predicate")
        arguments = fact.get("arguments", [])

        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        return (predicate, *arguments)

    raise ValueError(f"Unsupported fact format: {type(fact).__name__}")


def normalize_rule(rule):
    """
    Return a rule as:
        (premises, conclusion)

    Supports the tuple structure used by the inference engine
    and dictionary structures returned by some database loaders.
    """
    if isinstance(rule, dict):
        premises = rule.get("premises", [])
        conclusion = rule.get("conclusion")

        if isinstance(premises, str):
            premises = json.loads(premises)

        if isinstance(conclusion, str):
            conclusion = json.loads(conclusion)

        premises = [tuple(p) for p in premises]
        conclusion = tuple(conclusion)

        return (premises, conclusion)

    if isinstance(rule, (tuple, list)) and len(rule) >= 2:
        premises, conclusion = rule[0], rule[1]

        premises = [tuple(p) for p in premises]
        conclusion = tuple(conclusion)

        return (premises, conclusion)

    raise ValueError(f"Unsupported rule format: {type(rule).__name__}")


def load_knowledge_base():
    """
    Prefer MySQL as the source of truth.
    Use the local Python knowledge base if loading fails.
    """
    try:
        facts = [normalize_fact(f) for f in load_facts()]
        rules = [normalize_rule(r) for r in load_rules()]

        if not facts or not rules:
            raise ValueError(
                "MySQL returned an empty knowledge base."
            )

        return facts, rules, "MySQL database", None

    except Exception as exc:
        return (
            [normalize_fact(f) for f in LOCAL_FACTS],
            [normalize_rule(r) for r in LOCAL_RULES],
            "Local Python fallback",
            str(exc),
        )


FACTS, RULES, KB_SOURCE, KB_ERROR = load_knowledge_base()

st.caption(
    f"Knowledge base source: **{KB_SOURCE}** | "
    f"Facts loaded: **{len(FACTS)}** | "
    f"Rules loaded: **{len(RULES)}**"
)

if KB_ERROR:
    st.warning(
        "The knowledge base could not be loaded from MySQL. "
        "The app is using local Python data instead. "
        f"Details: {KB_ERROR}"
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_fact(fact):
    """Display a fact as a readable predicate expression."""
    if not fact:
        return str(fact)

    predicate = str(fact[0])

    if len(fact) == 1:
        return f"{predicate}()"

    arguments = ", ".join(str(arg) for arg in fact[1:])
    return f"{predicate}({arguments})"


def get_student_facts(facts, student):
    """Return facts whose arguments mention the selected student."""
    return [
        fact for fact in facts
        if student in fact[1:]
    ]


def get_student_conclusions(facts, student):
    """Return derived or known facts about the selected student."""
    return get_student_facts(facts, student)


def safe_display_trace(trace):
    """Render the inference trace without assuming its exact format."""
    if not trace:
        st.info(
            "No inference steps were recorded. "
            "The initial facts may already contain all matching information, "
            "or no rule was triggered."
        )
        return

    for index, step in enumerate(trace, start=1):
        if isinstance(step, dict):
            st.markdown(f"**Step {index}**")
            st.json(step)
        else:
            st.markdown(f"**Step {index}:** `{step}`")


def get_rule_parts(rule):
    """Extract premises and conclusion from a normalized rule."""
    return rule[0], rule[1]


def read_source_file(filename):
    """Read a source file if it exists in the app directory."""
    path = Path(__file__).parent / filename

    if path.exists():
        return path.read_text(encoding="utf-8")

    return None


def run_inference():
    """Execute forward chaining on the currently loaded knowledge base."""
    return forward_chain(FACTS, RULES)


# ============================================================
# RUN THE INFERENCE ENGINE
# ============================================================

try:
    ALL_FACTS, TRACE = run_inference()
    INFERENCE_ERROR = None
except Exception as exc:
    ALL_FACTS = set(FACTS)
    TRACE = []
    INFERENCE_ERROR = str(exc)

if INFERENCE_ERROR:
    st.error(
        "The inference engine could not complete reasoning. "
        f"Error: {INFERENCE_ERROR}"
    )


# ============================================================
# PRESENTATION TABS
# ============================================================

tabs = st.tabs([
    "1. Overview",
    "2. Architecture",
    "3. FOL Concepts",
    "4. Knowledge Base",
    "5. Inference Rules",
    "6. Live Demo",
    "7. Inference Engine",
    "8. Testing",
    "9. MySQL",
    "10. Source Code",
    "11. Deliverables",
])


# ------------------------------------------------------------
# TAB 1: OVERVIEW
# ------------------------------------------------------------

with tabs[0]:
    st.header("Project Overview")

    st.markdown("""
    ### Problem statement

    University admission decisions require checking multiple conditions,
    including academic eligibility, admission-test results, interview
    performance, document verification and fee payment.

    This project models these conditions using First-Order Logic and
    automatically derives conclusions through a forward-chaining
    inference engine.

    ### Project objectives

    - Represent admission knowledge as logical facts and rules.
    - Store facts and inference rules in a MySQL database.
    - Retrieve the knowledge base using Python.
    - Apply forward chaining to derive conclusions.
    - Explain the conclusions through a visible reasoning trace.
    - Test the system using representative student cases.
    """)

    col1, col2, col3 = st.columns(3)

    col1.metric("Facts loaded", len(FACTS))
    col2.metric("Inference rules", len(RULES))
    col3.metric("Derived / known facts", len(ALL_FACTS))

    st.info(
        "Current knowledge-base source: "
        f"{KB_SOURCE}"
    )

    st.markdown("""
    **Technologies:** Python, Streamlit, MySQL and First-Order Logic.

    **Reasoning method:** Rule-based forward chaining.
    """)


# ------------------------------------------------------------
# TAB 2: ARCHITECTURE
# ------------------------------------------------------------

with tabs[1]:
    st.header("System Architecture")

    st.markdown("""
    The system is divided into five logical components:

    1. **User interface:** Streamlit displays the knowledge base,
       rules, student selection and reasoning results.
    2. **Database:** MySQL stores the initial facts and inference rules.
    3. **Knowledge-base loader:** `mysql_db.py` retrieves database records.
    4. **Inference engine:** `inference_engine.py` applies forward chaining.
    5. **Explanation and testing:** The app displays derived facts,
       inference steps and test outcomes.
    """)

    st.code("""
    User
     |
     v
    Streamlit Interface (app.py)
     |
     v
    MySQL Knowledge Base
     |                  |
     v                  v
    Initial Facts    Inference Rules
     \\                  /
      \\                /
       v              v
        Forward-Chaining Engine
        (inference_engine.py)
                  |
                  v
          Derived Conclusions
                  |
                  v
          Results and Trace
    """, language="text")

    st.caption(
        "When MySQL cannot be loaded, the app displays a warning "
        "and uses the local Python knowledge base for troubleshooting."
    )


# ------------------------------------------------------------
# TAB 3: FOL CONCEPTS
# ------------------------------------------------------------

with tabs[2]:
    st.header("First-Order Logic Concepts")

    st.markdown("""
    ### 1. Predicates

    A predicate expresses a property or relationship.

    Example:

    `passed_test(ali)`

    This states that Ali passed the admission test.

    ### 2. Constants

    Constants identify specific entities.

    Examples: `ali`, `sara`, `usman`, `ai`.

    ### 3. Variables

    Variables represent entities that can match different facts.

    Example: `?student`, `?program`.

    ### 4. Facts

    Facts are statements initially supplied to the knowledge base.

    Example:

    `marks_requirement_met(ali, ai)`

    ### 5. Rules

    Rules specify how new conclusions can be inferred from existing facts.

    Example:

    If a student meets the marks requirement, then the student is
    academically eligible for the program.

    ### 6. Forward chaining

    Forward chaining starts with known facts, searches for rules whose
    premises match those facts, and adds conclusions until no new facts
    can be derived.
    """)

    st.latex(
        r"P(x) \land Q(x) \rightarrow R(x)"
    )

    st.caption(
        "Illustrative logical notation: if P(x) and Q(x) are true, "
        "the system may infer R(x)."
    )


# ------------------------------------------------------------
# TAB 4: KNOWLEDGE BASE
# ------------------------------------------------------------

with tabs[3]:
    st.header("Knowledge Base")

    st.write(
        "These are the facts loaded from the selected source. "
        "When the source label says MySQL, these records came from "
        "the database loader."
    )

    if FACTS:
        fact_rows = [
            {
                "No.": index,
                "Predicate": str(fact[0]),
                "Arguments": ", ".join(str(x) for x in fact[1:]),
                "Logical fact": format_fact(fact),
            }
            for index, fact in enumerate(FACTS, start=1)
        ]

        st.dataframe(
            fact_rows,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.warning("No facts are currently loaded.")

    st.subheader("Filter by student")

    student_filter = st.selectbox(
        "Choose a student",
        ["All students", "ali", "sara", "usman"],
        key="knowledge_student_filter",
    )

    if student_filter == "All students":
        filtered_facts = FACTS
    else:
        filtered_facts = get_student_facts(FACTS, student_filter)

    st.write(f"Matching facts: {len(filtered_facts)}")

    for fact in filtered_facts:
        st.code(format_fact(fact), language="text")


# ------------------------------------------------------------
# TAB 5: INFERENCE RULES
# ------------------------------------------------------------

with tabs[4]:
    st.header("Inference Rules")

    st.markdown("""
    Rules are represented as premises followed by a conclusion.
    A rule can fire when all its premises match known facts.
    """)

    for index, rule in enumerate(RULES, start=1):
        premises, conclusion = get_rule_parts(rule)

        with st.expander(f"Rule {index}", expanded=(index == 1)):
            st.markdown("**Premises**")

            for premise in premises:
                st.code(format_fact(premise), language="text")

            st.markdown("**Conclusion**")
            st.code(format_fact(conclusion), language="text")

            premise_text = " AND ".join(
                format_fact(p) for p in premises
            )

            st.markdown("**Rule in implication form**")
            st.code(
                f"{premise_text} -> {format_fact(conclusion)}",
                language="text",
            )


# ------------------------------------------------------------
# TAB 6: LIVE DEMO
# ------------------------------------------------------------

with tabs[5]:
    st.header("Live Admission Decision Demo")

    st.markdown("""
    Select a student to inspect the facts and conclusions associated
    with that student. The inference engine uses the complete loaded
    knowledge base, then the interface filters the results.
    """)

    selected_student = st.selectbox(
        "Select student",
        ["ali", "sara", "usman"],
        key="live_demo_student",
    )

    if st.button("Run Forward Chaining", type="primary"):
        st.rerun()

    student_known = get_student_facts(FACTS, selected_student)
    student_results = get_student_conclusions(
        ALL_FACTS, selected_student
    )

    st.subheader("Initial facts for the selected student")

    if student_known:
        for fact in student_known:
            st.write(f"- `{format_fact(fact)}`")
    else:
        st.info("No initial facts were found for this student.")

    st.subheader("Facts after inference")

    if student_results:
        for fact in sorted(student_results, key=str):
            st.write(f"- `{format_fact(fact)}`")
    else:
        st.info("No matching facts were derived.")

    eligibility = (
        "admission_eligible",
        selected_student,
        "ai",
    )

    review_required = (
        "admission_review_required",
        selected_student,
    )

    if eligibility in ALL_FACTS:
        st.success(
            f"{selected_student.title()} is admission-eligible "
            "for the AI program according to the current rules."
        )
    elif review_required in ALL_FACTS:
        st.warning(
            f"{selected_student.title()} requires admission review "
            "according to the current rules."
        )
    else:
        st.info(
            f"No admission-eligible conclusion was derived for "
            f"{selected_student.title()}. This is not necessarily "
            "a rejection; it may mean the rules lack enough evidence."
        )

    st.subheader("Inference trace")

    safe_display_trace(TRACE)

    st.caption(
        "The conclusion depends on the current facts and rules. "
        "The system does not infer a formal rejection unless an "
        "explicit rule represents that outcome."
    )


# ------------------------------------------------------------
# TAB 7: INFERENCE ENGINE
# ------------------------------------------------------------

with tabs[6]:
    st.header("Forward-Chaining Inference Engine")

    st.markdown("""
    The inference engine uses the facts and rules supplied by the
    knowledge-base loader.

    Its main cycle is:

    1. Start with the initial facts.
    2. Find rules whose premises match known facts.
    3. Apply variable bindings to the rule conclusion.
    4. Add any new conclusions.
    5. Repeat until no additional facts can be added.
    """)

    st.code("""
    known_facts = initial_facts

    repeat:
        changed = False

        for rule in rules:
            if all premises match known_facts:
                conclusion = apply_bindings(rule)

                if conclusion is new:
                    known_facts.add(conclusion)
                    changed = True

    until changed is False
    """, language="python")

    st.subheader("Current inference statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Initial facts", len(FACTS))
    col2.metric("Total facts after inference", len(ALL_FACTS))
    col3.metric(
        "Additional facts",
        max(0, len(ALL_FACTS) - len(set(FACTS))),
    )

    st.caption(
        "These counts describe the returned facts. The trace format "
        "depends on the implementation in inference_engine.py."
    )

    st.subheader("Complete fact set after inference")

    for fact in sorted(ALL_FACTS, key=str):
        st.write(f"- `{format_fact(fact)}`")


# ------------------------------------------------------------
# TAB 8: TESTING
# ------------------------------------------------------------

with tabs[7]:
    st.header("System Testing")

    st.markdown("""
    The following checks are based on the expected outcomes for
    the current sample knowledge base.
    """)

    expected_cases = [
        {
            "Student": "Ali",
            "Expected predicate": "admission_eligible",
            "Expected outcome": "Eligible",
            "Expected fact": ("admission_eligible", "ali", "ai"),
        },
        {
            "Student": "Sara",
            "Expected predicate": "admission_review_required",
            "Expected outcome": "Review required",
            "Expected fact": ("admission_review_required", "sara"),
        },
        {
            "Student": "Usman",
            "Expected predicate": "admission_eligible",
            "Expected outcome": "Not derived",
            "Expected fact": ("admission_eligible", "usman", "ai"),
        },
    ]

    test_results = []

    for case in expected_cases:
        expected_fact = case["Expected fact"]
        passed = (
            expected_fact in ALL_FACTS
            if case["Student"] != "Usman"
            else expected_fact not in ALL_FACTS
        )

        test_results.append({
            "Student": case["Student"],
            "Expected outcome": case["Expected outcome"],
            "Expected fact": format_fact(expected_fact),
            "Test result": "PASS" if passed else "FAIL",
        })

    st.dataframe(
        test_results,
        use_container_width=True,
        hide_index=True,
    )

    passed_count = sum(
        row["Test result"] == "PASS" for row in test_results
    )

    st.metric(
        "Tests passed",
        f"{passed_count}/{len(test_results)}",
    )

    if passed_count == len(test_results):
        st.success("All listed expected-outcome checks passed.")
    else:
        st.warning(
            "One or more checks failed. Review the facts, rules, "
            "database contents and inference engine."
        )

    st.caption(
        "These are outcome checks, not a substitute for testing "
        "database failures, malformed inputs and rule edge cases."
    )


# ------------------------------------------------------------
# TAB 9: MYSQL DATABASE
# ------------------------------------------------------------

with tabs[8]:
    st.header("MySQL Database Integration")

    st.markdown("""
    The application uses `mysql_db.py` to connect to the hosted
    MySQL service. The database contains the initial facts and
    inference rules, while Python performs the reasoning.
    """)

    st.write(f"**Current knowledge-base source:** {KB_SOURCE}")

    if KB_ERROR:
        st.error(
            "MySQL loading failed in this app session. "
            "The displayed knowledge base is the local fallback."
        )

    if st.button("Refresh MySQL Status"):
        st.rerun()

    try:
        counts = get_database_counts()

        st.subheader("Database record counts")

        if isinstance(counts, dict):
            st.json(counts)
        else:
            st.write(counts)

        st.caption(
            "These counts come from the database count function. "
            "They are distinct from the number of derived facts."
        )

    except Exception as exc:
        st.error(
            "Could not retrieve database counts. "
            f"Details: {exc}"
        )

    st.subheader("Database schema")

    st.code("""
    facts
    ├── fact_key (primary key)
    ├── predicate
    └── arguments (JSON)

    inference_rules
    ├── rule_id (primary key)
    ├── rule_name
    ├── premises (JSON)
    ├── conclusion (JSON)
    └── explanation
    """, language="text")

    st.info(
        "Database credentials should remain in Streamlit Cloud Secrets, "
        "not in app.py or in your public GitHub repository."
    )


# ------------------------------------------------------------
# TAB 10: SOURCE CODE
# ------------------------------------------------------------

with tabs[9]:
    st.header("Project Source Code")

    st.markdown("""
    The project is organized into separate modules to keep the
    interface, knowledge base, database access and reasoning logic
    independent.
    """)

    source_files = [
        "app.py",
        "knowledge_base.py",
        "inference_engine.py",
        "mysql_db.py",
        "db_setup.py",
        "test_cases.py",
        "requirements.txt",
    ]

    selected_file = st.selectbox(
        "Choose a source file",
        source_files,
        key="source_file_selector",
    )

    source_content = read_source_file(selected_file)

    if source_content is None:
        st.warning(
            f"`{selected_file}` was not found beside app.py. "
            "It may have a different name or may not be committed "
            "to the repository."
        )
    else:
        st.code(
            source_content,
            language=(
                "text"
                if selected_file == "requirements.txt"
                else "python"
            ),
        )


# ------------------------------------------------------------
# TAB 11: DELIVERABLES
# ------------------------------------------------------------

with tabs[10]:
    st.header("Assignment Deliverables")

    st.markdown("""
    ### Implemented components

    - [x] University admission domain selected.
    - [x] Facts represented as predicate expressions.
    - [x] Inference rules represented using premises and conclusions.
    - [x] MySQL database tables created.
    - [x] Knowledge base seeded with sample facts and rules.
    - [x] Python forward-chaining inference engine.
    - [x] Streamlit user interface with multiple presentation tabs.
    - [x] Sample student outcome checks.

    ### Final verification checklist

    - [ ] Confirm the main app reports **MySQL database** as its source.
    - [ ] Confirm 16 facts and 10 rules load into the main app.
    - [ ] Confirm the expected student outcomes.
    - [ ] Demonstrate the inference trace.
    - [ ] Verify that database credentials are not committed to GitHub.
    - [ ] Prepare a short explanation of predicates, variables, facts,
          rules, database integration and forward chaining.
    """)

    st.markdown("""
    ### Suggested demonstration sequence

    1. Introduce the admission problem.
    2. Show the system architecture.
    3. Explain the FOL facts and rules.
    4. Show the records loaded from MySQL.
    5. Run the live demo for Ali, Sara and Usman.
    6. Explain how forward chaining derives conclusions.
    7. Show the testing results and source-code organization.
    """)

    st.success(
        "The app is designed to demonstrate the complete workflow "
        "from stored knowledge to rule-based conclusions."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "University Admission Expert System | "
    "First-Order Logic | Python | MySQL | Streamlit"
)
