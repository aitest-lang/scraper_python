#!/usr/bin/env python3
"""
General Web Scraper Module
For scraping contact information from various professional websites
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, Any, Optional

def scrape_website(url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Scrape contact information from a general website

    Args:
        url (str): Website URL to scrape
        headers (dict): Custom headers for request

    Returns:
        dict: Scraped data
    """
    if not headers:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    try:
        print(f"Scraping website: {url}")

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract basic information
        data = {
            'url': url,
            'title': extract_title(soup),
            'description': extract_description(soup),
            'contact_info': extract_contact_section(soup),
            'raw_html': str(soup)[:5000]  # First 5000 chars
        }

        return data

    except requests.RequestException as e:
        print(f"Request error for {url}: {e}")
        return {'error': str(e), 'url': url}
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {'error': str(e), 'url': url}

def extract_title(soup: BeautifulSoup) -> Optional[str]:
    """Extract page title"""
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.get_text().strip()
    return None

def extract_description(soup: BeautifulSoup) -> Optional[str]:
    """Extract meta description"""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        return meta_desc['content'].strip()
    return None

def extract_contact_section(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract contact information from common sections"""
    contact_info = {}

    # Look for contact sections
    contact_selectors = [
        'contact', 'contact-us', 'about', 'footer',
        '.contact', '#contact', '.footer', '#footer'
    ]

    for selector in contact_selectors:
        elements = soup.select(selector)
        if elements:
            text = ' '.join([elem.get_text() for elem in elements])
            if text.strip():
                contact_info[selector] = text.strip()
                break

    # If no specific section found, look for common contact patterns in body
    if not contact_info:
        body = soup.find('body')
        if body:
            contact_info['body_text'] = body.get_text()[:2000]  # First 2000 chars

    return contact_info

def scrape_multiple_urls(urls: list) -> Dict[str, Any]:
    """
    Scrape multiple URLs and combine results

    Args:
        urls (list): List of URLs to scrape

    Returns:
        dict: Combined results
    """
    results = {
        'urls_scraped': len(urls),
        'results': [],
        'combined_contacts': {
            'emails': set(),
            'phones': set()
        }
    }

    for url in urls:
        data = scrape_website(url)
        results['results'].append(data)

        # Extract emails and phones from this result
        text_content = extract_text_for_contact_search(data)

        emails = extract_emails_from_text(text_content)
        phones = extract_phones_from_text(text_content)

        results['combined_contacts']['emails'].update(emails)
        results['combined_contacts']['phones'].update(phones)

        # Rate limiting
        time.sleep(1)

    # Convert sets to lists
    results['combined_contacts']['emails'] = list(results['combined_contacts']['emails'])
    results['combined_contacts']['phones'] = list(results['combined_contacts']['phones'])

    return results

def extract_text_for_contact_search(data: Dict[str, Any]) -> str:
    """Extract text content for contact pattern matching"""
    text_parts = []

    if data.get('title'):
        text_parts.append(data['title'])
    if data.get('description'):
        text_parts.append(data['description'])

    contact_info = data.get('contact_info', {})
    for key, value in contact_info.items():
        text_parts.append(value)

    if data.get('raw_html'):
        text_parts.append(data['raw_html'])

    return ' '.join(text_parts)

def extract_emails_from_text(text: str) -> list:
    """Extract emails from text using regex"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text, re.IGNORECASE)
    return list(set(matches))  # Remove duplicates

def extract_phones_from_text(text: str) -> list:
    """Extract phone numbers from text using regex"""
    phone_pattern = r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}'
    matches = re.findall(phone_pattern, text)
    # Clean and deduplicate
    phones = []
    for match in matches:
        clean = re.sub(r'[^\d]', '', match)
        if len(clean) >= 10:
            phones.append(clean)
    return list(set(phones))

# Professional site templates
PROFESSIONAL_SITES = {
    'linkedin': 'linkedin.com',
    'xing': 'xing.com',
    'viadeo': 'viadeo.com',
    'about_me': 'about.me',
    'angel_list': 'angel.co',
    'crunchbase': 'crunchbase.com'
}

def detect_site_type(url: str) -> str:
    """Detect the type of professional site from URL"""
    for site_type, domain in PROFESSIONAL_SITES.items():
        if domain in url:
            return site_type
    return 'general'
