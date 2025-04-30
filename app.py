import streamlit as st
import re

st.set_page_config(page_title="Byline Times Style Editor", layout="wide")

def apply_house_style(text):
    changes = []
    edited = text

    # Define Byline Times house style rules
    rules = [
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

        # Singular/plural fixes
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

    for pattern, replacement in rules:
        if re.search(pattern, edited):
            edited = re.sub(pattern, replacement, edited)
            changes.append(f"Replaced '{pattern}' with '{replacement}'")

    return edited, changes

# Streamlit UI
st.title("Byline Times Style Editor – MVP")

text_input = st.text_area("Paste your article text below", height=300)

if st.button("Apply House Style"):
    if not text_input.strip():
        st.warning("Please paste some text first.")
    else:
        edited_text, changes = apply_house_style(text_input)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Text")
            st.text_area("Original", text_input, height=300, disabled=True)
        with col2:
            st.subheader("Edited Version")
            st.text_area("Styled", edited_text, height=300)
            st.download_button("Copy Final Text", edited_text, file_name="styled-article.txt")

        if changes:
            st.markdown("### Changes Applied:")
            for change in changes:
                st.markdown(f"- {change}")
        else:
            st.info("No style changes were required.")
