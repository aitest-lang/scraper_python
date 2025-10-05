#!/usr/bin/env python3
"""
Reconnaissance Tool CLI
A Python CLI tool with Streamlit interface for scraping contact info from professional sites.
"""

import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(
        description="Reconnaissance tool for scraping contact information from professional sites"
    )

    parser.add_argument(
        '--url',
        type=str,
        help='Profile URL to scrape (e.g., LinkedIn profile URL)'
    )

    parser.add_argument(
        '--name',
        type=str,
        help='Person name to search for'
    )

    parser.add_argument(
        '--streamlit',
        action='store_true',
        help='Launch Streamlit web interface'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='data/results.json',
        help='Output JSON file path (default: data/results.json)'
    )

    args = parser.parse_args()

    if args.streamlit:
        # Launch Streamlit app
        print("Launching Streamlit interface...")
        try:
            subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'],
                         cwd=os.getcwd())
        except KeyboardInterrupt:
            print("\nStreamlit app stopped.")
        return

    if not args.url and not args.name:
        print("Error: Either --url or --name must be provided")
        parser.print_help()
        return

    # Import here to avoid import errors if dependencies not installed
    from scrapers.linkedin_scraper import scrape_linkedin_profile
    from utils.extractors import extract_contacts
    from utils.storage import save_to_json

    print("Starting reconnaissance...")

    try:
        if args.url:
            print(f"Scraping URL: {args.url}")
            # For now, assume LinkedIn URL
            raw_data = scrape_linkedin_profile(args.url)
        else:
            print(f"Searching for: {args.name}")
            # TODO: Implement name search
            print("Name search not implemented yet")
            return

        contacts = extract_contacts(raw_data)
        save_to_json(contacts, args.output)

        print(f"Results saved to {args.output}")
        print(f"Found {len(contacts.get('emails', []))} emails and {len(contacts.get('phones', []))} phones")

    except Exception as e:
        print(f"Error during scraping: {e}")
        return

if __name__ == "__main__":
    main()
