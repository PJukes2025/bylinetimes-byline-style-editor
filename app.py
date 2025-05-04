import streamlit as st
import re
from difflib import SequenceMatcher
import uuid

st.set_page_config(page_title="Byline Times Style Editor", layout="wide")

# ---------- RULESET DEFINITIONS ----------
batch_rules = {
    "Political Terminology": [
        (r"\bPM\b", "Prime Minister"),
        (r"\bgovt\b", "Government"),
        (r"\bthe Conservative Government\b", "the Government"),
        (r"\bthe UK government\b", "the UK Government"),
        (r"\bthe British Government\b", "the UK Government"),
        (r"\bthe English Government\b", "the UK Government"),
    ],
    "Institutional References": [
        (r"\bgovernment are\b", "Government is"),
        (r"\bThe Government are\b", "The Government is"),
        (r"\bThe NHS are\b", "The NHS is"),
        (r"\bNHS England\b", "the NHS in England"),
        (r"\bPublic Accounts Committee\b", "House of Commons’ Public Accounts Committee"),
        (r"\bDame Meg Hillier\b", "Labour MP Dame Meg Hillier"),
    ],
    "Party & Quote Formatting": [
        (r"\bTories\b", "Conservatives"),
        (r"\bLabour party\b", "Labour Party"),
        (r"\bLib Dems\b", "Liberal Democrats"),
        (r"\bGreens\b", "Green Party"),
        (r"[‘’]", "'"),
        (r"[“”]", '"'),
        (r"\bMarch (\d{1,2})(st|nd|rd|th)?, (\d{4})", r"\1 March \3"),
        (r"\b(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})", r"\2 \1 \3"),
    ],
    "Style & Clarity": [
        (r"\bjust\b", "merely"),
        (r"\bespecially\b", "particularly"),
        (r"\bOK\b", "okay"),
        (r"\bneeded\b", "required"),
        (r"\bgot\b", "obtained"),
    ],
    "Person-First Language": [
        (r"\baddicts\b", "users of drugs"),
        (r"\bdrug addicts\b", "users of drugs"),
        (r"\bdefendant\b", "the person accused"),
        (r"\bclaimant\b", "the person claiming benefits"),
        (r"\boffender\b", "the person who committed the offence"),
        (r"\bvictim of domestic abuse\b", "survivor of domestic abuse"),
    ],
    "Headline Clichés": [
        (r"\bshock\b", "unexpected"),
        (r"\bcontroversial\b", "widely debated"),
        (r"\bslammed\b", "strongly criticised"),
        (r"\bhit out at\b", "criticised"),
        (r"\bthe the\b", "the"),
    ]
}
# ---------- NORMALISERS ----------
def normalise_quotes(text):
    return text.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')

# ---------- COMPILE RULES FROM TOGGLES ----------
def compile_rules(selected_batches):
    rules = []
    for batch in selected_batches:
        rules.extend(batch_rules.get(batch, []))
    return rules

# ---------- APPLY RULES + TRACK CHANGES WITH IDs ----------
def apply_rules_with_tracking(text, rules):
    edited = normalise_quotes(text)
    edits = []
    for pattern, replacement in rules:
        for match in re.finditer(pattern, edited):
            start, end = match.span()
            original = edited[start:end]
            if original != replacement:
                edit_id = str(uuid.uuid4())
                edits.append({
                    "id": edit_id,
                    "start": start,
                    "end": end,
                    "original": original,
                    "replacement": re.sub(pattern, replacement, original),
                    "accepted": None
                })
    # Sort by position to avoid overlap issues
    edits.sort(key=lambda x: x["start"])
    return edited, edits
    # ---------- DIFF VIEW WITH BUTTON CONTROLS ----------
def diff_line_with_ui(a, b):
    a = normalise_quotes(a)
    b = normalise_quotes(b)
    matcher = SequenceMatcher(None, a, b)
    result = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result.append(a[i1:i2])
        elif tag == 'replace':
            replacement = b[j1:j2]
            original = a[i1:i2]
            result.append(
                f"~~{original}~~ **{replacement}**  "
                f"{st.button(f'Accept \"{replacement}\"', key=f'accept_{i1}')}"
                f"{st.button(f'Reject \"{original}\"', key=f'reject_{i1}')}"
            )
        elif tag == 'delete':
            original = a[i1:i2]
            result.append(
                f"~~{original}~~ "
                f"{st.button(f'Reject \"{original}\"', key=f'reject_{i1}')}"
            )
        elif tag == 'insert':
            replacement = b[j1:j2]
            result.append(
                f"**{replacement}** "
                f"{st.button(f'Accept \"{replacement}\"', key=f'accept_{j1}')}"
            )
    return ''.join(result)

    # ---------- STREAMLIT UI ----------
st.title("Byline Times Style Editor – Interactive Review")

text_input = st.text_area("Paste your article text below:", height=300)

# Descriptive batch toggle checkboxes
st.markdown("### Enable Style Rule Categories:")
active_batches = []
for batch_name in batch_rules.keys():
    if st.checkbox(batch_name, value=True):
        active_batches.append(batch_name)

show_tracked = st.checkbox("Show tracked changes and Accept/Reject controls", value=True)

# Initialise session state
if "edits" not in st.session_state:
    st.session_state.edits = []

if st.button("Apply House Style"):
    if not text_input.strip():
        st.warning("Please paste text first.")
    else:
        selected_rules = compile_rules(active_batches)
        styled_text, tracked_edits = apply_rules_with_tracking(text_input, selected_rules)
        st.session_state.edits = tracked_edits
        st.session_state.original = text_input
        st.session_state.styled = styled_text
        # ---------- OUTPUT VIEW ----------
if st.session_state.get("edits"):
    st.markdown("### Edited Output")

    if show_tracked:
        tracked_output = build_diff_output(st.session_state.original, st.session_state.edits)
        st.markdown(tracked_output, unsafe_allow_html=True)
    else:
        # Reconstruct output from accept/reject decisions
        clean_output = []
        cursor = 0
        for edit in st.session_state.edits:
            start, end = edit["start"], edit["end"]
            clean_output.append(st.session_state.original[cursor:start])
            if edit["accepted"]:
                clean_output.append(edit["replacement"])
            else:
                clean_output.append(edit["original"])
            cursor = end
        clean_output.append(st.session_state.original[cursor:])
        clean_text = ''.join(clean_output)

        st.text_area("Final Clean Output", clean_text, height=300)
        st.download_button("Download Final Text", clean_text, file_name="edited_output.txt")

    st.markdown("---")
    st.markdown("✅ Accepted edits will be applied to final output. Rejected ones are skipped.")




