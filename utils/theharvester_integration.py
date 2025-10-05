#!/usr/bin/env python3
"""
theHarvester Integration Module
Integrates theHarvester tool for email and subdomain reconnaissance
"""

import subprocess
import json
import re
import os
import tempfile
from typing import Dict, List, Any, Optional

def run_theharvester(domain: str, sources: List[str] = None) -> Dict[str, Any]:
    """
    Run theHarvester against a domain to find emails and subdomains

    Args:
        domain (str): Domain to search
        sources (list): List of sources to use (default: all)

    Returns:
        dict: Results from theHarvester
    """
    if not sources:
        sources = ['all']  # Use all sources by default

    try:
        # Create temporary file for output
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            temp_filepath = temp_file.name

        # Build command
        cmd = [
            'theHarvester',
            '-d', domain,
            '-f', temp_filepath  # JSON output
        ]

        # Add sources
        for source in sources:
            if source != 'all':
                cmd.extend(['-b', source])

        print(f"Running theHarvester: {' '.join(cmd)}")

        # Run theHarvester
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            print(f"theHarvester error: {result.stderr}")
            return {'error': result.stderr, 'domain': domain}

        # Read results from temp file
        try:
            with open(temp_filepath, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading theHarvester output: {e}")
            data = {'error': str(e)}
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_filepath)
            except:
                pass

        # Process and return results
        return process_theharvester_results(data, domain)

    except subprocess.TimeoutExpired:
        return {'error': 'theHarvester timed out', 'domain': domain}
    except FileNotFoundError:
        return {'error': 'theHarvester not found. Please install it.', 'domain': domain}
    except Exception as e:
        return {'error': str(e), 'domain': domain}

def process_theharvester_results(data: Dict[str, Any], domain: str) -> Dict[str, Any]:
    """
    Process raw theHarvester results into our format

    Args:
        data (dict): Raw theHarvester JSON output
        domain (str): Domain that was searched

    Returns:
        dict: Processed results
    """
    results = {
        'domain': domain,
        'emails': [],
        'hosts': [],
        'ips': [],
        'metadata': {
            'tool': 'theHarvester',
            'domain': domain,
            'timestamp': data.get('time', 'unknown')
        }
    }

    # Extract emails
    if 'emails' in data:
        results['emails'] = list(set(data['emails']))  # Remove duplicates

    # Extract hosts/subdomains
    if 'hosts' in data:
        results['hosts'] = list(set(data['hosts']))

    # Extract IPs
    if 'ips' in data:
        results['ips'] = list(set(data['ips']))

    # Add source information
    if 'asns' in data:
        results['metadata']['asns'] = data['asns']

    return results

def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL for theHarvester

    Args:
        url (str): URL to extract domain from

    Returns:
        str or None: Domain name
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc

        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]

        return domain
    except:
        return None

def search_person_emails(name: str, domain: str = None) -> Dict[str, Any]:
    """
    Search for person-specific emails using theHarvester

    Args:
        name (str): Person name
        domain (str): Domain to search (optional)

    Returns:
        dict: Email search results
    """
    # This is a simplified implementation
    # theHarvester doesn't directly support name-based search
    # We would need to use different sources or combine with other tools

    if not domain:
        # Try to find likely domains from name
        # This is very basic - in practice, you'd use more sophisticated methods
        name_parts = name.lower().split()
        if len(name_parts) >= 2:
            # Create common email patterns
            first, last = name_parts[0], name_parts[-1]
            common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']

            results = {
                'name': name,
                'possible_emails': [],
                'metadata': {
                    'search_type': 'name_based',
                    'generated_patterns': True
                }
            }

            for domain in common_domains:
                results['possible_emails'].extend([
                    f"{first}.{last}@{domain}",
                    f"{first}{last}@{domain}",
                    f"{first[0]}{last}@{domain}",
                    f"{first}_{last}@{domain}"
                ])

            return results

    return {'error': 'Domain required for name-based search', 'name': name}

def combine_results(scraper_results: Dict[str, Any], harvester_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combine scraper results with theHarvester results

    Args:
        scraper_results (dict): Results from web scraper
        harvester_results (dict): Results from theHarvester

    Returns:
        dict: Combined results
    """
    combined = scraper_results.copy()

    # Add theHarvester emails if not already found
    harvester_emails = harvester_results.get('emails', [])
    existing_emails = set(combined.get('emails', []))

    new_emails = [email for email in harvester_emails if email not in existing_emails]
    combined['emails'].extend(new_emails)

    # Add metadata
    if 'metadata' not in combined:
        combined['metadata'] = {}

    combined['metadata']['theharvester_used'] = True
    combined['metadata']['theharvester_domain'] = harvester_results.get('domain')
    combined['metadata']['additional_emails_from_harvester'] = len(new_emails)

    return combined

# Example usage and testing
if __name__ == "__main__":
    # Test theHarvester integration
    test_domain = "example.com"
    results = run_theharvester(test_domain)
    print(json.dumps(results, indent=2))
