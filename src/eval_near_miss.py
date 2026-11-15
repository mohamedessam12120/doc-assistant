from ask import ask

# Questions near the documents' topics whose answers are NOT in the documents
NEAR_MISS = [
    "How many days of annual leave do contractors get?",
    "Can I carry over unused sick leave?",
    "How many public holidays are there per year?",
    "Is there a childcare allowance?",
    "Can I work remotely from another country?",
    "What is the parking allowance for employees?",
]

# Held-out set: written after looking at the failures above
HELD_OUT = [
    "Can I carry over unused emergency leave?",
    "How many days of marriage leave are there?",
    "Is there a housing allowance?",
    "Can I take annual leave in half days?",
    "Can I carry over my unused training budget?",
    "Can I get an advance on my salary?",
]


def run(name, questions):
    refused = 0
    print(f"\n== {name} ==")
    for q in questions:
        answer, _ = ask(q)
        ok = answer.strip().lower().startswith("i don't know")
        refused += ok
        print(("OK   " if ok else "FAIL ") + q + "\n      -> " + answer.replace("\n", " ")[:200])
    print(f"{name}: refused {refused}/{len(questions)}")


run("NEAR_MISS", NEAR_MISS)
run("HELD_OUT", HELD_OUT)