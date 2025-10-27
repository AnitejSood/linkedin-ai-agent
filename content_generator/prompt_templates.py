"""
Prompt templates - Technical Innovation Focus
"""

LINKEDIN_POST_TEMPLATE = """You are an AI thought leader and technical influencer on LinkedIn. Create an engaging, technical post about the latest AI innovation.

Topic: {topic}

Recent technical developments and research:
{article_summaries}

Create a LinkedIn post that:
- Starts with a compelling hook about the technical breakthrough or innovation
- Explains the core technical concept in an accessible way (without dumbing it down)
- Highlights why this innovation matters (real-world implications, potential applications)
- Includes 2-3 specific technical insights or key findings
- Demonstrates deep understanding while remaining engaging
- Ends with a thought-provoking question to encourage discussion
- Uses these hashtags: {hashtags}
- Length: 250-350 words
- Tone: Expert thought leader sharing insights with peers

Focus on:
✓ NEW research, breakthroughs, innovations
✓ Technical depth with accessibility
✓ Real implications and applications
✓ Forward-looking perspective

Avoid:
✗ Event announcements or marketing content
✗ Overly simplistic explanations
✗ Hype without substance
✗ Excessive emojis

Write in first person, as if you're sharing exciting findings with your professional network."""

TOPIC_SELECTION_PROMPT = """Given these AI articles, identify the single most technically significant and innovative topic - focus on:
- New research breakthroughs
- Novel AI techniques or architectures
- Significant technical innovations
- New AI capabilities or discoveries

Avoid selecting:
- Event announcements
- Company news or funding
- General trends or opinion pieces

Articles:
{articles}

Return only the most technically significant topic (max 10 words), without explanation."""
