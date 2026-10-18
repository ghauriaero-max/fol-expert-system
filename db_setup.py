
import streamlit as st

from knowledge_base import FACTS, RULES
from mysql_db import (
    get_connection,
    initialize_schema,
    seed_knowledge_base,
    load_facts,
    load_rules,
    get_database_counts,
)

st.set_page_config(
    page_title="MySQL Setup",
    page_icon="🗄️",
)

st.title("🗄️ FOL Expert System — MySQL Setup")

st.write(
    "Use this page to initialize the database and verify "
    "that the facts and rules are stored correctly."
)

if st.button("1. Test database connection"):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        cursor.close()
        connection.close()

        st.success("Database connection successful.")
        st.write("MySQL server version:", version)

    except Exception as exc:
        st.error("Connection failed.")
        st.code(str(exc))

if st.button("2. Initialize tables and load knowledge"):
    try:
        initialize_schema()
        seed_knowledge_base(FACTS, RULES)

        st.success("Database tables initialized and knowledge loaded.")

    except Exception as exc:
        st.error("Database initialization failed.")
        st.code(str(exc))

if st.button("3. Verify stored knowledge"):
    try:
        fact_count, rule_count = get_database_counts()
        stored_facts = load_facts()
        stored_rules = load_rules()

        st.metric("Facts stored in MySQL", fact_count)
        st.metric("Rules stored in MySQL", rule_count)

        st.write("Sample stored facts:")
        st.json([list(f) for f in stored_facts[:5]])

        st.write("Sample stored rules:")
        st.json([
            {
                "premises": [list(p) for p in premises],
                "conclusion": list(conclusion),
            }
            for premises, conclusion in stored_rules[:3]
        ])

        if fact_count == 16 and rule_count == 10:
            st.success("All 16 facts and 10 rules are present.")
        else:
            st.warning(
                "The stored counts differ from the expected "
                "16 facts and 10 rules. Review the knowledge base."
            )

    except Exception as exc:
        st.error("Verification failed.")
        st.code(str(exc))
