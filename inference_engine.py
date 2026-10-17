
"""
Forward-chaining inference engine for the FOL expert system.
Compatible with the FACTS and RULES format in knowledge_base.py.
"""


def unify(pattern, fact, bindings=None):
    """Match a predicate pattern against a fact."""
    if bindings is None:
        bindings = {}

    if len(pattern) != len(fact):
        return None

    if pattern[0] != fact[0]:
        return None

    result = bindings.copy()

    for term, value in zip(pattern[1:], fact[1:]):
        if isinstance(term, str) and term.startswith("?"):
            if term in result:
                if result[term] != value:
                    return None
            else:
                result[term] = value
        elif term != value:
            return None

    return result


def match_premises(premises, facts, bindings=None):
    """Find substitutions satisfying every rule premise."""
    if bindings is None:
        bindings = {}

    if not premises:
        yield bindings
        return

    first = premises[0]
    remaining = premises[1:]

    for fact in facts:
        new_bindings = unify(first, fact, bindings)

        if new_bindings is not None:
            yield from match_premises(
                remaining, facts, new_bindings
            )


def substitute(pattern, bindings):
    """Replace variables with their bound values."""
    return tuple(
        bindings.get(term, term)
        if isinstance(term, str) and term.startswith("?")
        else term
        for term in pattern
    )


def forward_chain(initial_facts, rules):
    """
    Repeatedly apply rules until no new facts can be derived.

    Returns:
        all_facts: set of known and inferred facts
        trace: explanations of newly inferred facts
    """
    all_facts = {tuple(fact) for fact in initial_facts}
    trace = []

    changed = True

    while changed:
        changed = False
        current_facts = list(all_facts)

        for premises, conclusion in rules:
            for bindings in match_premises(
                premises, current_facts
            ):
                new_fact = substitute(conclusion, bindings)

                if new_fact not in all_facts:
                    all_facts.add(new_fact)
                    trace.append({
                        "fact": new_fact,
                        "rule": (premises, conclusion),
                        "bindings": bindings.copy(),
                    })
                    changed = True

    return all_facts, trace
