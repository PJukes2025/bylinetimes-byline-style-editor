import streamlit as st
import re
from difflib import SequenceMatcher

st.set_page_config(page_title="Byline Times Style Editor – Tracked Changes", layout="wide")

# House style rules (Batch 1–6, selected highlights)
style_rules = [
    (r"\bPM\b", "Prime Minister"),
    (r"\bgovt\b", "Government"),
    (r"\bjust\b", "merely"),
    (r"[‘’]", "'"),
    (r"[“”]", '"'),
    (r"\baddicts\b", "users of drugs"),
    (r"\bdefendant\b", "the person accused"),
    (r"\bTories\b", "Conservatives"),
    (r"\bLib Dems\b", "Liberal Democrats"),
    (r"\bcontroversial\b", "widely debated"),
    (r"\bshock\b", "unexpected"),
    (r"\bMarch (\d{1,2})(st|nd|rd|th)?, (\d{4})", r"\1 March \3"),
    (r"\bthe the\b", "the")
]

# Normalise quote characters
def normalise_quotes(text):
    return text.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')

# Apply all style edits
def apply_house_style(text):
    edited = normalise_quotes(text)
    changes = []
    for pattern, replacement in style_rules:
        if re.search(pattern, edited):
            new = re.sub(pattern, replacement, edited)
            if new != edited:
                changes.append((pattern, replacement))
                edited = new
    return edited, changes

# Inline word-level diff for paragraph pairs
def diff_paragraphs(original, edited):
    result = []
    o_paras = normalise_quotes(original).split('\n\n')
    e_paras = edited.split('\n\n')
    matcher = SequenceMatcher(None, o_paras, e_paras)

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            result.extend([para for para in o_paras[i1:i2]])
        elif op in ("replace", "delete", "insert"):
            for i, j in zip(range(i1, i2), range(j1, j2)):
                o_line = o_paras[i] if i < len(o_paras) else ""
                e_line = e_paras[j] if j < len(e_paras) else ""
                result.append(diff_line(o_line, e_line))
            for j in range(j1 + (i2 - i1), j2):
                result.append(f"**{e_paras[j]}**")
            for i in range(i1 + (j2 - j1), i2):
                result.append(f"~~{o_paras[i]}~~")

    return "\n\n".join(result)

# Word-level diff within paragraph
def diff_line(a, b):
    matcher = SequenceMatcher(None, a, b)
    result = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            result.append(a[i1:i2])
        elif tag == "replace":
            result.append(f"~~{a[i1:i2]}~~ **{b[j1:j2]}**")
        elif tag == "delete":
            result.append(f"~~{a[i1:i2]}~~")
        elif tag == "insert":
            result.append(f"**{b[j1:j2]}**")
    return ''.join(result)

# Streamlit UI
st.title("Byline Times Style Editor – Tracked Changes")

text_input = st.text_area("Paste your article text below", height=300)
show_tracked = st.checkbox("Show tracked changes (inline)", value=True)

if st.button("Apply House Style"):
    if not text_input.strip():
        st.warning("Please paste some text first.")
    else:
        styled_text, changes_applied = apply_house_style(text_input)
        display_text = diff_paragraphs(text_input, styled_text) if show_tracked else styled_text

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.text_area("Original Text", text_input, height=300, disabled=True)
        with col2:
            st.subheader("Edited" if not show_tracked else "Tracked View")
            st.markdown(display_text, unsafe_allow_html=True)

        st.download_button("Copy Final Text", styled_text, file_name="styled-article.txt")

        if changes_applied:
            st.markdown("### Summary of Style Fixes:")
            for pattern, replacement in changes_applied:
                st.markdown(f"- `{pattern}` → **{replacement}**")
        else:
            st.info("No style changes were applied.")
