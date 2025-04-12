import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the email AI agent."""
    
    # Email Settings
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    
    # Groq API Settings
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
    
    # Database Settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/email_manager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Payment Settings
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration variables are set."""
        required_vars = [
            'EMAIL_USERNAME',
            'EMAIL_PASSWORD',
            'GROQ_API_KEY',
            'STRIPE_PUBLIC_KEY',
            'STRIPE_SECRET_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
    
    @classmethod
    def initialize(cls):
        """Initialize and validate the configuration."""
        # Create instance directory if it doesn't exist
        os.makedirs('instance', exist_ok=True)
        cls.validate_config()
        return cls
