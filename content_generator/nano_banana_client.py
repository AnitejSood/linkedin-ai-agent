"""
Nano Banana (Gemini 2.5 Flash Image) Client - FIXED INDENTATION
"""

import os
import base64
import io
from PIL import Image
from google import genai
from google.genai import types
from utils.logger import setup_logger

logger = setup_logger()

class NanoBananaClient:
    """Wrapper for Nano Banana (Gemini 2.5 Flash Image) API"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("Please set GEMINI_API_KEY in .env file")
        
        self.client = genai.Client(api_key=api_key)
        self.image_model = "gemini-2.5-flash-image"
        self.text_model = "gemini-2.0-flash-exp"
        logger.info("Nano Banana client initialized")
    
    def generate_image_prompt(self, topic: str, post_content: str) -> str:
        """Use Gemini 2.0 to generate optimized image prompt"""
        try:
            # Fixed the long prompt string formatting
            prompt = f"""You are an expert at creating LinkedIn-optimized image generation prompts for AI and technology content that drives professional engagement.

Given this LinkedIn post topic and content, create a detailed, specific image generation prompt that will produce a compelling, business-professional visual that enhances understanding of the concept.

Topic: {topic}

Post Content:
{post_content[:500]}

Create an image prompt with these STRATEGIC requirements:

COMPOSITION & FORMAT:
- Full-frame 16:9 composition with NO borders, NO white backgrounds, NO frames
- Edge-to-edge content filling the entire canvas
- Professional business aesthetic with modern tech elements
- Clean, sophisticated design suitable for C-suite audiences

CONCEPTUAL VISUALIZATION:
- Visual metaphors that illustrate the core AI concept
- Abstract representations of the technical process or innovation
- Conceptual diagrams rendered as beautiful, glowing architectural structures
- Data visualization elements integrated as artistic elements

VISUAL ELEMENTS & STYLE:
- Sophisticated color palette: Deep navy, professional blue, silver, white, with strategic accent colors
- Subtle tech elements: Circuit patterns as background textures, data streams as connecting lines
- Architectural/geometric structures representing AI concepts
- Clean, modern iconography integrated into the composition

BUSINESS PROFESSIONAL AESTHETIC:
- Corporate presentation quality
- Sophisticated lighting (not overly dramatic)
- Clean, organized visual hierarchy
- Professional conference slide or annual report quality

STRICT EXCLUSIONS:
- NO text, words, letters, or typography
- NO white backgrounds, borders, or frames
- NO overly sci-fi or gaming aesthetics
- NO cluttered or busy compositions

TECHNICAL SPECIFICATIONS:
- 16:9 aspect ratio optimized for LinkedIn
- High resolution, professional quality
- Edge-to-edge immersive composition
- Business presentation grade visual clarity

Create an image that a business executive would proudly share, that visually explains {topic} through sophisticated conceptual illustration while maintaining LinkedIn's professional standards.

Return ONLY the optimized image generation prompt."""

            response = self.client.models.generate_content(
                model=self.text_model,
                contents=prompt
            )
            
            image_prompt = response.text.strip()
            
            # Post-process to ensure key requirements
            enhanced_prompt = f"{image_prompt} | Full-bleed edge-to-edge composition, no borders, no white background, immersive cinematic quality, professional LinkedIn banner style."
            
            logger.info(f"Generated image prompt: {enhanced_prompt[:150]}...")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error generating image prompt: {e}")
            return self._fallback_prompt(topic)
    
    def _fallback_prompt(self, topic: str) -> str:
        """Fallback image prompt with full-frame specification"""
        return f"""A stunning hyperrealistic 3D render representing {topic}. 
