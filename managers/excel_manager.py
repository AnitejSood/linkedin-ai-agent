"""
Excel Manager - Handles all Excel operations - FIXED
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from utils.logger import setup_logger

logger = setup_logger()

class ExcelManager:
    """Manages Excel file operations for post tracking"""
    
    def __init__(self, excel_path: str):
        """Initialize with Excel file path"""
        self.excel_path = excel_path
        logger.info(f"Excel manager initialized: {excel_path}")
    
    def add_post(self, topic: str, content: str, sources: List[Dict], image_path: Optional[str] = None):
        """Add a new post to the Excel tracker"""
        try:
            # Read existing data
            try:
                df = pd.read_excel(self.excel_path)
            except FileNotFoundError:
                # If file doesn't exist, create empty DataFrame
                df = pd.DataFrame(columns=["date", "topic", "post_content", "sources", "posted", "posted_date", "image_path"])
            
            # Create new row
            new_row = {
                "date": datetime.now(),
                "topic": topic,
                "post_content": content,
                "sources": str(sources),
                "posted": False,
                "posted_date": None,
                "image_path": image_path if image_path else ""
            }
            
            # Add new row
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save to Excel
            df.to_excel(self.excel_path, index=False)
            
            logger.info(f"✓ Added post to tracker: {topic[:50]}...")
            
        except Exception as e:
            logger.error(f"Error adding post to Excel: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def mark_as_posted(self, topic: str):
        """Mark a post as published on LinkedIn"""
        try:
            df = pd.read_excel(self.excel_path)
            mask = df['topic'] == topic
            df.loc[mask, 'posted'] = True
            df.loc[mask, 'posted_date'] = datetime.now()
            df.to_excel(self.excel_path, index=False)
            logger.info(f"✓ Marked as posted: {topic}")
        except Exception as e:
            logger.error(f"Error updating Excel: {e}")
    
    def get_all_posts(self) -> pd.DataFrame:
        """Get all posts from Excel"""
        try:
            return pd.read_excel(self.excel_path)
        except FileNotFoundError:
            logger.warning("Excel file not found, returning empty DataFrame")
            return pd.DataFrame(columns=["date", "topic", "post_content", "sources", "posted", "posted_date", "image_path"])
        except Exception as e:
            logger.error(f"Error reading Excel: {e}")
            return pd.DataFrame()
