#!/usr/bin/env python3
"""
LinkedIn Scraper Module
Uses linkedin_scraper library for extracting profile data
"""

import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scrape_linkedin_profile(url):
    """
    Scrape LinkedIn profile for contact information

    Args:
        url (str): LinkedIn profile URL

    Returns:
        dict: Raw scraped data
    """
    print(f"Scraping LinkedIn profile: {url}")

    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        driver.get(url)
        time.sleep(3)  # Wait for page to load

        # Try to handle login wall
        try:
            # Check if login is required
            login_button = driver.find_element(By.XPATH, "//a[contains(@href, 'login')]")
            print("LinkedIn requires login. This scraper works best with logged-in sessions.")
            print("For better results, consider using linkedin_scraper library with credentials.")
        except NoSuchElementException:
            pass

        # Wait for profile content to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pv-top-card"))
            )
        except TimeoutException:
            print("Profile content may not have loaded properly")

        # Get page source
        page_source = driver.page_source

        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

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
            'raw_html': page_source[:5000]  # First 5000 chars for debugging
        }

        driver.quit()
        return profile_data

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
