#!/usr/bin/env python3
"""
Data Extraction Module
Extracts emails and phone numbers from scraped data using regex and validation
"""

import re
import json
from typing import Dict, List, Any

# Email regex patterns
EMAIL_PATTERNS = [
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    r'\b[A-Za-z0-9._%+-]+\[at\][A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # [at] obfuscation
    r'\b[A-Za-z0-9._%+-]+\(at\)[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # (at) obfuscation
]

# Phone regex patterns (international formats)
PHONE_PATTERNS = [
    r'\+\d{1,3}[\s\-\.]?\(?\d{1,4}\)?[\s\-\.]?\d{1,4}[\s\-\.]?\d{1,4}[\s\-\.]?\d{0,4}',
    r'\(\d{3}\)\s*\d{3}[\s\-]?\d{4}',  # US format (123) 456-7890
    r'\d{3}[\s\-]\d{3}[\s\-]\d{4}',    # US format 123-456-7890
    r'\d{10,15}',                      # Plain numbers
]

def extract_contacts(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract emails and phone numbers from raw scraped data

    Args:
        raw_data (dict): Raw data from scraper

    Returns:
        dict: Extracted and validated contacts
    """
    if not raw_data or 'error' in raw_data:
        return {
            'emails': [],
            'phones': [],
            'metadata': {'error': raw_data.get('error', 'No data')}
        }

    # Combine all text data for extraction
    text_content = extract_text_content(raw_data)

    # Extract emails
    emails = extract_emails(text_content)
    validated_emails = validate_emails(emails)

    # Extract phones
    phones = extract_phones(text_content)
    validated_phones = validate_phones(phones)

    # Create result
    result = {
        'emails': validated_emails,
        'phones': validated_phones,
        'metadata': {
            'source_url': raw_data.get('url'),
            'name': raw_data.get('name'),
            'title': raw_data.get('title'),
            'company': raw_data.get('company'),
            'location': raw_data.get('location'),
            'extraction_timestamp': raw_data.get('timestamp'),
            'total_emails_found': len(emails),
            'total_phones_found': len(phones),
            'validated_emails': len(validated_emails),
            'validated_phones': len(validated_phones)
        }
    }

    return result

def extract_text_content(raw_data: Dict[str, Any]) -> str:
    """
    Extract all text content from raw data for pattern matching

    Args:
        raw_data (dict): Raw scraped data

    Returns:
        str: Combined text content
    """
    text_parts = []

    # Add structured data
    if raw_data.get('name'):
        text_parts.append(raw_data['name'])
    if raw_data.get('title'):
        text_parts.append(raw_data['title'])
    if raw_data.get('company'):
        text_parts.append(raw_data['company'])
    if raw_data.get('location'):
        text_parts.append(raw_data['location'])
    if raw_data.get('about'):
        text_parts.append(raw_data['about'])

    # Add experience
    if raw_data.get('experience'):
        for exp in raw_data['experience']:
            text_parts.extend(exp.values())

    # Add education
    if raw_data.get('education'):
        for edu in raw_data['education']:
            text_parts.extend(edu.values())

    # Add raw HTML as fallback
    if raw_data.get('raw_html'):
        text_parts.append(raw_data['raw_html'])

    return ' '.join(str(part) for part in text_parts if part)

def extract_emails(text: str) -> List[str]:
    """
    Extract email addresses from text using regex patterns

    Args:
        text (str): Text to search

    Returns:
        list: List of found email addresses
    """
    emails = set()  # Use set to avoid duplicates

    for pattern in EMAIL_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean up obfuscated emails
            clean_email = match.replace('[at]', '@').replace('(at)', '@')
            emails.add(clean_email.lower())

    return list(emails)

def extract_phones(text: str) -> List[str]:
    """
    Extract phone numbers from text using regex patterns

    Args:
        text (str): Text to search

    Returns:
        list: List of found phone numbers
    """
    phones = set()  # Use set to avoid duplicates

    for pattern in PHONE_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean up formatting
            clean_phone = re.sub(r'[\s\-\(\)\.]', '', match)
            if len(clean_phone) >= 10:  # Minimum length check
                phones.add(clean_phone)

    return list(phones)

def validate_emails(emails: List[str]) -> List[str]:
    """
    Validate email addresses using python-email-validator

    Args:
        emails (list): List of email addresses

    Returns:
        list: List of validated email addresses
    """
    validated = []

    try:
        from email_validator import validate_email, EmailNotValidError

        for email in emails:
            try:
                # Validate and normalize
                valid = validate_email(email, check_deliverability=False)
                validated.append(valid.email)
            except EmailNotValidError:
                continue  # Skip invalid emails

    except ImportError:
        # Fallback if library not available
        print("email-validator not available, using basic validation")
        validated = [email for email in emails if basic_email_check(email)]

    return validated

def validate_phones(phones: List[str]) -> List[str]:
    """
    Validate phone numbers using phonenumbers library

    Args:
        phones (list): List of phone numbers

    Returns:
        list: List of validated and formatted phone numbers
    """
    validated = []

    try:
        import phonenumbers

        for phone in phones:
            try:
                # Try to parse as international number
                parsed = phonenumbers.parse(phone, None)
                if phonenumbers.is_valid_number(parsed):
                    # Format in international format
                    formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    validated.append(formatted)
            except:
                continue

    except ImportError:
        # Fallback if library not available
        print("phonenumbers library not available, using basic validation")
        validated = [phone for phone in phones if basic_phone_check(phone)]

    return validated

def basic_email_check(email: str) -> bool:
    """
    Basic email validation fallback

    Args:
        email (str): Email to check

    Returns:
        bool: True if basic checks pass
    """
    if not email or '@' not in email:
        return False

    local, domain = email.split('@', 1)
    if not local or not domain or '.' not in domain:
        return False

    return len(local) > 0 and len(domain) > 2

def basic_phone_check(phone: str) -> bool:
    """
    Basic phone validation fallback

    Args:
        phone (str): Phone to check

    Returns:
        bool: True if basic checks pass
    """
    if not phone:
        return False

    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)

    # Check length (10-15 digits for international)
    return 10 <= len(digits) <= 15
