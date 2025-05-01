import streamlit as st
import re

st.set_page_config(page_title="Byline Times Style Editor", layout="wide")

def apply_house_style(text):
    changes = []
    edited = text

    rules = [
        # --- Batch 1–3 (abbreviated here to focus on Batch 5) ---
        (r"\bPM\b", "Prime Minister"),
        (r"\bgovt\b", "Government"),
        (r"\bthe Conservative Government\b", "the Government"),
        (r"\bgovernment are\b", "Government is"),
        (r"\bThe Government are\b", "The Government is"),
        (r"\bthe Tories\b", "the Conservatives"),
        (r"\bTories\b", "the Conservatives"),
        (r"\bLib Dems\b", "the Liberal Democrats"),
        (r"\bMarch (\d{1,2})(st|nd|rd|th)?, (\d{4})", r"\1 March \3"),  # US → UK date format
        (r"\bthe the\b", "the"),  # generic fallback

        # --- Batch 5: Social affairs and legal style ---

        # Drug/alcohol users
        (r"\baddicts\b", "users of drugs"),
        (r"\bdrug addicts\b", "users of drugs"),
        (r"\bjunkies\b", "users of drugs"),
        (r"\baddicted to drugs\b", "experiencing problematic drug use"),
        (r"\balcoholics\b", "those who abuse alcohol"),

        # Mental health sensitivity
        (r"\blost the plot\b", "became distressed"),
        (r"\bcrazy\b", "unwell"),
        (r"\bmental\b", "experiencing mental illness"),
        (r"\bpsychotic\b", "in a mental health crisis"),
        (r"\basylum\b", "psychiatric facility"),

        # Legal terms
        (r"\bclaimant\b", "the person claiming benefits"),
        (r"\bdefendant\b", "the person accused"),
        (r"\boffender\b", "the person who committed the offence"),
        (r"\bbehind bars\b", "in prison"),
        (r"\bthe prisoner\b", "the person in prison"),
        (r"\bvictim of domestic abuse\b", "survivor of domestic abuse"),

        # Court formatting
        (r"\bJudge ([A-Z][a-z]+)\b", r"Judge \1"),
        (r"\bThe trial took place at ([A-Z].+? Court)\b", r"the trial, set for \1"),

        # Disability/identity-first language
        (r"\bthe disabled\b", "disabled people"),
        (r"\bthe mentally ill\b", "people experiencing mental illness"),
        (r"\bservice users\b", "those receiving services"),

        # Clean quotation marks
        (r"[‘’]", "'"),
        (r"[“”]", '"'),
    ]

    for pattern, replacement in rules:
        try:
            if re.search(pattern, edited):
                new_text = re.sub(pattern, replacement, edited)
                if new_text != edited:
                    changes.append(f"Replaced '{pattern}' with '{replacement}'")
                    edited = new_text
        except Exception as e:
            changes.append(f"Error processing '{pattern}': {str(e)}")

    return edited, changes

# Streamlit UI
st.title("Byline Times Style Editor – Batch 5")

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
