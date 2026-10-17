
from knowledge_base import FACTS, RULES
from inference_engine import forward_chain

all_facts, trace = forward_chain(FACTS, RULES)

print("Initial facts:", len(FACTS))
print("Total facts after inference:", len(all_facts))
print("New facts inferred:", len(trace))

print("\nInferred conclusions:")

for item in trace:
    print(item["fact"])

print("\nAdmission eligibility checks:")

for student in ["ali", "sara", "usman"]:
    conclusion = ("admission_eligible", student, "ai")
    print(student, "->", conclusion in all_facts)
