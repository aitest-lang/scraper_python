#!/usr/bin/env python3
"""
LinkedIn Scraper Module
Uses requests and BeautifulSoup for static scraping (Streamlit Cloud compatible)
"""

import re
import time
import requests
from bs4 import BeautifulSoup

def scrape_linkedin_profile(url):
    """
    Scrape LinkedIn profile for contact information using requests (Streamlit Cloud compatible)

    Args:
        url (str): LinkedIn profile URL

    Returns:
        dict: Raw scraped data
    """
    print(f"Scraping LinkedIn profile: {url}")

    # Headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # Make the request
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check if we got a login page
        if 'login' in response.url or soup.find('form', {'action': re.compile(r'login')}):
            print("LinkedIn returned a login page. Static scraping has limitations.")
            print("For better results, consider using the linkedin-scraper library or manual data entry.")

        # Extract basic profile info
        profile_data = {
            'url': url,
            'name': extract_name(soup),
            'title': extract_title(soup),
            'company': extract_company(soup),
            'location': extract_location(soup),
            'about': extract_about(soup),
            'experience': extract_experience(soup),
            'education': extract_education(soup),
            'raw_html': str(soup)[:5000]  # First 5000 chars for debugging
        }

        return profile_data

    except requests.RequestException as e:
        print(f"Request error for LinkedIn: {e}")
        return {'error': f'Request failed: {str(e)}', 'url': url}
    except Exception as e:
        print(f"Error scraping LinkedIn: {e}")
        return {'error': str(e), 'url': url}

def extract_name(soup):
    """Extract name from LinkedIn profile"""
    try:
        name_elem = soup.find('h1', class_=re.compile(r'text-heading-xlarge'))
        if name_elem:
            return name_elem.get_text().strip()
        # Alternative selector
        name_elem = soup.find('h1')
        if name_elem:
            return name_elem.get_text().strip()
    except:
        pass
    return None

def extract_title(soup):
    """Extract current job title"""
    try:
        title_elem = soup.find('div', class_=re.compile(r'text-body-medium'))
        if title_elem:
            return title_elem.get_text().strip()
    except:
        pass
    return None

def extract_company(soup):
    """Extract current company"""
    try:
        # Look for company in experience section
        exp_section = soup.find('section', {'id': 'experience-section'})
        if exp_section:
            company_elem = exp_section.find('p', class_=re.compile(r'pv-entity__secondary-title'))
            if company_elem:
                return company_elem.get_text().strip()
    except:
        pass
    return None

def extract_location(soup):
    """Extract location"""
    try:
        loc_elem = soup.find('span', class_=re.compile(r'text-body-small.*geo-region'))
        if loc_elem:
            return loc_elem.get_text().strip()
    except:
        pass
    return None

def extract_about(soup):
    """Extract about section"""
    try:
        about_section = soup.find('section', {'id': 'about-section'})
        if about_section:
            about_elem = about_section.find('div', class_=re.compile(r'pv-about__summary-text'))
            if about_elem:
                return about_elem.get_text().strip()
    except:
        pass
    return None

def extract_experience(soup):
    """Extract experience information"""
    experiences = []
    try:
        exp_section = soup.find('section', {'id': 'experience-section'})
        if exp_section:
            exp_items = exp_section.find_all('div', class_=re.compile(r'pv-entity__summary-info'))
            for item in exp_items[:3]:  # Limit to first 3
                exp = {
                    'title': item.find('h3').get_text().strip() if item.find('h3') else None,
                    'company': item.find('p', class_=re.compile(r'pv-entity__secondary-title')).get_text().strip() if item.find('p', class_=re.compile(r'pv-entity__secondary-title')) else None,
                    'dates': item.find('span', class_=re.compile(r'pv-entity__date-range')).get_text().strip() if item.find('span', class_=re.compile(r'pv-entity__date-range')) else None
                }
                experiences.append(exp)
    except:
        pass
    return experiences

def extract_education(soup):
    """Extract education information"""
    education = []
    try:
        edu_section = soup.find('section', {'id': 'education-section'})
        if edu_section:
            edu_items = edu_section.find_all('div', class_=re.compile(r'pv-entity__summary-info'))
            for item in edu_items[:2]:  # Limit to first 2
                edu = {
                    'school': item.find('h3').get_text().strip() if item.find('h3') else None,
                    'degree': item.find('p', class_=re.compile(r'pv-entity__degree-name')).get_text().strip() if item.find('p', class_=re.compile(r'pv-entity__degree-name')) else None,
                    'dates': item.find('span', class_=re.compile(r'pv-entity__date-range')).get_text().strip() if item.find('span', class_=re.compile(r'pv-entity__date-range')) else None
                }
                education.append(edu)
    except:
        pass
    return education
