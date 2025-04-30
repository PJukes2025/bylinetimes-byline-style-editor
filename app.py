import streamlit as st
import re

st.set_page_config(page_title="Byline Times Style Editor", layout="wide")

def apply_house_style(text):
    changes = []
    edited = text

    rules = [
        # Batch 1 – Titles, politics, parties
        (r"\bPM\b", "Prime Minister"),
        (r"\bgovt\b", "Government"),
        (r"\bthe Conservative Government\b", "the Government"),
        (r"\bgovernment are\b", "Government is"),
        (r"\bthe UK government\b", "the UK Government"),
        (r"\bthe British Government\b", "the UK Government"),
        (r"\bthe English Government\b", "the UK Government"),
        (r"\bParole Board\b", "Parole Board for England and Wales"),
        (r"\bNHS England\b", "the NHS in England"),
        (r"(?<!the )Public Accounts Committee", "the House of Commons’ Public Accounts Committee"),
        (r"\bDame Meg Hillier\b", "Labour MP Dame Meg Hillier"),
        (r"\bthe Leveson Inquiry\b", 
         "the Leveson Inquiry – into the culture, practices and ethics of the press following the exposure of the phone-hacking scandal in 2011-12"),
        (r"\bTories\b", "the Conservatives"),
        (r"\bTory\b", "Conservative"),
        (r"\bLabour party\b", "Labour Party"),
        (r"\bLib Dems\b", "the Liberal Democrats"),
        (r"\bGreens\b", "the Green Party"),
        (r"\bThe Government are\b", "The Government is"),
        (r"\bThe NHS are\b", "The NHS is"),

        # Batch 2 – Numbers, dates, grammar
        (r"\b1\b", "one"),
        (r"\b2\b", "two"),
        (r"\b3\b", "three"),
        (r"\b4\b", "four"),
        (r"\b5\b", "five"),
        (r"\b6\b", "six"),
        (r"\b7\b", "seven"),
        (r"\b8\b", "eight"),
        (r"\b9\b", "nine"),
        (r"\b(\d{1,2})(st|nd|rd|th) (January|February|March|...)", r"\1 \3"),
        (r"\b(January|February|March|...)\s\d{1,2}, \d{4}", lambda m: m.group().replace(",", "")),
        (r"\b\d{1,2}(am|pm)\b", lambda m: m.group().lower()),
        (r"\b(\d+)\s?percent\b", r"\1%"),
        (r"\bper cent\b", "%"),
        (r"\bone half\b", "half"),
        (r"\btwo thirds\b", "two-thirds"),
        (r"\bthree quarters\b", "three-quarters"),
        (r"\b(\d+)-year old\b", r"\1-year-old"),
        (r"\b(\d+) years old\b", r"\1 years old"),
        (r"\b(\d{2}),\s?(who is|aged)\b", r"\1, aged"),
        (r"\b£(\d+)m\b", r"£\1 million"),
        (r"\b£(\d+)bn\b", r"£\1 billion"),
        (r"\$(\d+)m\b", r"$\1 million"),

        # Batch 3 – Quotes, media, terminology
        (r"‘", '"'),
        (r"’", '"'),
        (r"“", '"'),
        (r"”", '"'),
        (r"\bThe Sun\b", "*The Sun*"),
        (r"\bThe Times\b", "*The Times*"),
        (r"\bMailOnline\b", "*MailOnline*"),
        (r"\bThe Guardian\b", "*The Guardian*"),
        (r"\bThe Independent\b", "*The Independent*"),
        (r"\bThe BBC\b", "*The BBC*"),
        (r"\bPanorama\b", "*BBC’s Panorama*"),
        (r"\bNewsnight\b", "*BBC Newsnight*"),
        (r"\bstatutory instrument\b", "statutory instrument – a form of delegated legislation"),
        (r"\bprerogative power\b", "prerogative power – a residual executive power held by the Crown"),
        (r"\bearlier today\b", "today"),

        # UK spelling (selected)
        (r"\borganize\b", "organise"),
        (r"\bprioritize\b", "prioritise"),
        (r"\bcenter\b", "centre"),
        (r"\bdefense\b", "defence"),
        (r"\blicense\b", "licence"),
        (r"\btraveling\b", "travelling")
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

# Streamlit app UI
st.title("Byline Times Style Editor – Beta")

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
