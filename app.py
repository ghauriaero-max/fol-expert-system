
from pathlib import Path

import streamlit as st

from knowledge_base import FACTS, RULES
from inference_engine import forward_chain


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="FOL Expert System | Class Presentation",
    page_icon="🧠",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent

# Run the inference engine
ALL_FACTS, TRACE = forward_chain(FACTS, RULES)


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🧠 First-Order Logic Based Expert System")
st.subheader("Design and Development | Class Presentation")

st.markdown(
    """
    **Domain:** University Admission Advisory

    **Technologies:** Python, Streamlit, First-Order Logic,
    forward chaining, and planned MySQL integration.
    """
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Initial facts", len(FACTS))
c2.metric("Inference rules", len(RULES))
c3.metric("Total known facts", len(ALL_FACTS))
c4.metric("New conclusions", len(ALL_FACTS) - len(FACTS))

st.divider()


# --------------------------------------------------
# PRESENTATION TABS
# --------------------------------------------------
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


# --------------------------------------------------
# TAB 1: PROJECT OVERVIEW
# --------------------------------------------------
with tabs[0]:
    st.header("Project Objective")

    st.write(
        "Design an expert system that represents domain knowledge "
        "using First-Order Logic, stores facts and rules, applies "
        "logical reasoning, and explains the conclusions."
    )

    st.subheader("Problem being solved")
    st.write(
        "Admission decisions may depend on several conditions, "
        "such as academic eligibility, test results, interview "
        "results, document verification, and fee payment."
    )

    st.subheader("Our solution")
    st.markdown(
        """
        - Represent domain knowledge as predicates and facts.
        - Define rules that describe relationships between facts.
        - Apply forward chaining to derive new facts.
        - Display conclusions and the reasoning trace.
        - Integrate MySQL for persistent knowledge storage.
        """
    )

    st.info(
        "The current application demonstrates reasoning over "
        "sample facts and rules. MySQL integration is a remaining task."
    )


# --------------------------------------------------
# TAB 2: SYSTEM ARCHITECTURE
# --------------------------------------------------
with tabs[1]:
    st.header("System Architecture")

    stages = [
        (
            "1. User Interface",
            "Streamlit collects inputs and presents results.",
        ),
        (
            "2. Knowledge Base",
            "Facts and logical rules are defined in Python files.",
        ),
        (
            "3. Inference Engine",
            "Python matches predicates, binds variables, "
            "and derives new facts.",
        ),
        (
            "4. Reasoning Trace",
            "The application shows the rule and bindings "
            "behind each inferred fact.",
        ),
        (
            "5. MySQL Database",
            "Planned persistent storage for facts and rules.",
        ),
    ]

    for title, description in stages:
        with st.container(border=True):
            st.subheader(title)
            st.write(description)

    st.caption(
        "Current implementation: Streamlit → Python knowledge base "
        "→ inference engine → conclusions. MySQL is not connected yet."
    )


# --------------------------------------------------
# TAB 3: FOL CONCEPTS
# --------------------------------------------------
with tabs[2]:
    st.header("First-Order Logic Concepts")

    st.markdown(
        """
        **Predicate:** A statement about an entity or a relationship.

        **Constant:** A specific entity, such as `ali` or `ai`.

        **Variable:** A symbol such as `?student` that can match
        different entities.

        **Fact:** A statement treated as known in the knowledge base.

        **Inference rule:** A logical condition that permits a
        conclusion to be derived from matching premises.
        """
    )

    st.subheader("Example predicates")

    examples = [
        ("passed_test(ali)", "Ali passed the admission test."),
        (
            "marks_requirement_met(ali, ai)",
            "Ali satisfies the academic marks requirement for AI.",
        ),
        (
            "admission_eligible(ali, ai)",
            "Ali satisfies all requirements represented by the rules.",
        ),
    ]

    for predicate, meaning in examples:
        with st.container(border=True):
            st.code(predicate, language="text")
            st.write(meaning)

    st.subheader("A rule in logical form")

    st.latex(
        r"\forall x,\ "
        r"passed\_test(x)\rightarrow test\_qualified(x)"
    )

    st.write(
        "Meaning: for every student x, if x passed the test, "
        "then x is test-qualified under our sample rules."
    )

    st.warning(
        "The implementation uses a restricted predicate-rule "
        "language for this assignment; it is not a complete "
        "general-purpose FOL theorem prover."
    )


# --------------------------------------------------
# TAB 4: KNOWLEDGE BASE
# --------------------------------------------------
with tabs[3]:
    st.header("Knowledge Base: Facts")

    st.write(
        "The facts below are the initial information supplied "
        "to the inference engine."
    )

    fact_rows = [
        {
            "No.": i,
            "Predicate": fact[0],
            "Arguments": ", ".join(map(str, fact[1:])),
            "Full fact": str(fact),
        }
        for i, fact in enumerate(FACTS, start=1)
    ]

    st.dataframe(
        fact_rows,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Facts by predicate")

    predicate_counts = {}
    for fact in FACTS:
        predicate_counts[fact[0]] = (
            predicate_counts.get(fact[0], 0) + 1
        )

    st.table(
        [
            {"Predicate": name, "Count": count}
            for name, count in sorted(predicate_counts.items())
        ]
    )


# --------------------------------------------------
# TAB 5: INFERENCE RULES
# --------------------------------------------------
with tabs[4]:
    st.header("Inference Rules")

    st.write(
        "Rules contain premises (IF conditions) and a conclusion "
        "(THEN statement). Variables begin with a question mark."
    )

    for i, (premises, conclusion) in enumerate(RULES, start=1):
        with st.expander(f"Rule {i}: {conclusion[0]}"):
            st.markdown("**IF — premises**")

            for premise in premises:
                st.code(str(premise), language="text")

            st.markdown("**THEN — conclusion**")
            st.code(str(conclusion), language="text")

    st.caption(
        "These are the actual rules loaded from knowledge_base.py."
    )


# --------------------------------------------------
# TAB 6: LIVE DEMONSTRATION
# --------------------------------------------------
with tabs[5]:
    st.header("Live Admission Evaluation")

    student = st.selectbox(
        "Choose a sample student",
        ["ali", "sara", "usman"],
    )

    program = "ai"

    st.subheader("Initial facts for this student")

    selected_facts = [
        fact for fact in FACTS if student in fact
    ]

    if selected_facts:
        for fact in selected_facts:
            st.code(str(fact), language="text")
    else:
        st.info("No initial facts found for this student.")

    st.subheader("Derived conclusions")

    derived_facts = [
        fact for fact in ALL_FACTS
        if student in fact and fact not in FACTS
    ]

    if derived_facts:
        for fact in derived_facts:
            st.write("Derived:", fact)
    else:
        st.write("No new facts derived for this student.")

    eligible = (
        "admission_eligible", student, program
    ) in ALL_FACTS

    if eligible:
        st.success(
            f"{student.title()} satisfies the defined "
            "admission rules for AI."
        )
    else:
        st.warning(
            f"{student.title()} does not satisfy all "
            "defined admission rules for AI."
        )

    st.subheader("Reasoning trace")

    student_trace = [
        item for item in TRACE
        if student in item["fact"]
    ]

    if student_trace:
        for number, item in enumerate(student_trace, start=1):
            with st.expander(
                f"Step {number}: {item['fact']}"
            ):
                premises, conclusion = item["rule"]

                st.write("Matched bindings:")
                st.json(item["bindings"])

                st.write("Rule premises:")
                for premise in premises:
                    st.code(str(premise), language="text")

                st.write("Rule conclusion:")
                st.code(str(conclusion), language="text")
    else:
        st.info("No inference steps found for this student.")

    st.caption(
        "This demonstration uses predefined sample facts, "
        "not a live university admission database."
    )


# --------------------------------------------------
# TAB 7: INFERENCE ENGINE
# --------------------------------------------------
with tabs[6]:
    st.header("Forward-Chaining Inference Engine")

    st.markdown(
        """
        **Forward chaining** starts from known facts and repeatedly
        applies rules to derive new facts.

        1. Match a rule's premise against known facts.
        2. Bind variables to matching values.
        3. Check whether all premises can be satisfied.
        4. Substitute bindings into the conclusion.
        5. Add the conclusion if it is new.
        6. Repeat until no more facts can be derived.
        """
    )

    st.subheader("Current inference statistics")

    a, b, c = st.columns(3)
    a.metric("Initial facts", len(FACTS))
    b.metric("Derived facts", len(ALL_FACTS) - len(FACTS))
    c.metric("Inference steps", len(TRACE))

    st.subheader("Inferred facts")

    if TRACE:
        st.dataframe(
            [
                {
                    "Step": i,
                    "New fact": str(item["fact"]),
                    "Rule conclusion": str(item["rule"][1]),
                    "Bindings": str(item["bindings"]),
                }
                for i, item in enumerate(TRACE, start=1)
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No new facts were inferred.")


# --------------------------------------------------
# TAB 8: TESTING
# --------------------------------------------------
with tabs[7]:
    st.header("Testing and Validation")

    test_students = ["ali", "sara", "usman"]
    test_rows = []

    for name in test_students:
        conclusion = ("admission_eligible", name, "ai")
        actual = conclusion in ALL_FACTS
        expected = name == "ali"

        test_rows.append(
            {
                "Student": name.title(),
                "Expected eligible": expected,
                "Actual eligible": actual,
                "Result": "PASS" if expected == actual else "FAIL",
            }
        )

    st.dataframe(
        test_rows,
        use_container_width=True,
        hide_index=True,
    )

    passed = sum(row["Result"] == "PASS" for row in test_rows)
    st.metric("Tests passed", f"{passed}/{len(test_rows)}")

    if passed == len(test_rows):
        st.success("All sample admission tests passed.")
    else:
        st.error("Some tests failed. Review the rules and facts.")

    st.subheader("Important test limitation")

    st.write(
        "These checks validate the current sample rules and facts. "
        "Additional tests should cover missing facts, conflicting "
        "information, repeated inference, and database failures."
    )


# --------------------------------------------------
# TAB 9: MYSQL DATABASE
# --------------------------------------------------
with tabs[8]:
    st.header("MySQL Database Design")

    st.warning(
        "MySQL has not yet been connected. The following SQL "
        "is a proposed schema, not a live database."
    )

    st.markdown(
        """
        The assignment requires MySQL to store facts, predicates,
        relationships and inference rules. Python will retrieve
        the knowledge and apply the inference engine.
        """
    )

    schema_sql = '''
CREATE DATABASE fol_expert_system;
USE fol_expert_system;

CREATE TABLE facts (
    fact_id INT AUTO_INCREMENT PRIMARY KEY,
    predicate VARCHAR(100) NOT NULL,
    arguments_json JSON NOT NULL
);

CREATE TABLE inference_rules (
    rule_id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(150) NOT NULL,
    premises_json JSON NOT NULL,
    conclusion_json JSON NOT NULL,
    explanation TEXT
);
'''

    st.subheader("Proposed SQL schema")
    st.code(schema_sql, language="sql")

    st.subheader("Integration plan")

    st.markdown(
        """
        1. Provision a hosted MySQL database.
        2. Create the tables and insert the sample facts and rules.
        3. Add the database connector to `requirements.txt`.
        4. Configure database credentials using Streamlit Secrets.
        5. Load facts and rules from MySQL in Python.
        6. Run the inference engine on the retrieved knowledge.
        7. Test database connectivity and inference results.
        """
    )

    st.info(
        "Do not put database passwords or connection credentials "
        "in GitHub source files."
    )


# --------------------------------------------------
# TAB 10: SOURCE CODE
# --------------------------------------------------
with tabs[9]:
    st.header("Project Source Code")

    st.write(
        "Select a project file to display its actual contents "
        "from the deployed repository."
    )

    source_files = [
        "app.py",
        "knowledge_base.py",
        "inference_engine.py",
        "test_cases.py",
        "requirements.txt",
    ]

    selected_file = st.selectbox(
        "Select source file",
        source_files,
    )

    file_path = BASE_DIR / selected_file

    if file_path.is_file():
        source_text = file_path.read_text(encoding="utf-8")

        language = {
            ".py": "python",
            ".txt": "text",
        }.get(file_path.suffix, "text")

        st.code(
            source_text,
            language=language,
        )

        st.download_button(
            label=f"Download {selected_file}",
            data=source_text,
            file_name=selected_file,
            mime="text/plain",
        )
    else:
        st.error(
            f"{selected_file} was not found in the deployed repository."
        )


# --------------------------------------------------
# TAB 11: DELIVERABLES
# --------------------------------------------------
with tabs[10]:
    st.header("Assignment Deliverables Checklist")

    deliverables = [
        ("Python application", "app.py"),
        ("Knowledge-base facts and rules", "knowledge_base.py"),
        ("Forward-chaining engine", "inference_engine.py"),
        ("Test script", "test_cases.py"),
        ("Dependency list", "requirements.txt"),
        ("MySQL schema and sample data", "Pending implementation"),
        ("MySQL connection and persistence", "Pending implementation"),
        ("Documentation", "Pending preparation"),
        ("Working demonstration", "Streamlit deployment"),
    ]

    for item, status in deliverables:
        st.markdown(f"- **{item}:** {status}")

    st.subheader("Current project status")

    st.write(
        "The predicate facts, inference rules, reasoning engine, "
        "and Streamlit presentation are implemented in the project. "
        "MySQL persistence and final documentation remain to be completed."
    )

    st.caption(
        "Educational demonstration. Admission rules are illustrative "
        "and must not be treated as official university policy."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.caption(
    "First-Order Logic Expert System | Python + Streamlit | "
    "MySQL integration pending"
)
