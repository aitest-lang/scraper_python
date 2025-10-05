#!/usr/bin/env python3
"""
Streamlit Web Interface for Reconnaissance Tool
"""

import streamlit as st
import json
import os
from datetime import datetime

# Import our modules
from scrapers.linkedin_scraper import scrape_linkedin_profile
from utils.extractors import extract_contacts
from utils.storage import save_to_json, load_from_json
from utils.theharvester_integration import run_theharvester, extract_domain_from_url, combine_results

def main():
    st.set_page_config(
        page_title="Recon Tool",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🔍 Professional Contact Reconnaissance Tool")
    st.markdown("Extract contact information from professional profiles")

    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        output_file = st.text_input("Output file", value="data/results.json")
        auto_save = st.checkbox("Auto-save results", value=True)

    # Main content
    tab1, tab2 = st.tabs(["Scrape Profile", "View Results"])

    with tab1:
        st.header("Input")

        input_type = st.radio("Input type", ["Profile URL", "Person Name"])

        if input_type == "Profile URL":
            url = st.text_input("Profile URL", placeholder="https://www.linkedin.com/in/username")
            name = None
        else:
            name = st.text_input("Person Name", placeholder="John Doe")
            url = None

        if st.button("🔍 Start Reconnaissance", type="primary"):
            if not url and not name:
                st.error("Please provide either a URL or name")
                return

            with st.spinner("Scraping in progress..."):
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    status_text.text("Initializing scraper...")
                    progress_bar.progress(10)

                    if url:
                        status_text.text(f"Scraping {url}...")
                        raw_data = scrape_linkedin_profile(url)

                        # Run theHarvester for additional OSINT
                        progress_bar.progress(30)
                        status_text.text("Running OSINT reconnaissance...")

                        domain = extract_domain_from_url(url)
                        if domain:
                            harvester_results = run_theharvester(domain)
                            if 'error' not in harvester_results:
                                # Combine results
                                contacts_temp = extract_contacts(raw_data)
                                contacts = combine_results(contacts_temp, harvester_results)
                            else:
                                contacts = extract_contacts(raw_data)
                        else:
                            contacts = extract_contacts(raw_data)
                    else:
                        status_text.text(f"Searching for {name}...")
                        st.warning("Name search not implemented yet")
                        return

                    progress_bar.progress(70)
                    status_text.text("Extracting contacts...")

                    progress_bar.progress(80)
                    status_text.text("Saving results...")

                    if auto_save:
                        save_to_json(contacts, output_file)

                    progress_bar.progress(100)
                    status_text.text("Complete!")

                    # Display results
                    st.success("Reconnaissance complete!")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("📧 Emails Found")
                        emails = contacts.get('emails', [])
                        if emails:
                            for email in emails:
                                st.write(f"• {email}")
                        else:
                            st.write("No emails found")

                    with col2:
                        st.subheader("📞 Phones Found")
                        phones = contacts.get('phones', [])
                        if phones:
                            for phone in phones:
                                st.write(f"• {phone}")
                        else:
                            st.write("No phones found")

                    # Raw data expander
                    with st.expander("Raw Extracted Data"):
                        st.json(contacts)

                except Exception as e:
                    st.error(f"Error during scraping: {str(e)}")
                    st.exception(e)

    with tab2:
        st.header("Previous Results")

        if os.path.exists(output_file):
            try:
                data = load_from_json(output_file)
                st.json(data)
            except Exception as e:
                st.error(f"Error loading results: {e}")
        else:
            st.info("No results file found")

if __name__ == "__main__":
    main()
