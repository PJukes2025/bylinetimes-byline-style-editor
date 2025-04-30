import re

def apply_house_style(text):
    changes = []
    edited = text

    # Define replacements as (pattern, replacement) tuples
    replacements = [
        # Government and political institutions
        (r"\bPM\b", "Prime Minister"),
        (r"\bgovt\b", "Government"),
        (r"\bthe Conservative Government\b", "the Government"),
        (r"\bgovernment are\b", "Government is"),
        (r"\bthe UK government\b", "the UK Government"),
        (r"\bthe British Government\b", "the UK Government"),
        (r"\bthe English Government\b", "the UK Government"),
        (r"\bParole Board\b", "Parole Board for England and Wales"),
        (r"\bNHS England\b", "the NHS in England"),

        # Committees and proper naming
        (r"\bPublic Accounts Committee\b", "the House of Commons’ Public Accounts Committee"),
        (r"\bDame Meg Hillier\b", "Labour MP Dame Meg Hillier"),
        (r"\bthe Leveson Inquiry\b", 
         "the Leveson Inquiry – into the culture, practices and ethics of the press following the exposure of the phone-hacking scandal in 2011-12"),

        # Parties
        (r"\bTories\b", "the Conservatives"),
        (r"\bTory\b", "Conservative"),
        (r"\bLabour party\b", "Labour Party"),
        (r"\bLib Dems\b", "the Liberal Democrats"),
        (r"\bGreens\b", "the Green Party"),

        # Singular/plural consistency for institutions
        (r"\bThe Government are\b", "The Government is"),
        (r"\bThe NHS are\b", "The NHS is"),

        # Number formatting (1–9 as words)
        (r"\b1\b", "one"),
        (r"\b2\b", "two"),
        (r"\b3\b", "three"),
        (r"\b4\b", "four"),
        (r"\b5\b", "five"),
        (r"\b6\b", "six"),
        (r"\b7\b", "seven"),
        (r"\b8\b", "eight"),
        (r"\b9\b", "nine"),
    ]

    # Apply replacements
    for pattern, replacement in replacements:
        if re.search(pattern, edited):
            edited = re.sub(pattern, replacement, edited)
            changes.append(f"Replaced '{pattern}' with '{replacement}'")

    return edited, changes
