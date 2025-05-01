import streamlit as st
import re
from difflib import SequenceMatcher

st.set_page_config(page_title="Byline Times Style Editor – Tracked Changes", layout="wide")

# -----------------------------------------
# BYLINE HOUSE STYLE RULES (Batches 1–6)
# -----------------------------------------

style_rules = [
    (r"\bPM\b", "Prime Minister"),
    (r"\bgovt\b", "Government"),
    (r"\bthe Conservative Government\b", "the Government"),
    (r"\bgovernment are\b", "Government is"),
    (r"\bThe Government are\b", "The Government is"),
    (r"\bthe UK government\b", "the UK Government"),
    (r"\bthe British Government\b", "the UK Government"),
    (r"\bthe English Government\b", "the UK Government"),
    (r"\bParole Board\b", "Parole Board for England and Wales"),
    (r"\bNHS England\b", "the NHS in England"),
    (r"\bDame Meg Hillier\b", "Labour MP Dame Meg Hillier"),
    (r"\bPublic Accounts Committee\b", "House of Commons’ Public Accounts Committee"),
    (r"\bTories\b", "Conservatives"),
    (r"\bLabour party\b", "Labour Party"),
    (r"\bLib Dems\b", "Liberal Democrats"),
    (r"\bGreens\b", "Green Party"),
    (r"\bThe NHS are\b", "The NHS is"),
    (r"\bMarch (\d{1,2})(st|nd|rd|th)?, (\d{4})", r"\1 March \3"),
    (r"[‘’]", "'"), (r"[“”]", '"'),
    (r"\bjust\b", "merely"),
    (r"\bespecially\b", "particularly"),
    (r"\bOK\b", "okay"),
    (r"\bBrexiteers\b", "Brexiters"),
    (r"\baddicts\b", "users of drugs"),
    (r"\bthe the\b", "the"),
]

# -----------------------------------------
# STYLE APPLICATION + CHANGE COMPARISON
# -----------------------------------------

def apply_house_style(text):
    """Returns styled text and a summary of what changed"""
    edited = text
    changes = []

    for pattern, replacement in style_rules:
        if re.search(pattern, edited):
            new = re.sub(pattern, replacement, edited)
            if new != edited:
                changes.append((pattern, replacement))
                edited = new
    return edited, changes

def inline_diff(a, b):
    """Returns inline diff with strikethroughs and bold insertions"""
    matcher = SequenceMatcher(None, a, b)
    result = []

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            result.append(a[i1:i2])
        elif op == "insert":
            result.append(f"**{b[j1:j2]}**")
        elif op == "delete":
            result.append(f"~~{a[i1:i2]}~~")
        elif op == "replace":
            result.append(f"~~{a[i1:i2]}~~**{b[j1:j2]}**")
    return "".join(result)

# -----------------------------------------
# STREAMLIT UI
# -----------------------------------------

st.title("Byline Times Style Editor – Tracked Changes")

text_input = st.text_area("Paste your article text below", height=300)
show_tracked = st.checkbox("Show tracked changes (inline view)", value=True)

if st.button("Apply House Style"):
    if not text_input.strip():
        st.warning("Please paste some text first.")
    else:
        styled_text, raw_changes = apply_house_style(text_input)
        diff_text = inline_diff(text_input, styled_text) if show_tracked else styled_text

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.text_area("Original", text_input, height=300, disabled=True)
        with col2:
            st.subheader("Edited" if not show_tracked else "Tracked Changes")
            st.markdown(diff_text, unsafe_allow_html=True)

        st.download_button("Copy Final Text", styled_text, file_name="styled-article.txt")

        if raw_changes:
            st.markdown("### Changes Applied:")
            for pattern, replacement in raw_changes:
                st.markdown(f"- Replaced `{pattern}` → **{replacement}**")
        else:
            st.info("No style changes were required.")
