"""
Gemini API Client for content generation
"""

import os
from google import genai
from utils.logger import setup_logger

logger = setup_logger()

class GeminiClient:
    """Wrapper for Gemini API interactions"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("Please set GEMINI_API_KEY in .env file")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"
        logger.info("Gemini client initialized")
    
    def generate_content(self, prompt: str) -> str:
        """
        Generate content using Gemini
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            Generated text content
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return ""
    
    def generate_post(self, topic: str, articles: list, template: str) -> str:
        """
        Generate LinkedIn post using Gemini
        
        Args:
            topic: Selected topic
            articles: List of relevant articles
            template: Prompt template
            
        Returns:
            Generated LinkedIn post content
        """
        # Format articles for context
        article_summaries = "\n".join([
            f"- {art.get('title', '')}: {art.get('summary', '')[:200]}"
            for art in articles[:5]
        ])
        
        # Create prompt
        prompt = template.format(
            topic=topic,
            article_summaries=article_summaries,
            hashtags=" ".join(["#AI", "#MachineLearning", "#TechNews"])
        )
        
        return self.generate_content(prompt)
