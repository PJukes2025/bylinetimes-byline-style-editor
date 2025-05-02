import streamlit as st
import re
from difflib import SequenceMatcher

st.set_page_config(page_title="Byline Times Style Editor", layout="wide")

# ---------- RULESET DEFINITIONS ----------
batch_rules = {
    "Batch 1": [
        (r"\bPM\b", "Prime Minister"),
        (r"\bgovt\b", "Government"),
        (r"\bthe Conservative Government\b", "the Government"),
        (r"\bthe UK government\b", "the UK Government"),
        (r"\bthe British Government\b", "the UK Government"),
        (r"\bthe English Government\b", "the UK Government"),
    ],
    "Batch 2": [
        (r"\bgovernment are\b", "Government is"),
        (r"\bThe Government are\b", "The Government is"),
        (r"\bThe NHS are\b", "The NHS is"),
        (r"\bNHS England\b", "the NHS in England"),
        (r"\bPublic Accounts Committee\b", "House of Commons’ Public Accounts Committee"),
        (r"\bDame Meg Hillier\b", "Labour MP Dame Meg Hillier"),
    ],
    "Batch 3": [
        (r"\bTories\b", "Conservatives"),
        (r"\bLabour party\b", "Labour Party"),
        (r"\bLib Dems\b", "Liberal Democrats"),
        (r"\bGreens\b", "Green Party"),
        (r"[‘’]", "'"),
        (r"[“”]", '"'),
        (r"\bMarch (\d{1,2})(st|nd|rd|th)?, (\d{4})", r"\1 March \3"),
    ],
    "Batch 4": [
        (r"\bjust\b", "merely"),
        (r"\bespecially\b", "particularly"),
        (r"\bOK\b", "okay"),
        (r"\bneeded\b", "required"),
        (r"\bgot\b", "obtained"),
    ],
    "Batch 5": [
        (r"\baddicts\b", "users of drugs"),
        (r"\bdrug addicts\b", "users of drugs"),
        (r"\bdefendant\b", "the person accused"),
        (r"\bclaimant\b", "the person claiming benefits"),
        (r"\boffender\b", "the person who committed the offence"),
        (r"\bvictim of domestic abuse\b", "survivor of domestic abuse"),
    ],
    "Batch 6": [
        (r"\bshock\b", "unexpected"),
        (r"\bcontroversial\b", "widely debated"),
        (r"\bslammed\b", "strongly criticised"),
        (r"\bhit out at\b", "criticised"),
        (r"\bthe the\b", "the"),
    ],
}
# ---------- QUOTE NORMALISER ----------
def normalise_quotes(text):
    return text.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')

# ---------- COMPILE SELECTED BATCHES ----------
def compile_rules(selected_batches):
    rules = []
    for batch in selected_batches:
        rules.extend(batch_rules.get(batch, []))
    return rules

# ---------- APPLY SELECTED RULES ----------
def apply_style_rules(text, rules):
    edited = normalise_quotes(text)
    changes = []
    for pattern, replacement in rules:
        if re.search(pattern, edited):
            new_text = re.sub(pattern, replacement, edited)
            if new_text != edited:
                changes.append((pattern, replacement))
                edited = new_text
    return edited, changes
    # ---------- PARAGRAPH DIFF WITH INLINE CHANGE DISPLAY ----------
def inline_diff_paragraphs(original, edited):
    original_paras = [p.strip() for p in original.split('\n') if p.strip()]
    edited_paras = [p.strip() for p in edited.split('\n') if p.strip()]
    matcher = SequenceMatcher(None, original_paras, edited_paras)
    result = []

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == 'equal':
            result.extend(original_paras[i1:i2])
        elif op in ('replace', 'delete', 'insert'):
            for i, j in zip(range(i1, i2), range(j1, j2)):
                orig = original_paras[i] if i < len(original_paras) else ''
                edit = edited_paras[j] if j < len(edited_paras) else ''
                result.append(diff_line_with_ui(orig, edit))
    return '\n\n'.join(result)

# ---------- INLINE CHANGE DISPLAY WITH PLACEHOLDER BUTTONS ----------
def diff_line_with_ui(a, b):
    a = normalise_quotes(a)
    b = normalise_quotes(b)
    matcher = SequenceMatcher(None, a, b)
    result = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result.append(a[i1:i2])
        elif tag == 'replace':
            result.append(
                f"~~{a[i1:i2]}~~ **{b[j1:j2]}** "
                f"[Accept] [Reject]"
            )
        elif tag == 'delete':
            result.append(f"~~{a[i1:i2]}~~ [Reject]")
        elif tag == 'insert':
            result.append(f"**{b[j1:j2]}** [Accept]")
    return ''.join(result)

# ---------- STREAMLIT UI ----------
st.title("Byline Times Style Editor – Full Batch Toggles & Tracked Changes")

text_input = st.text_area("Paste your article text below:", height=300)

st.markdown("### Select Batches to Apply:")
active_batches = []
for batch in batch_rules.keys():
    if st.checkbox(batch, value=True):  # All default ON
        active_batches.append(batch)

show_tracked = st.checkbox("Show tracked changes with Accept/Reject buttons", value=True)

if st.button("Apply House Style"):
    if not text_input.strip():
        st.warning("Please paste some text first.")
    else:
        selected_rules = compile_rules(active_batches)
        styled_text, change_log = apply_style_rules(text_input, selected_rules)
        display_output = inline_diff_paragraphs(text_input, styled_text) if show_tracked else styled_text

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.text_area("Original Text", text_input, height=300, disabled=True)
        with col2:
            st.subheader("Edited Version" if not show_tracked else "Tracked Changes")
            st.markdown(display_output, unsafe_allow_html=True)

        st.download_button("Copy Final Text", styled_text, file_name="styled-article.txt")

        if change_log:
            st.markdown("### Summary of Replacements:")
            for pat, rep in change_log:
                st.markdown(f"- `{pat}` → **{rep}**")
        else:
            st.info("No style changes were applied.")
