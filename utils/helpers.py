"""
Helper utility functions
"""

import json
from datetime import datetime
from typing import Dict
from urllib.parse import urlparse

def save_json(data: Dict, filepath: str):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(filepath: str) -> Dict:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def format_timestamp(dt=None) -> str:
    """Format datetime to string"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    return ' '.join(text.split()).strip()

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    return urlparse(url).netloc
