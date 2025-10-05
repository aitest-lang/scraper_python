#!/usr/bin/env python3
"""
Storage Module
Handles JSON file operations for saving and loading reconnaissance data
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

def save_to_json(data: Dict[str, Any], filepath: str) -> bool:
    """
    Save data to JSON file

    Args:
        data (dict): Data to save
        filepath (str): Path to JSON file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Add timestamp if not present
        if 'metadata' in data and 'extraction_timestamp' not in data['metadata']:
            data['metadata']['extraction_timestamp'] = datetime.now().isoformat()

        # Save with pretty printing
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Data saved to {filepath}")
        return True

    except Exception as e:
        print(f"Error saving to {filepath}: {e}")
        return False

def load_from_json(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load data from JSON file

    Args:
        filepath (str): Path to JSON file

    Returns:
        dict or None: Loaded data or None if error
    """
    try:
        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    except Exception as e:
        print(f"Error loading from {filepath}: {e}")
        return None

def append_to_json(new_data: Dict[str, Any], filepath: str) -> bool:
    """
    Append new data to existing JSON file or create new one

    Args:
        new_data (dict): New data to append
        filepath (str): Path to JSON file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load existing data
        existing_data = load_from_json(filepath) or {'results': []}

        # Ensure it's a list structure
        if not isinstance(existing_data, dict):
            existing_data = {'results': [existing_data]}

        if 'results' not in existing_data:
            existing_data = {'results': [existing_data]}

        # Add timestamp to new data
        if 'metadata' not in new_data:
            new_data['metadata'] = {}
        new_data['metadata']['saved_timestamp'] = datetime.now().isoformat()

        # Append new result
        existing_data['results'].append(new_data)

        # Save updated data
        return save_to_json(existing_data, filepath)

    except Exception as e:
        print(f"Error appending to {filepath}: {e}")
        return False

def export_to_csv(data: Dict[str, Any], csv_filepath: str) -> bool:
    """
    Export contacts data to CSV format

    Args:
        data (dict): Contact data
        csv_filepath (str): Path to CSV file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import csv

        # Ensure directory exists
        os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)

        with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(['Type', 'Value', 'Source_URL', 'Name', 'Title', 'Company', 'Location'])

            # Write emails
            metadata = data.get('metadata', {})
            for email in data.get('emails', []):
                writer.writerow([
                    'Email',
                    email,
                    metadata.get('source_url', ''),
                    metadata.get('name', ''),
                    metadata.get('title', ''),
                    metadata.get('company', ''),
                    metadata.get('location', '')
                ])

            # Write phones
            for phone in data.get('phones', []):
                writer.writerow([
                    'Phone',
                    phone,
                    metadata.get('source_url', ''),
                    metadata.get('name', ''),
                    metadata.get('title', ''),
                    metadata.get('company', ''),
                    metadata.get('location', '')
                ])

        print(f"Data exported to CSV: {csv_filepath}")
        return True

    except Exception as e:
        print(f"Error exporting to CSV {csv_filepath}: {e}")
        return False

def get_file_info(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a saved JSON file

    Args:
        filepath (str): Path to JSON file

    Returns:
        dict or None: File information
    """
    try:
        if not os.path.exists(filepath):
            return None

        stat = os.stat(filepath)

        data = load_from_json(filepath)
        if not data:
            return None

        # Handle both single result and multiple results format
        if 'results' in data:
            result_count = len(data['results'])
            latest_result = data['results'][-1] if data['results'] else {}
        else:
            result_count = 1
            latest_result = data

        return {
            'filepath': filepath,
            'size_bytes': stat.st_size,
            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'result_count': result_count,
            'latest_emails': len(latest_result.get('emails', [])),
            'latest_phones': len(latest_result.get('phones', [])),
            'latest_source': latest_result.get('metadata', {}).get('source_url')
        }

    except Exception as e:
        print(f"Error getting file info for {filepath}: {e}")
        return None
