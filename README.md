# MailPhantom - AI-Powered Email Management

MailPhantom is a sophisticated email management system that uses AI to help you organize, analyze, and respond to your emails efficiently. Powered by Groq AI, it provides intelligent email categorization, sentiment analysis, and action item extraction.

## Features

- 🤖 **AI-Powered Analysis**
  - Smart email categorization
  - Sentiment analysis
  - Action item extraction
  - Thread summarization
  - Automated response suggestions

- 📊 **Email Management**
  - Priority inbox organization
  - Automatic email fetching
  - Smart categorization
  - Email analytics and insights

- 🔒 **Security & Authentication**
  - Secure user authentication
  - Subscription management
  - API key management for lifetime users
  - Data encryption

## Subscription Plans

### Monthly Plan ($30/month)
- Full access to AI email management
- Unlimited email processing
- Priority support
- Cloud-based processing

### Lifetime Plan ($100 one-time)
- All features from monthly plan
- Use your own API keys
- Lifetime updates
- Self-hosted option available

## Prerequisites

- Python 3.x
- Email account with IMAP access
- Groq API key (for lifetime plan users)
- Modern web browser
- Stripe account (for payment processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mailphantom.git
cd mailphantom
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
```
# Application Configuration
FLASK_SECRET_KEY=your_secret_key_here
DEBUG=True

# Email Configuration
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_app_specific_password
IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# AI Configuration
GROQ_API_KEY=your_groq_api_key

# Payment Configuration
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
```

## Usage

1. Start the application:
```bash
flask run
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

3. Register an account and choose your subscription plan:
   - Monthly ($30/month) with managed AI processing
   - Lifetime ($100) with your own API key

4. Configure your email settings:
   - Connect your email account
   - Set up processing rules
   - Configure auto-reply templates

5. Monitor and manage your emails:
   - View AI-analyzed emails
   - Track processing history
   - Manage subscription

## Project Structure

```
mailphantom/
├── src/
│   ├── templates/
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── subscription.html
│   │   ├── base.html
│   │   └── ...
│   ├── static/
│   │   └── logo.png
│   ├── models/
│   │   └── subscription.py
│   ├── app.py
│   ├── auth.py
│   ├── email_manager.py
│   └── groq_handler.py
├── config/
│   ├── email_history.yaml
│   └── email_rules.yaml
├── requirements.txt
└── README.md
```

## Security Considerations

- All sensitive data is encrypted
- Secure payment processing via Stripe
- API keys are stored securely
- HTTPS enforced for all connections
- Regular security updates

## Error Handling

The application includes comprehensive error handling:
- Email connection issues
- Payment processing errors
- API failures
- Authentication issues
- Runtime exceptions

All errors are:
- Logged for debugging
- Displayed appropriately in the UI
- Recorded in the history

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## Support

For support:
- Email: support@mailphantom.com
- Discord: [Join our community](https://discord.gg/mailphantom)
- Documentation: [docs.mailphantom.com](https://docs.mailphantom.com)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Groq AI for providing the AI capabilities
- Stripe for payment processing
- The Flask team for the amazing web framework
- Our community of users and contributors
