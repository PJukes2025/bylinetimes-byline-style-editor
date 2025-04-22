import streamlit as st

st.set_page_config(page_title="Byline Times Style Editor", layout="wide")

def apply_house_style(text, article_type):
    # Placeholder: In production this would be more complex
    changes = []
    edited = text

    if "PM" in edited:
        edited = edited.replace("PM", "Prime Minister")
        changes.append("Replaced 'PM' with 'Prime Minister'")

    if "okay" in edited:
        edited = edited.replace("okay", "okay")  # already correct but log
        changes.append("Confirmed 'okay' is correctly styled")

    if "government are" in edited.lower():
        edited = edited.replace("Government are", "Government is")
        changes.append("Changed 'Government are' to 'Government is'")

    return edited, changes

st.title("Byline Times Style Editor")

st.markdown("Paste or upload your article and apply the Byline Times house style.")

article_type = st.selectbox("Select article type:", ["News", "Opinion", "Feature"])

text_input = st.text_area("Paste your article text here:", height=300)

uploaded_file = st.file_uploader("Or upload a .txt file", type=["txt"])
if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    text_input = content

if st.button("Apply Byline House Style"):
    if not text_input.strip():
        st.warning("Please provide article text first.")
    else:
        edited_text, changes = apply_house_style(text_input, article_type)
        st.success("Style applied successfully!")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.text_area("Original Text", text_input, height=300, disabled=True)
        with col2:
            st.subheader("Edited")
            st.text_area("Styled Text", edited_text, height=300)

        if changes:
            st.markdown("### Changes Made:")
            for change in changes:
                st.markdown(f"- {change}")

        st.markdown("Copy the final text above and paste into WordPress.")
