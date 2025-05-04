import streamlit as st
import re
from difflib import SequenceMatcher
import uuid

st.set_page_config(page_title="Byline Times Style Editor", layout="wide")

# ---------- RULESETS ----------
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
    ],
}
# ---------- NORMALISE QUOTES ----------
def normalise_quotes(text):
    return text.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')

# ---------- COMPILE SELECTED RULES ----------
def compile_rules(selected_batches):
    rules = []
    for batch in selected_batches:
        rules.extend(batch_rules.get(batch, []))
    return rules

# ---------- APPLY RULES AND CAPTURE EDITS ----------
def apply_rules_with_tracking(text, rules):
    edited = normalise_quotes(text)
    edits = []
    offset = 0
    for pattern, replacement in rules:
        for match in re.finditer(pattern, edited):
            start, end = match.span()
            original = edited[start:end]
            new_text = re.sub(pattern, replacement, original)
            if original != new_text:
                edit_id = str(uuid.uuid4())[:5]
                edits.append({
                    "id": edit_id,
                    "start": start,
                    "end": end,
                    "original": original,
                    "replacement": new_text,
                    "accepted": True  # default to accepted
                })
    edits.sort(key=lambda x: x["start"])
    return edited, edits
    # ---------- BUILD OUTPUT WITH ACCEPT/REJECT BUTTONS ----------
def build_diff_output(original_text, edits):
    output = []
    cursor = 0

    for edit in edits:
        start, end = edit["start"], edit["end"]
        output.append(original_text[cursor:start])

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(f'✅ Accept “{edit["replacement"]}”', key=f'accept_{edit["id"]}'):
                edit["accepted"] = True
        with col2:
            if st.button(f'❌ Reject “{edit["original"]}”', key=f'reject_{edit["id"]}'):
                edit["accepted"] = False

        # Show result based on state
        if edit["accepted"]:
            output.append(f'~~{edit["original"]}~~ **{edit["replacement"]}**')
        else:
            output.append(edit["original"])

        cursor = end

    output.append(original_text[cursor:])
    return ''.join(output)

# ---------- STREAMLIT UI ----------
st.title("Byline Times Style Editor – Final Version")

text_input = st.text_area("Paste your article text below:", height=300)

# Descriptive batch toggles
st.markdown("### Enable Style Rule Categories:")
active_batches = []
for batch in batch_rules.keys():
    if st.checkbox(batch, value=True):  # Default to ON
        active_batches.append(batch)

show_tracked = st.checkbox("Show tracked changes with Accept/Reject", value=True)

# Initialise session
if "edits" not in st.session_state:
    st.session_state.edits = []
if "original" not in st.session_state:
    st.session_state.original = ""
if "styled" not in st.session_state:
    st.session_state.styled = ""

if st.button("Apply House Style"):
    if not text_input.strip():
        st.warning("Please paste some text.")
    else:
        selected_rules = compile_rules(active_batches)
        styled_text, tracked_edits = apply_rules_with_tracking(text_input, selected_rules)
        st.session_state.original = text_input
        st.session_state.styled = styled_text
        st.session_state.edits = tracked_edits

# ---------- RENDER OUTPUT ----------
if st.session_state.get("edits"):
    st.markdown("### Edited Output")

    if show_tracked:
        tracked_output = build_diff_output(st.session_state.original, st.session_state.edits)
        st.markdown(tracked_output, unsafe_allow_html=True)
    else:
        # Generate clean output with only accepted edits
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
    st.info("✅ Accepted edits are applied to final output. Rejected edits are skipped.")






