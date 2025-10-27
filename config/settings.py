"""
Configuration settings - Working Technical AI Sources
"""

# Technical AI sources with VERIFIED RSS feeds
NEWS_SOURCES = [
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        "type": "rss"
    },
    {
        "name": "DeepMind Blog",
        "url": "https://deepmind.google/blog/rss.xml",
        "type": "rss"
    },
    {
        "name": "NVIDIA AI Blog",
        "url": "https://blogs.nvidia.com/blog/category/deep-learning/feed/",
        "type": "rss"
    },
    {
        "name": "Microsoft AI Blog",
        "url": "https://blogs.microsoft.com/ai/feed/",
        "type": "rss"
    },
    {
        "name": "MarkTechPost AI",
        "url": "https://www.marktechpost.com/feed/",
        "type": "rss"
    },
    {
        "name": "AI News",
        "url": "https://www.artificialintelligence-news.com/feed/",
        "type": "rss"
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "type": "rss"
    },
    {
        "name": "Papers With Code",
        "url": "https://paperswithcode.com/newsletter/rss/",
        "type": "rss"
    }
]

# Post generation settings
MAX_POST_LENGTH = 3000
MIN_POST_LENGTH = 250
NUM_SOURCES = 4
HASHTAGS = ["#AI", "#MachineLearning", "#ArtificialIntelligence", "#AIResearch", "#Innovation", "#TechBreakthrough"]

# Excel settings
EXCEL_PATH = "data/posts_tracker.xlsx"
EXCEL_COLUMNS = ["date", "topic", "post_content", "sources", "posted", "posted_date", "image_path"]

# Scraping settings
SCRAPE_TIMEOUT = 30
MAX_ARTICLES_PER_SOURCE = 10

# Gemini settings
# Gemini settings
GEMINI_MODEL = "gemini-2.0-flash-exp"
GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"  # Add this
GEMINI_TEMPERATURE = 0.7

