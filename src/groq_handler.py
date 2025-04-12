import os
import json
from .models import Session, EmailHistory

class GroqHandler:
    def __init__(self):
        # For now, we'll simulate AI responses since we're having issues with the Groq client
        self.api_key = os.getenv('GROQ_API_KEY')

    def analyze_email(self, email_content, sender, subject):
        """
        Analyze email content using simulated AI responses.
        Returns a dictionary containing analysis results.
        """
        try:
            # Simulate AI analysis with predefined responses
            # In production, this would use actual Groq API calls
            analysis = {
                'category': self._determine_category(subject, email_content),
                'importance': self._determine_importance(subject, email_content),
                'sentiment': self._determine_sentiment(email_content),
                'summary': self._generate_summary(email_content),
                'required_action': self._determine_action(email_content)
            }
            return analysis
            
        except Exception as e:
            print(f"Error in email analysis: {str(e)}")
            return {
                'category': 'other',
                'importance': 'medium',
                'sentiment': 'neutral',
                'summary': 'Failed to analyze email content',
                'required_action': None
            }

    def suggest_reply(self, email_content, sender, subject):
        """
        Generate a suggested reply using templates.
        """
        try:
            # Generate a simple template-based reply
            reply = f"""Dear {sender.split('<')[0].strip()},

Thank you for your email regarding "{subject}".

I have received your message and will respond appropriately.

Best regards,
[Your Name]"""
            return reply
            
        except Exception as e:
            print(f"Error generating reply: {str(e)}")
            return "Failed to generate reply suggestion."

    def _determine_category(self, subject, content):
        """Simple rule-based categorization"""
        subject_lower = subject.lower()
        content_lower = content.lower()
        
        if any(word in subject_lower for word in ['urgent', 'asap', 'emergency']):
            return 'urgent'
        elif any(word in subject_lower for word in ['offer', 'discount', 'sale', 'promotion']):
            return 'promotional'
        elif '@' in content_lower or 'meeting' in content_lower:
            return 'personal'
        return 'other'

    def _determine_importance(self, subject, content):
        """Simple rule-based importance assessment"""
        subject_lower = subject.lower()
        content_lower = content.lower()
        
        if any(word in subject_lower for word in ['urgent', 'asap', 'emergency']):
            return 'high'
        elif any(word in content_lower for word in ['important', 'priority']):
            return 'medium'
        return 'low'

    def _determine_sentiment(self, content):
        """Simple rule-based sentiment analysis"""
        content_lower = content.lower()
        
        positive_words = ['thank', 'good', 'great', 'excellent', 'appreciate']
        negative_words = ['bad', 'issue', 'problem', 'complaint', 'sorry']
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'

    def _generate_summary(self, content):
        """Generate a simple summary"""
        # Take first 200 characters as summary
        summary = content[:200].strip()
        if len(content) > 200:
            summary += '...'
        return summary

    def _determine_action(self, content):
        """Simple rule-based action determination"""
        content_lower = content.lower()
        
        if 'please reply' in content_lower:
            return 'Reply needed'
        elif 'review' in content_lower:
            return 'Review required'
        elif 'confirm' in content_lower:
            return 'Confirmation needed'
        return None
