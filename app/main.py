import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    # Page Title and Description
    st.title("📧 Cold Mail Generator")
    st.markdown(
        """
        Generate personalized cold emails for job opportunities. Provide a job portal URL, 
        and let AI help you craft the perfect email to connect with recruiters.
        """,
        unsafe_allow_html=True,
    )
    st.divider()  # Adds a horizontal line for better section separation

    # Input Section
    col1, col2 = st.columns([3, 1])  # Create a 3:1 column ratio for input and button
    with col1:
        url_input = st.text_input(
            "🔗 Enter a Job Portal URL:",
            value="https://jobs.nike.com/?jobSearch=true&jsOffset=0&jsSort=posting_start_date&jsLanguage=en",
        )
    with col2:
        submit_button = st.button("🚀 Generate Emails", use_container_width=True)

    st.divider()

    # Output Section
    if submit_button:
        with st.spinner("Processing... Please wait."):
            try:
                loader = WebBaseLoader([url_input])
                data = clean_text(loader.load().pop().page_content)

                # Portfolio and job extraction
                portfolio.load_portfolio()
                jobs = llm.extract_jobs(data)

                # Display Results
                for idx, job in enumerate(jobs, start=1):
                    st.subheader(f"Job #{idx}: {job.get('title', 'Unknown Title')}")
                    st.markdown(f"**Company**: {job.get('company', 'Unknown')}")

                    skills = job.get('skills', [])
                    st.markdown(f"**Skills Required**: {', '.join(skills) if skills else 'N/A'}")

                    links = portfolio.query_links(skills)
                    email = llm.write_mail(job, links)

                    st.code(email, language='markdown')
                    st.divider()  # Separate job results visually
            except Exception as e:
                st.error(f"❌ An error occurred while processing: {e}")


if __name__ == "__main__":
    # Set Page Configurations
    st.set_page_config(
        layout="wide",
        page_title="Cold Email Generator",
        page_icon="📧",
    )
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)
