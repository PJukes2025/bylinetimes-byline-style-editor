import streamlit as st
import re

st.set_page_config(page_title="Byline Times Style Editor", layout="wide")

def apply_house_style(text):
    changes = []
    edited = text

    rules = [

        # --- Batch 1–2: Political, numbers, institutions ---
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
        (r"\b(Dame Meg Hillier)\b", "Labour MP Dame Meg Hillier"),
        (r"\bthe Leveson Inquiry\b", 
         "the Leveson Inquiry – into the culture, practices and ethics of the press following the exposure of the phone-hacking scandal in 2011-12"),
        (r"\bPublic Accounts Committee\b", "House of Commons’ Public Accounts Committee"),
        (r"\bTories\b", "Conservatives"),
        (r"\bLabour party\b", "Labour Party"),
        (r"\bLib Dems\b", "Liberal Democrats"),
        (r"\bGreens\b", "Green Party"),
        (r"\bThe NHS are\b", "The NHS is"),
        (r"\b1\b", "one"), (r"\b2\b", "two"), (r"\b3\b", "three"),
        (r"\b4\b", "four"), (r"\b5\b", "five"), (r"\b6\b", "six"),
        (r"\b7\b", "seven"), (r"\b8\b", "eight"), (r"\b9\b", "nine"),
        (r"\b(\d+)-year old\b", r"\1-year-old"),
        (r"\b(\d+) years old\b", r"\1 years old"),
        (r"\b(\d+)\s?percent\b", r"\1%"),
        (r"\bper cent\b", "%"),
        (r"\bone half\b", "half"),
        (r"\btwo thirds\b", "two-thirds"),
        (r"\bthree quarters\b", "three-quarters"),
        (r"\b£(\d+)m\b", r"£\1 million"),
        (r"\b£(\d+)bn\b", r"£\1 billion"),
        (r"\$(\d+)m\b", r"$\1 million"),
        (r"\bMarch (\d{1,2})(st|nd|rd|th)?, (\d{4})", r"\1 March \3"),

        # --- Batch 3: Quotation, media, explanations ---
        (r"[‘’]", "'"), (r"[“”]", '"'),
        (r"\bThe Sun\b", "*The Sun*"),
        (r"\bThe Guardian\b", "*The Guardian*"),
        (r"\bThe Times\b", "*The Times*"),
        (r"\bMailOnline\b", "*MailOnline*"),
        (r"\bThe Independent\b", "*The Independent*"),
        (r"\bThe BBC\b", "*The BBC*"),
        (r"\bPanorama\b", "*BBC’s Panorama*"),
        (r"\bNewsnight\b", "*BBC Newsnight*"),
        (r"\bstatutory instrument\b", "statutory instrument – a form of delegated legislation"),
        (r"\bprerogative power\b", "prerogative power – a residual executive power held by the Crown"),

        # --- Batch 4: Tone, editorial phrasing ---
        (r"\bespecially\b", "particularly"),
        (r"\bjust\b", "merely"),
        (r"\bneeded\b", "required"),
        (r"\bgot\b", "obtained"),
        (r"\bOK\b", "okay"),
        (r"\bBrexiteers\b", "Brexiters"),
        (r"\byesterday\b", "on [insert date]"),
        (r"\blast week\b", "last week [insert date range]"),
        (r"\bI think\b", "It could be argued that"),
        (r"\bwe need\b", "some argue there is a need to"),
        (r"\bmay well\b", "may"),
        (r"\bcould well\b", "could"),
        (r"\bmight well\b", "might"),

        # --- Batch 5: Person-first, social affairs, courts ---
        (r"\baddicts\b", "users of drugs"),
        (r"\bdrug addicts\b", "users of drugs"),
        (r"\bjunkies\b", "users of drugs"),
        (r"\baddicted to drugs\b", "experiencing problematic drug use"),
        (r"\balcoholics\b", "those who abuse alcohol"),
        (r"\blost the plot\b", "became distressed"),
        (r"\bcrazy\b", "unwell"),
        (r"\bmental\b", "experiencing mental illness"),
        (r"\bpsychotic\b", "in a mental health crisis"),
        (r"\basylum\b", "psychiatric facility"),
        (r"\bclaimant\b", "the person claiming benefits"),
        (r"\bdefendant\b", "the person accused"),
        (r"\boffender\b", "the person who committed the offence"),
        (r"\bbehind bars\b", "in prison"),
        (r"\bthe prisoner\b", "the person in prison"),
        (r"\bvictim of domestic abuse\b", "survivor of domestic abuse"),
        (r"\bthe disabled\b", "disabled people"),
        (r"\bthe mentally ill\b", "people experiencing mental illness"),
        (r"\bservice users\b", "those receiving services"),

        # --- Batch 6: Editorial voice and cliché removal ---
        (r"\bslammed\b", "strongly criticised"),
        (r"\bhit out at\b", "criticised"),
        (r"\btorched\b", "criticised"),
        (r"\blast\b", "criticised"),
        (r"\bsparked outrage\b", "drew criticism"),
        (r"\bbrand new\b", "new"),
        (r"\bcontroversial\b", "widely debated"),
        (r"\bshock\b", "unexpected"),
        (r"\bshocking\b", "notable"),
        (r"\bplunged into chaos\b", "faced major disruption"),
        (r"\bin meltdown\b", "under severe strain"),
        (r"\bstormed\b", "entered"),
        (r"\bunder fire\b", "facing scrutiny"),
        (r"\bin chaos\b", "in disarray"),

        # UK spelling
        (r"\borganize\b", "organise"),
        (r"\bprioritize\b", "prioritise"),
        (r"\bcenter\b", "centre"),
        (r"\bdefense\b", "defence"),
        (r"\blicense\b", "licence"),
        (r"\btraveling\b", "travelling"),

        # Final safety net for duplicate "the the"
        (r"\bthe the\b", "the")
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
st.title("Byline Times Style Editor – Batch 6")

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
