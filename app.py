import streamlit as st

st.set_page_config(page_title="Byline Times Style Editor", layout="wide")

# Simplified house style rule engine (editable/expandable)
def apply_house_style(text):
    changes = []
    edited = text

    replacements = {
        "PM": "Prime Minister",
        "government are": "Government is",
        "Conservative Government": "the Government",
        "govt": "Government",
        "the Leveson Inquiry": "the Leveson Inquiry – into the culture, practices and ethics of the press following the exposure of the phone-hacking scandal in 2011-12",
        "NHS England": "the NHS in England",
        "Parole Board": "the Parole Board for England and Wales"
    }

    for original, replacement in replacements.items():
        if original in edited:
            edited = edited.replace(original, replacement)
            changes.append(f"Replaced '{original}' with '{replacement}'")

    return edited, changes

# UI layout
st.title("Byline Times Style Editor (MVP)")

text_input = st.text_area("Paste your article text here:", height=300)

if st.button("Apply Byline House Style"):
    if not text_input.strip():
        st.warning("Please paste some article text.")
    else:
        edited_text, changes = apply_house_style(text_input)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Text")
            st.text_area("Original", text_input, height=300, disabled=True)
        with col2:
            st.subheader("Styled Version")
            styled = st.text_area("Edited", edited_text, height=300)
            st.download_button("Copy Final Text", styled, file_name="styled-article.txt")

        if changes:
            st.markdown("### Changes Made:")
            for change in changes:
                st.markdown(f"- {change}")
