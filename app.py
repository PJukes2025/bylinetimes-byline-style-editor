import streamlit as st
import re
from difflib import SequenceMatcher

st.set_page_config(page_title="Byline Times Style Editor – Tracked", layout="wide")

# ---------- HOUSE STYLE RULES (BATCHES 1–6) ----------
house_style_rules = [
    # Batch 1–2
    (r"\bPM\b", "Prime Minister"),
    (r"\bgovt\b", "Government"),
    (r"\bgovernment are\b", "Government is"),
    (r"\bThe Government are\b", "The Government is"),
    (r"\bTories\b", "Conservatives"),
    (r"\bLib Dems\b", "Liberal Democrats"),
    (r"\bBrexiteers\b", "Brexiters"),
    (r"\baddicts\b", "users of drugs"),
    (r"\bMarch (\d{1,2})(st|nd|rd|th)?, (\d{4})", r"\1 March \3"),
    (r"\b1\b", "one"), (r"\b2\b", "two"), (r"\b3\b", "three"),

    # Batch 3–4
    (r"\bjust\b", "merely"),
    (r"\bespecially\b", "particularly"),
    (r"\bOK\b", "okay"),
    (r"[‘’]", "'"),
    (r"[“”]", '"'),
    (r"\bcontroversial\b", "widely debated"),
    (r"\bshock\b", "unexpected"),
    (r"\bslammed\b", "strongly criticised"),
    (r"\bhit out at\b", "criticised"),

    # Batch 5
    (r"\bdefendant\b", "the person accused"),
    (r"\bclaimant\b", "the person claiming benefits"),

    # Batch 6
    (r"\bshock\b", "unexpected"),
    (r"\bcontroversial\b", "widely debated"),
    (r"\bthe the\b", "the"),
]

def normalise_quotes(text):
    return text.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')

def apply_house_style(text):
    edited = normalise_quotes(text)
    changes = []
    for pattern, replacement in house_style_rules:
        if re.search(pattern, edited):
            new_text = re.sub(pattern, replacement, edited)
            if new_text != edited:
                changes.append((pattern, replacement))
                edited = new_text
    return edited, changes

# ---------- INLINE DIFF + PARAGRAPH PRESERVATION ----------

def diff_paragraphs(original, edited):
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
                result.append(diff_line(orig, edit))
            for j in range(j1 + (i2 - i1), j2):
                result.append(f"**{edited_paras[j]}**")
            for i in range(i1 + (j2 - j1), i2):
                result.append(f"~~{original_paras[i]}~~")

    return '\n\n'.join(result)

def diff_line(a, b):
    matcher = SequenceMatcher(None, a, b)
    result = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result.append(a[i1:i2])
        elif tag == 'replace':
            result.append(f"~~{a[i1:i2]}~~ **{b[j1:j2]}**")
        elif tag == 'delete':
            result.append(f"~~{a[i1:i2]}~~")
        elif tag == 'insert':
            result.append(f"**{b[j1:j2]}**")
    return ''.join(result)

# ---------- STREAMLIT UI ----------

st.title("Byline Times Style Editor – Tracked & Clean Output")

text_input = st.text_area("Paste your article text below", height=300)
show_tracked = st.checkbox("Show tracked changes", value=True)

if st.button("Apply House Style"):
    if not text_input.strip():
        st.warning("Please paste some text first.")
    else:
        styled_text, changes = apply_house_style(text_input)
        output = diff_paragraphs(text_input, styled_text) if show_tracked else styled_text

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.text_area("Original", text_input, height=300, disabled=True)
        with col2:
            st.subheader("Edited" if not show_tracked else "Tracked Changes")
            st.markdown(output, unsafe_allow_html=True)

        st.download_button("Copy Final Text", styled_text, file_name="styled-article.txt")

        if changes:
            st.markdown("### Changes Applied:")
            for pat, rep in changes:
                st.markdown(f"- `{pat}` → **{rep}**")
        else:
            st.info("No style changes were applied.")
