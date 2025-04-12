import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from .config import Config
from .models import Session, EmailHistory, EmailCategory, ActionType
import os
from groq.base_client import BaseClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI email assistant. Analyze the email content and provide:
1. Importance level (high, medium, low)
2. Category (urgent, personal, promotional, other)
3. Required actions
4. Key points
5. Sentiment analysis
6. Suggested response (if needed)

Be concise but thorough in your analysis."""

class GroqHandler:
    def __init__(self):
        self.config = Config()
        self.client = None
        try:
            api_key = os.getenv('GROQ_API_KEY') or getattr(self.config, 'GROQ_API_KEY', None)
            if api_key:
                self.client = BaseClient(api_key=api_key)
            else:
                logger.warning("No Groq API key found, AI features will be limited")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
        
        self.db = Session()

    def analyze_email(self, email_content: str, sender: str, subject: str = "") -> Dict:
        """Analyze email content using Groq AI."""
        if not self.client:
            logger.warning("Groq client is not available. Falling back to basic analysis.")
            return self._basic_analysis(email_content, sender)

        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Subject: {subject}\nFrom: {sender}\nContent: {email_content}"}
            ]

            completion = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=messages,
                temperature=0.5,
                max_tokens=500
            )
            
            analysis = completion.choices[0].message.content
            
            # Parse AI response and create structured output
            result = self._parse_ai_analysis(analysis)
            
            # Save to database
            history_entry = EmailHistory(
                action=ActionType.ANALYSIS.value,
                sender=sender,
                subject=subject,
                category=result['category'],
                ai_analysis=analysis,
                sentiment=result.get('sentiment', 'neutral'),
                key_points=result.get('key_points', ''),
                suggested_actions=result.get('required_action', '')
            )
            self.db.add(history_entry)
            self.db.commit()
            
            return result
        except Exception as e:
            logger.error(f"Failed to analyze email: {str(e)}")
            return self._basic_analysis(email_content, sender)

    def _basic_analysis(self, email_content: str, sender: str) -> Dict:
        """Fallback basic analysis when AI is unavailable."""
        importance = "medium"
        category = "other"
        required_action = "none"
        
        if any(word in email_content.lower() for word in ["urgent", "important", "asap", "emergency"]):
            importance = "high"
            category = "urgent"
        
        if "@gmail.com" in sender.lower() or "@yahoo.com" in sender.lower():
            category = "personal"
        elif "newsletter" in email_content.lower() or "subscribe" in email_content.lower():
            category = "promotional"
        
        return {
            "importance": importance,
            "category": category,
            "required_action": required_action,
            "key_points": "Basic analysis (AI unavailable)",
            "sentiment": "neutral"
        }

    def _parse_ai_analysis(self, analysis: str) -> Dict:
        """Parse AI analysis into structured format."""
        try:
            lines = analysis.split('\n')
            result = {
                "importance": "medium",
                "category": "other",
                "required_action": "",
                "key_points": "",
                "sentiment": "neutral"
            }
            
            for line in lines:
                line = line.lower().strip()
                if "importance" in line:
                    if "high" in line:
                        result["importance"] = "high"
                    elif "low" in line:
                        result["importance"] = "low"
                elif "category" in line:
                    if "urgent" in line:
                        result["category"] = "urgent"
                    elif "personal" in line:
                        result["category"] = "personal"
                    elif "promotional" in line:
                        result["category"] = "promotional"
                elif "sentiment" in line:
                    if "positive" in line:
                        result["sentiment"] = "positive"
                    elif "negative" in line:
                        result["sentiment"] = "negative"
                elif "key points" in line:
                    result["key_points"] = line.split(":", 1)[1].strip() if ":" in line else line
                elif "action" in line:
                    result["required_action"] = line.split(":", 1)[1].strip() if ":" in line else line
            
            return result
        except Exception as e:
            logger.error(f"Failed to parse AI analysis: {str(e)}")
            return {
                "importance": "medium",
                "category": "other",
                "required_action": "",
                "key_points": "Failed to parse AI analysis",
                "sentiment": "neutral"
            }
