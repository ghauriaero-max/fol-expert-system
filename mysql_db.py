
"""MySQL persistence layer for the FOL expert system."""

import hashlib
import json
import tempfile
from pathlib import Path

import mysql.connector
import streamlit as st


def get_connection():
    """Connect using credentials stored in Streamlit Secrets."""
    cfg = st.secrets["mysql"]

    options = {
        "host": cfg["host"],
        "port": int(cfg["port"]),
        "user": cfg["user"],
        "password": cfg["password"],
        "database": cfg["database"],
        "ssl_disabled": False,
        "connection_timeout": 15,
    }

    # Optional CA certificate for verified TLS connections.
    if cfg.get("ca_cert"):
        cert_path = Path(tempfile.gettempdir()) / "aiven-ca.pem"
        cert_path.write_text(cfg["ca_cert"], encoding="utf-8")
        options["ssl_ca"] = str(cert_path)
        options["ssl_verify_cert"] = True
        options["ssl_verify_identity"] = True

    return mysql.connector.connect(**options)


def parse_json(value):
    """Handle JSON returned as either a string or a Python object."""
    if isinstance(value, str):
        return json.loads(value)
    return value


def initialize_schema():
    """Create the tables required by the assignment."""
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                fact_key CHAR(64) NOT NULL PRIMARY KEY,
                predicate VARCHAR(100) NOT NULL,
                arguments JSON NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inference_rules (
                rule_id INT NOT NULL PRIMARY KEY,
                rule_name VARCHAR(150) NOT NULL,
                premises JSON NOT NULL,
                conclusion JSON NOT NULL,
                explanation TEXT
            )
        """)

        connection.commit()
        cursor.close()
    finally:
        connection.close()


def seed_knowledge_base(facts, rules):
    """Insert or update facts and rules without creating duplicates."""
    connection = get_connection()

    try:
        cursor = connection.cursor()

        for fact in facts:
            predicate = fact[0]
            arguments = list(fact[1:])

            canonical = json.dumps(
                list(fact),
                sort_keys=True,
                separators=(",", ":"),
            )
            fact_key = hashlib.sha256(
                canonical.encode("utf-8")
            ).hexdigest()

            cursor.execute(
                """
                INSERT INTO facts
                    (fact_key, predicate, arguments)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    predicate = VALUES(predicate),
                    arguments = VALUES(arguments)
                """,
                (
                    fact_key,
                    predicate,
                    json.dumps(arguments),
                ),
            )

        for index, (premises, conclusion) in enumerate(
            rules, start=1
        ):
            cursor.execute(
                """
                INSERT INTO inference_rules
                    (rule_id, rule_name, premises,
                     conclusion, explanation)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    rule_name = VALUES(rule_name),
                    premises = VALUES(premises),
                    conclusion = VALUES(conclusion),
                    explanation = VALUES(explanation)
                """,
                (
                    index,
                    f"Rule {index}",
                    json.dumps([list(p) for p in premises]),
                    json.dumps(list(conclusion)),
                    f"Derive {conclusion[0]} when all premises match.",
                ),
            )

        connection.commit()
        cursor.close()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def load_facts():
    """Retrieve stored facts in the inference engine's tuple format."""
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT predicate, arguments FROM facts ORDER BY fact_key"
        )

        facts = [
            tuple([predicate] + list(parse_json(arguments)))
            for predicate, arguments in cursor.fetchall()
        ]

        cursor.close()
        return facts
    finally:
        connection.close()


def load_rules():
    """Retrieve rules in the inference engine's expected format."""
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT premises, conclusion
            FROM inference_rules
            ORDER BY rule_id
        """)

        rules = []

        for premises, conclusion in cursor.fetchall():
            premises = [
                tuple(p) for p in parse_json(premises)
            ]
            conclusion = tuple(parse_json(conclusion))
            rules.append((premises, conclusion))

        cursor.close()
        return rules
    finally:
        connection.close()


def get_database_counts():
    """Return the number of stored facts and rules."""
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM facts")
        fact_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM inference_rules")
        rule_count = cursor.fetchone()[0]

        cursor.close()
        return fact_count, rule_count
    finally:
        connection.close()
