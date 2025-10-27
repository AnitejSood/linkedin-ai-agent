"""
Smart Topic Manager - Dual LLM Approach (Scoring + Selection)
"""

import pandas as pd
from typing import List, Dict, Tuple
from content_generator.gemini_client import GeminiClient
from utils.logger import setup_logger
import json
import re

logger = setup_logger()

class LLMScoringTopicManager:
    """Topic selection using LLM scoring + LLM final selection"""
    
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.gemini_client = GeminiClient()
    
    def select_best_topic(self, articles: List[Dict]) -> Tuple[str, List[Dict]]:
        """Main method: LLM scoring → Top 10 → LLM final selection"""
        
        logger.info(f"Starting LLM-powered topic selection from {len(articles)} articles...")
        
        # Step 1: Filter out already posted topics
        available_articles = self._filter_posted_topics(articles)
        logger.info(f"After duplicate filtering: {len(available_articles)} unique articles")
        
        if not available_articles:
            return "", []
        
        # Step 2: LLM scores ALL articles in one call
        scored_articles = self._llm_score_all_articles(available_articles)
        logger.info(f"LLM scored {len(scored_articles)} articles")
        
        if not scored_articles:
            return "", []
        
        # Step 3: Select top 10 based on LLM scores
        top_candidates = self._select_top_candidates(scored_articles, top_n=10)
        logger.info(f"Selected top {len(top_candidates)} candidates for final LLM selection")
        
        # Step 4: LLM selects best from top 10
        selected_topic, relevant_articles = self._llm_final_selection(top_candidates)
        
        return selected_topic, relevant_articles
    
    def _filter_posted_topics(self, articles: List[Dict]) -> List[Dict]:
        """Filter out previously posted topics"""
        try:
            df = pd.read_excel(self.excel_path)
            posted_topics = df['topic'].tolist() if not df.empty else []
            logger.info(f"Found {len(posted_topics)} previously posted topics")
        except FileNotFoundError:
            posted_topics = []
            logger.info("No previous posts found")
        
        available_articles = []
        for article in articles:
            title = article.get('title', '').strip()
            if not title:
                continue
            
            # Check for similarity with posted topics
            is_duplicate = any(
                self._calculate_similarity(title, posted_title) > 0.7 
                for posted_title in posted_topics
            )
            
            if not is_duplicate:
                available_articles.append(article)
        
        return available_articles
    
    def _calculate_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles"""
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _llm_score_all_articles(self, articles: List[Dict]) -> List[Tuple[float, Dict]]:
        """Send ALL articles to LLM for scoring in one API call"""
        
        try:
            # Format all articles for LLM scoring
            article_list = []
            for i, article in enumerate(articles, 1):
                title = article.get('title', 'Untitled')
                summary = article.get('summary', '')[:100]  # Truncate to save tokens
                source = article.get('source', 'Unknown')
                
                article_list.append(f"{i}. **{title}**")
                if summary:
                    article_list.append(f"   Summary: {summary}...")
                article_list.append(f"   Source: {source}")
                article_list.append("")  # Empty line for readability
            
            # Create comprehensive scoring prompt
            scoring_prompt = f"""You are a LinkedIn content strategist and AI expert. Score each of these {len(articles)} AI articles for LinkedIn engagement potential.

ARTICLES TO SCORE:
{chr(10).join(article_list)}

SCORING CRITERIA (0-10 scale):
🎯 **Business Impact** (25%): Will executives, CTOs, VPs care about this?
💬 **Discussion Potential** (25%): Will this spark meaningful comments and debates?
📈 **Viral/Share Potential** (20%): Surprising, breakthrough, or counterintuitive findings?
🔥 **Timeliness** (15%): Is this trending, newsworthy, or time-sensitive?
👥 **Professional Value** (15%): Does this help careers, skills, or business strategy?

SCORING GUIDELINES:
- **9-10**: Breakthrough news, game-changing developments, viral potential
- **7-8**: Strong business relevance, high engagement expected
- **5-6**: Solid professional content, moderate engagement
- **3-4**: Niche or technical, limited broad appeal
- **1-2**: Low engagement, too academic or narrow

RESPONSE FORMAT (CRITICAL - Follow exactly):
1: [Score] - [Brief reason]
2: [Score] - [Brief reason]
3: [Score] - [Brief reason]
...continue for all {len(articles)} articles

Example:
1: 8.5 - Breakthrough AI achievement with huge business impact
2: 6.0 - Solid technical content but limited viral potential
3: 9.0 - Major company announcement, high discussion value

