"""
LinkedIn AI Agent - Complete with Technical Focus and Nano Banana
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

from config.settings import NEWS_SOURCES, EXCEL_PATH
from scrapers.rss_scraper import RSSFeedScraper
from content_generator.gemini_client import GeminiClient
from content_generator.nano_banana_client import NanoBananaClient
from content_generator.prompt_templates import LINKEDIN_POST_TEMPLATE, TOPIC_SELECTION_PROMPT
from managers.topic_manager import TopicManager
from managers.excel_manager import ExcelManager
from managers.source_validator import SourceValidator
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger()

def main():
    """Main execution function"""
    logger.info("="*70)
    logger.info("LinkedIn AI Agent - Technical Innovation Mode")
    logger.info("="*70)
    
    try:
        # Step 1: Scrape articles from technical sources
        logger.info("\nStep 1: Scraping technical AI sources...")
        all_articles = []
        
        for source in NEWS_SOURCES:
            scraper = RSSFeedScraper(source['name'], source['url'])
            articles = scraper.scrape()
            all_articles.extend(articles)
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        
        if not all_articles:
            logger.error("No articles found! Check your internet connection.")
            return
        
        # FIXED: Save raw data (OVERWRITE, don't append)
        scraped_data = {
            "last_updated": datetime.now().isoformat(),
            "articles": all_articles,  # Fresh data only
            "total_articles": len(all_articles),
            "sources_count": len(set(article.get('source') for article in all_articles))
        }
        
        with open("data/scraped_data.json", "w", encoding='utf-8') as f:  # 'w' not 'a'
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved {len(all_articles)} fresh articles to JSON")

        # Step 2: LLM-powered topic selection
        logger.info("\nStep 2: LLM-powered topic selection...")
        topic_manager = TopicManager(EXCEL_PATH)  # This will use the new LLM scoring system

        # Use the new method name (or keep select_new_topic for compatibility)
        selected_topic, relevant_articles = topic_manager.select_best_topic(all_articles)

        if not selected_topic:
            logger.error("Could not select a suitable topic!")
            return

        logger.info(f"✓ Selected topic: {selected_topic}")

        
        # Step 3: Generate technical LinkedIn post
        logger.info("\nStep 3: Generating technical LinkedIn post...")
        gemini = GeminiClient()
        post_content = gemini.generate_post(
            selected_topic, 
            relevant_articles, 
            LINKEDIN_POST_TEMPLATE
        )
        
        if not post_content:
            logger.error("Failed to generate post content!")
            return
        
        logger.info(f"✓ Post generated ({len(post_content)} characters)")
        
        # Step 4: Extract credible sources
        logger.info("\nStep 4: Extracting credible sources...")
        validator = SourceValidator()
        sources = validator.extract_sources(relevant_articles, num_sources=4)
        
        # Step 5: Generate optimized image prompt with Gemini 2.0
        logger.info("\nStep 5: Creating AI-optimized image prompt...")
        nano_banana = NanoBananaClient()
        image_prompt = nano_banana.generate_image_prompt(selected_topic, post_content)
        
        # Step 6: Generate image with Nano Banana
        logger.info("\nStep 6: Generating LinkedIn image with Nano Banana...")
        image_data = nano_banana.generate_linkedin_image(image_prompt)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filepath = None
        
        if image_data:
            image_filepath = f"outputs/ready_posts/post_{timestamp}.png"
            nano_banana.save_image(image_data, image_filepath)
        else:
            logger.warning("Could not generate image, proceeding without it")
        
        # Step 7: Save to Excel (FIXED - include image path)
        logger.info("\nStep 7: Saving to Excel tracker...")
        excel_manager = ExcelManager(EXCEL_PATH)
        excel_manager.add_post(selected_topic, post_content, sources, image_filepath)

        
        # Step 8: Create comprehensive output file
        logger.info("\nStep 8: Creating output file...")
        output_file = f"outputs/ready_posts/post_{timestamp}.txt"
        
        with open(output_file, "w", encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("LINKEDIN POST - TECHNICAL AI INNOVATION\n")
            f.write("="*70 + "\n\n")
            f.write(f"TOPIC: {selected_topic}\n\n")
            
            f.write("-"*70 + "\n")
            f.write("POST CONTENT:\n")
            f.write("-"*70 + "\n")
            f.write(post_content + "\n\n")
            
            if image_filepath:
                f.write("-"*70 + "\n")
                f.write("GENERATED IMAGE:\n")
                f.write("-"*70 + "\n")
                f.write(f"Image file: {image_filepath}\n")
                f.write(f"Image prompt used: {image_prompt}\n\n")
            
            f.write("-"*70 + "\n")
            f.write("SOURCES FOR VERIFICATION:\n")
            f.write("-"*70 + "\n")
            for i, source in enumerate(sources, 1):
                f.write(f"{i}. {source['title']}\n")
                f.write(f"   {source['url']}\n\n")
            
            f.write("="*70 + "\n")
            f.write("NEXT STEPS:\n")
            f.write("1. Review the technical post content\n")
            f.write("2. Check the AI-generated image\n")
            f.write("3. Verify all sources are accurate\n")
            f.write("4. Post to LinkedIn with image\n")
            f.write("5. Update Excel with posted=True\n")
            f.write("="*70 + "\n")
        
        logger.info("\n" + "="*70)
        logger.info("✓ SUCCESS! Technical post ready:")
        logger.info(f"  Text: {output_file}")
        if image_filepath:
            logger.info(f"  Image: {image_filepath}")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"\nError in main execution: {e}", exc_info=True)

if __name__ == "__main__":
    main()
