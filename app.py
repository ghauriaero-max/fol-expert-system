
import streamlit as st

st.set_page_config(
    page_title="FOL Expert System",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 First-Order Logic Expert System")
st.subheader("University Admission Advisor")

st.write(
    "This application demonstrates how facts and "
    "logical rules can be used to derive conclusions."
)

st.info(
    "Prototype: the next development stage will store "
    "facts and rules in a MySQL database."
)

st.header("Student Information")

student_name = st.text_input("Student name", value="Ali")
marks = st.number_input(
    "Admission marks (%)",
    min_value=0.0,
    max_value=100.0,
    value=75.0
)

passed_test = st.checkbox("Passed admission test")

minimum_marks = 60.0

if st.button("Evaluate Admission", type="primary"):

    # Known facts supplied by the user
    facts = [
        ("marks", student_name, marks),
        ("passed_test", student_name, passed_test),
        ("minimum_marks", "AI", minimum_marks)
    ]

    # Rule 1: Academic eligibility
    academic_eligible = marks >= minimum_marks

    # Rule 2: Final eligibility
    admission_eligible = (
        academic_eligible and passed_test
    )

    st.header("Reasoning Results")

    with st.expander("View known facts"):
        for fact in facts:
            st.write(fact)

    if academic_eligible:
        st.success("Derived: Academic requirement satisfied.")
    else:
        st.warning("Academic requirement not satisfied.")

    if admission_eligible:
        st.success(
            f"Conclusion: {student_name} satisfies "
            "the defined admission requirements for AI."
        )
    else:
        st.error(
            f"Conclusion: {student_name} does not "
            "currently satisfy all defined requirements."
        )

    st.caption(
        "This is a demonstration, not an official "
        "university admission decision."
    )