Score each article (1-{len(articles)}):"""

            # Get LLM scores
            logger.info(f"Requesting LLM scores for {len(articles)} articles...")
            response = self.gemini_client.generate_content(scoring_prompt)
            
            if not response:
                logger.error("No response from LLM scoring")
                return []
            
            # Parse scores from LLM response
            scored_articles = self._parse_llm_scores(response, articles)
            
            # Log top scored articles
            if scored_articles:
                logger.info("🏆 Top LLM-scored articles:")
                for i, (score, article) in enumerate(scored_articles[:5], 1):
                    title = article.get('title', 'Untitled')[:50]
                    logger.info(f"  {i}. {title}... (LLM Score: {score}/10)")
            
            return scored_articles
            
        except Exception as e:
            logger.error(f"Error in LLM scoring: {e}")
            return []
    
    def _parse_llm_scores(self, response: str, articles: List[Dict]) -> List[Tuple[float, Dict]]:
        """Parse LLM response to extract scores for each article"""
        
        scored_articles = []
        
        try:
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for pattern: "1: 8.5 - reason" or "1. 8.5 - reason"
                match = re.match(r'^(\d+)[\:\.]?\s*(\d+(?:\.\d+)?)\s*[-–—]\s*(.+)$', line)
                
                if match:
                    article_num = int(match.group(1))
                    score = float(match.group(2))
                    reason = match.group(3)
                    
                    # Validate article number and score
                    if 1 <= article_num <= len(articles) and 0 <= score <= 10:
                        article_index = article_num - 1
                        article = articles[article_index]
                        
                        # Add reason to article for logging
                        article_with_reason = article.copy()
                        article_with_reason['llm_reason'] = reason
                        
                        scored_articles.append((score, article_with_reason))
            
            # Sort by score (highest first)
            scored_articles.sort(key=lambda x: x[0], reverse=True)
            
            logger.info(f"✅ Successfully parsed {len(scored_articles)} LLM scores")
            
            return scored_articles
            
        except Exception as e:
            logger.error(f"Error parsing LLM scores: {e}")
            return []
    
    def _select_top_candidates(self, scored_articles: List[Tuple[float, Dict]], top_n: int = 10) -> List[Dict]:
        """Select top N articles based on LLM scores"""
        
        top_candidates = []
        
        for i, (score, article) in enumerate(scored_articles[:top_n]):
            article_with_score = article.copy()
            article_with_score['llm_score'] = score
            top_candidates.append(article_with_score)
            
            # Log candidate info
            title = article.get('title', 'Untitled')[:60]
            reason = article.get('llm_reason', 'No reason provided')
            logger.info(f"  Candidate {i+1}: {title}... (Score: {score}/10)")
            logger.info(f"    Reason: {reason}")
        
        return top_candidates
    
    def _llm_final_selection(self, candidates: List[Dict]) -> Tuple[str, List[Dict]]:
        """LLM selects the single best topic from top candidates"""
        
        if not candidates:
            return "", []
        
        try:
            # Format top candidates for final selection
            candidate_summaries = []
            for i, article in enumerate(candidates, 1):
                title = article.get('title', 'Untitled')
                summary = article.get('summary', '')[:150]
                source = article.get('source', 'Unknown')
                score = article.get('llm_score', 0)
                reason = article.get('llm_reason', 'No reason')
                
                candidate_summaries.append(
                    f"{i}. **{title}** (LLM Score: {score}/10)\n"
                    f"   Source: {source}\n"
                    f"   Why it scored high: {reason}\n"
                    f"   Summary: {summary}...\n"
                )
            
            # Create focused final selection prompt
            final_prompt = f"""You are a LinkedIn content strategist making the FINAL decision. These are the top {len(candidates)} AI articles (already pre-scored by LLM for engagement potential).

TOP CANDIDATES:
{chr(10).join(candidate_summaries)}

FINAL SELECTION CRITERIA:
🏆 **Maximum LinkedIn Impact**: Which will get the most shares, comments, saves?
💼 **Executive Appeal**: What would a CEO, CTO, or VP want to discuss?
🔥 **Right-Now Relevance**: What's trending and timely TODAY?
💡 **Thought Leadership**: What positions you as an AI expert and innovator?
🎯 **Broad Professional Appeal**: Valuable to both tech and business professionals?

INSTRUCTIONS:
- Choose EXACTLY ONE number (1-{len(candidates)})
- This will be your LinkedIn post topic for today
- Consider: Would YOU personally share this with your network?
- Think: What would drive the most valuable professional discussions?

RESPONSE FORMAT:
Selected: [NUMBER]
Final Reason: [One compelling sentence why THIS topic beats all others for LinkedIn success]

Your final choice:"""

            # Get LLM final decision
            logger.info("🎯 Requesting final LLM selection from top candidates...")
            response = self.gemini_client.generate_content(final_prompt)
            
            # Parse final selection
            selected_index = self._parse_final_selection(response, len(candidates))
            
            if selected_index is not None:
                selected_article = candidates[selected_index]
                selected_topic = selected_article.get('title', '')
                score = selected_article.get('llm_score', 0)
                
                logger.info(f"🏆 FINAL SELECTION: {selected_topic[:60]}...")
                logger.info(f"   LLM Score: {score}/10")
                logger.info(f"   Source: {selected_article.get('source', 'Unknown')}")
                
                return selected_topic, [selected_article]
            
            else:
                logger.warning("Could not parse final selection, using top scored article")
                top_article = candidates[0]
                return top_article.get('title', ''), [top_article]
        
        except Exception as e:
            logger.error(f"Final LLM selection failed: {e}")
            if candidates:
                return candidates[0].get('title', ''), [candidates[0]]
            return "", []
    
    def _parse_final_selection(self, response: str, max_candidates: int) -> int:
        """Parse final LLM selection response"""
        try:
            # Look for "Selected: X" pattern
            selected_match = re.search(r'selected:\s*(\d+)', response.lower())
            if selected_match:
                num = int(selected_match.group(1))
                if 1 <= num <= max_candidates:
                    return num - 1  # Convert to 0-based
            
            # Fallback: find any number in response
            numbers = re.findall(r'\b(\d+)\b', response)
            for num_str in numbers:
                num = int(num_str)
                if 1 <= num <= max_candidates:
                    return num - 1
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing final selection: {e}")
            return None

# Keep the old class name for backwards compatibility
class TopicManager(LLMScoringTopicManager):
    """Backwards compatibility alias"""
    
    def select_new_topic(self, articles: List[Dict]) -> Tuple[str, List[Dict]]:
        """Backwards compatible method name"""
        return self.select_best_topic(articles)
