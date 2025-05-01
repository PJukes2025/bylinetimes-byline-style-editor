import streamlit as st
import re
from difflib import SequenceMatcher

st.set_page_config(page_title="Byline Times Style Editor – Tracked Changes", layout="wide")

# House style rules (abbreviated to key examples for speed; extend as needed)
style_rules = [
    (r"\bjust\b", "merely"),
    (r"[‘’]", "'"),
    (r"[“”]", '"'),
    (r"\bPM\b", "Prime Minister"),
    (r"\bgovt\b", "Government"),
    (r"\bTories\b", "Conservatives"),
    (r"\bLib Dems\b", "Liberal Democrats"),
    (r"\baddicts\b", "users of drugs"),
    (r"\bdefendant\b", "the person accused"),
    (r"\bMarch (\d{1,2})(st|nd|rd|th)?, (\d{4})", r"\1 March \3"),
    (r"\bthe the\b", "the")
]

# Apply style rules and record changes
def apply_house_style(text):
    edited = text
    changes = []

    for pattern, replacement in style_rules:
        if re.search(pattern, edited):
            new_text = re.sub(pattern, replacement, edited)
            if new_text != edited:
                changes.append((pattern, replacement))
                edited = new_text

    return edited, changes

# Inline diff for individual lines
def inline_diff_lines(original, edited):
    original_lines = original.splitlines()
    edited_lines = edited.splitlines()
    output_lines = []

    matcher = SequenceMatcher(None, original_lines, edited_lines)

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            output_lines.extend(original_lines[i1:i2])
        elif op == "replace":
            for o, e in zip(original_lines[i1:i2], edited_lines[j1:j2]):
                output_lines.append(inline_diff_text(o, e))
        elif op == "insert":
            for e in edited_lines[j1:j2]:
                output_lines.append(f"**{e}**")
        elif op == "delete":
            for o in original_lines[i1:i2]:
                output_lines.append(f"~~{o}~~")
    return "\n".join(output_lines)

# Inline diff at word-level (within a line)
def inline_diff_text(a, b):
    matcher = SequenceMatcher(None, a, b)
    result = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result.append(a[i1:i2])
        elif tag == 'replace':
            result.append(f"~~{a[i1:i2]}~~**{b[j1:j2]}**")
        elif tag == 'delete':
            result.append(f"~~{a[i1:i2]}~~")
        elif tag == 'insert':
            result.append(f"**{b[j1:j2]}**")
    return ''.join(result)

# --- Streamlit UI ---
st.title("Byline Times Style Editor – Tracked Inline View")

text_input = st.text_area("Paste your article text below", height=300)
show_tracked = st.checkbox("Show tracked changes (inline)", value=True)

if st.button("Apply Byline House Style"):
    if not text_input.strip():
        st.warning("Please paste some text first.")
    else:
        styled_text, change_log = apply_house_style(text_input)
        diff_view = inline_diff_lines(text_input, styled_text) if show_tracked else styled_text

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.text_area("Original", text_input, height=300, disabled=True)
        with col2:
            st.subheader("Edited Version" if not show_tracked else "Tracked Changes")
            st.markdown(diff_view, unsafe_allow_html=True)

        st.download_button("Copy Final Text", styled_text, file_name="styled-article.txt")

        if change_log:
            st.markdown("### Summary of Style Changes:")
            for pat, rep in change_log:
                st.markdown(f"- Replaced `{pat}` → **{rep}**")
        else:
            st.info("No style changes were needed.")