Full-frame composition with edge-to-edge content, NO white background, NO borders.
Futuristic scene with glowing neural network patterns and neon data streams.
Vibrant cyan, magenta, and purple colors with dramatic cinematic lighting.
Ultra-sharp detail, octane render quality.
Professional tech illustration suitable for LinkedIn banner.
NO text, NO people, NO frames, immersive full-bleed composition."""
    
    def generate_linkedin_image(self, image_prompt: str) -> bytes:
        """Generate image with correct aspect ratio config"""
        try:
            logger.info("Generating 16:9 image with Nano Banana...")
            
            # Create content with text prompt
            text_part = types.Part.from_text(text=image_prompt)
            contents = [types.Content(role="user", parts=[text_part])]
            
            # Create config with image_config containing aspect_ratio
            config = types.GenerateContentConfig(
                temperature=1.0,
                top_p=0.95,
                max_output_tokens=8192,
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9"
                ),
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH", 
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT", 
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT", 
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT", 
                        threshold="BLOCK_NONE"
                    ),
                ]
            )
            
            # Generate image with correct config format
            response = self.client.models.generate_content(
                model=self.image_model,
                contents=contents,
                config=config
            )
            
            if not response:
                logger.error("No response from Gemini image generation")
                return None
            
            # Extract image data from response
            image_data = self._extract_image_data(response)
            
            if not image_data:
                logger.error("Could not extract image data from response")
                return None
            
            # Process and return image data
            return self._process_image_data(image_data)
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _extract_image_data(self, response):
        """Extract image data from Gemini response"""
        # Method 1: Check candidates for inline_data
        if hasattr(response, 'candidates') and response.candidates:
            logger.info(f"Found {len(response.candidates)} candidates")
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        logger.info(f"Found {len(candidate.content.parts)} parts")
                        for part in candidate.content.parts:
                            # Check for inline_data
                            if hasattr(part, 'inline_data') and part.inline_data:
                                if hasattr(part.inline_data, 'data'):
                                    logger.info("✓ Found inline_data")
                                    return part.inline_data.data
                            # Check for blob
                            if hasattr(part, 'blob') and part.blob:
                                logger.info("✓ Found blob")
                                return part.blob
        
        # Method 2: Check for direct text (base64)
        if hasattr(response, 'text'):
            logger.info("Checking text response")
            return response.text
        
        return None
    
    def _process_image_data(self, image_data):
        """Process image data (decode base64 if needed)"""
        # If base64 string
        if isinstance(image_data, str):
            try:
                image_data = image_data.strip()
                decoded_data = base64.b64decode(image_data)
                logger.info(f"✓ Decoded base64 image: {len(decoded_data)} bytes")
                return decoded_data
            except Exception as e:
                logger.error(f"Failed to decode base64: {e}")
                return None
        
        # If already bytes
        if isinstance(image_data, bytes):
            logger.info(f"✓ Got raw image bytes: {len(image_data)} bytes")
            return image_data
        
        # If file-like object
        if hasattr(image_data, 'read'):
            logger.info("✓ Got file-like object")
            return image_data.read()
        
        logger.error(f"Unexpected image data type: {type(image_data)}")
        return None
    
    def save_image(self, image_data: bytes, filepath: str) -> bool:
        """Save and validate image - optimized for LinkedIn"""
        if not image_data:
            logger.error("No image data to save")
            return False
        
        logger.info(f"Attempting to save image: {len(image_data)} bytes")
        
        try:
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Original image - Format: {image.format}, Size: {image.size}, Mode: {image.mode}")
            
            # Convert to RGB if needed
            if image.mode not in ('RGB', 'L'):
                logger.info(f"Converting from {image.mode} to RGB")
                image = image.convert('RGB')
            
            # Resize to LinkedIn optimal size (1200x675 for 16:9)
            linkedin_size = (1200, 675)
            if image.size != linkedin_size:
                image = image.resize(linkedin_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized to LinkedIn optimal: {linkedin_size}")
            
            # Save as high-quality PNG
            image.save(filepath, 'PNG', optimize=True, compress_level=6)
            logger.info(f"✓ Image saved successfully: {filepath}")
            logger.info(f"  Final dimensions: {image.size}")
            return True
            
        except Exception as pil_error:
            logger.warning(f"PIL processing failed: {pil_error}")
            
            # Fallback: direct binary write
            try:
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                file_size = os.path.getsize(filepath)
                logger.info(f"✓ Image saved (direct write): {filepath} ({file_size} bytes)")
                return True
                
            except Exception as write_error:
                logger.error(f"Error saving image: {write_error}")
                return False