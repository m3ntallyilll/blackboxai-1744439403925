from src.app import app
import os

if __name__ == '__main__':
    # Set default environment variables if not set
    if not os.getenv('FLASK_SECRET_KEY'):
        os.environ['FLASK_SECRET_KEY'] = 'dev_key_replace_in_production'
    
    if not os.getenv('STRIPE_PUBLIC_KEY'):
        os.environ['STRIPE_PUBLIC_KEY'] = 'your_stripe_public_key'
    
    if not os.getenv('STRIPE_SECRET_KEY'):
        os.environ['STRIPE_SECRET_KEY'] = 'your_stripe_secret_key'
    
    if not os.getenv('GROQ_API_KEY'):
        os.environ['GROQ_API_KEY'] = 'your_groq_api_key'

    # Run the application
    app.run(host='0.0.0.0', port=8000, debug=True)
