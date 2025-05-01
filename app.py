import streamlit as st
import re
from difflib import SequenceMatcher

st.set_page_config(page_title="Byline Times Style Editor – Tracked Changes", layout="wide")

# --- QUOTE NORMALISER ---
def normalise_quotes(text):
    return text.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')

# --- HOUSE STYLE RULES (Batch 1–6, condensed) ---
style_rules = [
    # Batch 1–2: political and numeric
    (r"\bPM\b", "Prime Minister"),
    (r"\bgovt\b", "Government"),
    (r"\bgovernment are\b", "Government is"),
    (r"\bThe Government are\b", "The Government is"),
    (r"\bTories\b", "Conservatives"),
    (r"\bLib Dems\b", "Liberal Democrats"),
    (r"\baddicts\b", "users of drugs"),
    (r"\bMarch (\d{1,2})(st|nd|rd|th)?, (\d{4})", r"\1 March \3"),
    (r"\b1\b", "one"), (r"\b2\b", "two"), (r"\b3\b", "three"),

    # Batch 3–4: editorial tone and punctuation
    (r"\bjust\b", "merely"),
    (r"\bespecially\b", "particularly"),
    (r"\bOK\b", "okay"),
    (r"\bBrexiteers\b", "Brexiters"),
    (r"[‘’]", "'"), (r"[“”]", '"'),

    # Batch 5: person-first and court style
    (r"\bdefendant\b", "the person accused"),
    (r"\bclaimant\b", "the person claiming benefits"),

    # Batch 6: headline clichés
    (r"\bslammed\b", "strongly criticised"),
    (r"\bhit out at\b", "criticised"),
    (r"\bshock\b", "unexpected"),
    (r"\bcontroversial\b", "widely debated"),

    # Final safety fix
    (r"\bthe the\b", "the")
]

# --- APPLY HOUSE STYLE RULES ---
def apply_house_style(text):
    edited = normalise_quotes(text)
    changes = []

    for pattern, replacement in style_rules:
        if re.search(pattern, edited):
            new_text = re.sub(pattern, replacement, edited)
            if new_text != edited:
                changes.append((pattern, replacement))
                edited = new_text

    return edited, changes

# --- INLINE DIFF ---
def inline_diff_lines(original, edited):
    original_lines = normalise_quotes(original).splitlines()
    edited_lines = edited.splitlines()
    output_lines = []

    matcher = SequenceMatcher(None, original_lines, edited_lines)

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            output_lines.extend(original_lines[i1:i2])
        elif op in ("replace", "delete", "insert"):
            for i, j in zip(range(i1, i2), range(j1, j2)):
                a_line = original_lines[i] if i < len(original_lines) else ""
                b_line = edited_lines[j] if j < len(edited_lines) else ""
                output_lines.append(diff_line(a_line, b_line))
            for j in range(j1 + (i2 - i1), j2):
                output_lines.append(f"**{edited_lines[j]}**")
            for i in range(i1 + (j2 - j1), i2):
                output_lines.append(f"~~{original_lines[i]}~~")
    return "\n".join(output_lines)

def diff_line(a, b):
    matcher = SequenceMatcher(None, a, b)
    result = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            result.append(a[i1:i2])
        elif tag == "replace":
            result.append(f"~~{a[i1:i2]}~~**{b[j1:j2]}**")
        elif tag == "delete":
            result.append(f"~~{a[i1:i2]}~~")
        elif tag == "insert":
            result.append(f"**{b[j1:j2]}**")
    return ''.join(result)

# --- STREAMLIT UI ---
st.title("Byline Times Style Editor – Tracked Changes")

text_input = st.text_area("Paste your article text below", height=300)
show_tracked = st.checkbox("Show tracked changes (inline)", value=True)

if st.button("Apply House Style"):
    if not text_input.strip():
        st.warning("Please paste some text first.")
    else:
        styled_text, changes_applied = apply_house_style(text_input)
        diff_display = inline_diff_lines(text_input, styled_text) if show_tracked else styled_text

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Text")
            st.text_area("Original", text_input, height=300, disabled=True)
        with col2:
            st.subheader("Edited Version" if not show_tracked else "Tracked Changes")
            st.markdown(diff_display, unsafe_allow_html=True)

        st.download_button("Copy Final Text", styled_text, file_name="styled-article.txt")

        if changes_applied:
            st.markdown("### Summary of Replacements:")
            for pat, rep in changes_applied:
                st.markdown(f"- `{pat}` → **{rep}**")
        else:
            st.info("No style changes were made.")
