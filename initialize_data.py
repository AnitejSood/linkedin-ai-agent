"""
Initialize data files for the LinkedIn AI Agent
Run this script once: python initialize_data.py
"""

import pandas as pd
import json
import os
from config.settings import EXCEL_PATH, EXCEL_COLUMNS

def initialize_excel_tracker():
    """Create the Excel file for tracking posts"""
    print("\nInitializing Excel tracker...")
    
    df = pd.DataFrame(columns=EXCEL_COLUMNS)
    os.makedirs(os.path.dirname(EXCEL_PATH), exist_ok=True)
    df.to_excel(EXCEL_PATH, index=False)
    
    print(f"  ✓ Excel tracker created: {EXCEL_PATH}")

def initialize_json_storage():
    """Create initial JSON storage files"""
    print("\nInitializing JSON storage...")
    
    # scraped_data.json
    scraped_data = {
        "last_updated": None,
        "articles": []
    }
    with open("data/scraped_data.json", 'w') as f:
        json.dump(scraped_data, f, indent=2)
    print("  ✓ Created: data/scraped_data.json")
    
    # sources.json
    sources_data = {
        "credible_domains": [
            "techcrunch.com",
            "venturebeat.com",
            "arxiv.org",
            "technologyreview.com",
            "nature.com",
            "openai.com",
            "deepmind.com",
            "ai.google",
            "research.google",
            "blog.google",
            "theverge.com",
            "wired.com"
        ]
    }
    with open("data/sources.json", 'w') as f:
        json.dump(sources_data, f, indent=2)
    print("  ✓ Created: data/sources.json")

if __name__ == "__main__":
    print("="*70)
    print("LinkedIn AI Agent - Data Initialization")
    print("="*70)
    
    initialize_excel_tracker()
    initialize_json_storage()
    
    print("\n" + "="*70)
    print("✓ Data initialization complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Edit .env file and add your GEMINI_API_KEY")
    print("2. Run: python main.py")
    print("="*70)
