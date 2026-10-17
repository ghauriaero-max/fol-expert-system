
"""
Knowledge base for the First-Order Logic Expert System.

Facts are represented as predicate tuples.
Rules have premises and a conclusion.
Variables begin with '?'.
"""

# Each fact is a predicate with its arguments.
FACTS = [
    ("marks_requirement_met", "ali", "ai"),
    ("passed_test", "ali"),
    ("interview_passed", "ali"),
    ("documents_complete", "ali"),
    ("fee_paid", "ali"),
    ("marks_requirement_met", "sara", "ai"),
    ("passed_test", "sara"),
    ("interview_failed", "sara"),
    ("documents_complete", "sara"),
    ("marks_requirement_met", "usman", "ai"),
    ("passed_test", "usman"),
    ("documents_incomplete", "usman"),
    ("program_requires_test", "ai"),
    ("program_requires_interview", "ai"),
    ("program_requires_documents", "ai"),
    ("program_requires_fee", "ai"),
]

# Rule format: (premises, conclusion)
# Variables such as ?student can match different entities.
RULES = [
    (
        [("marks_requirement_met", "?student", "?program")],
        ("academically_eligible", "?student", "?program"),
    ),
    (
        [("passed_test", "?student")],
        ("test_qualified", "?student"),
    ),
    (
        [("interview_passed", "?student")],
        ("interview_qualified", "?student"),
    ),
    (
        [("documents_complete", "?student")],
        ("documents_verified", "?student"),
    ),
    (
        [("fee_paid", "?student")],
        ("fee_verified", "?student"),
    ),
    (
        [
            ("academically_eligible", "?student", "?program"),
            ("test_qualified", "?student"),
        ],
        ("initially_qualified", "?student", "?program"),
    ),
    (
        [
            ("initially_qualified", "?student", "?program"),
            ("interview_qualified", "?student"),
        ],
        ("interview_stage_passed", "?student", "?program"),
    ),
    (
        [
            ("interview_stage_passed", "?student", "?program"),
            ("documents_verified", "?student"),
        ],
        ("documents_stage_passed", "?student", "?program"),
    ),
    (
        [
            ("documents_stage_passed", "?student", "?program"),
            ("fee_verified", "?student"),
        ],
        ("admission_eligible", "?student", "?program"),
    ),
    (
        [("interview_failed", "?student")],
        ("admission_review_required", "?student"),
    ),
]
