import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from .models import Session, EmailHistory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailManager:
    def __init__(self):
        self.email = os.getenv('EMAIL_USERNAME')
        self.password = os.getenv('EMAIL_PASSWORD')
        self.imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.imap_conn = None
        self.smtp_conn = None

    def connect_to_imap(self) -> bool:
        """
        Establish connection to IMAP server.
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.imap_conn:
                try:
                    self.imap_conn.close()
                    self.imap_conn.logout()
                except:
                    pass
            
            self.imap_conn = imaplib.IMAP4_SSL(self.imap_server)
            self.imap_conn.login(self.email, self.password)
            logger.info("Successfully connected to IMAP server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {str(e)}")
            self.imap_conn = None
            return False

    def connect_to_smtp(self) -> None:
        """Establish connection to SMTP server."""
        try:
            self.smtp_conn = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.smtp_conn.starttls()
            self.smtp_conn.login(self.email, self.password)
            logger.info("Successfully connected to SMTP server")
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {str(e)}")
            raise

    def fetch_recent_emails(self, days: int = 1) -> List[Dict]:
        """
        Fetch recent emails from specified folder.
        
        Args:
            days: Number of days of emails to fetch
            
        Returns:
            List of dictionaries containing email information
        """
        # Check if email credentials are configured
        if not self.email or not self.password:
            logger.warning("Email credentials not configured. Please set EMAIL_USERNAME and EMAIL_PASSWORD in .env file")
            return []

        # Try to connect if not connected
        if not self.imap_conn and not self.connect_to_imap():
            return []

        try:
            self.imap_conn.select('INBOX')
            date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
            _, messages = self.imap_conn.search(None, f'(SINCE {date})')
            
            emails = []
            for num in messages[0].split():
                _, msg_data = self.imap_conn.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                message = email.message_from_bytes(email_body)
                
                # Get subject
                subject = ''
                if message['subject']:
                    subject = decode_header(message['subject'])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()

                # Get sender
                sender = message['from']
                if sender:
                    sender = decode_header(message['from'])[0][0]
                    if isinstance(sender, bytes):
                        sender = sender.decode()

                # Get body
                body = self._get_email_content(message)

                emails.append({
                    'from': sender,
                    'subject': subject,
                    'body': body,
                    'date': message['date']
                })

            logger.info(f"Successfully fetched {len(emails)} recent emails")
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            return []

    def send_reply(self, to_address: str, subject: str, body: str) -> bool:
        """
        Send a reply email.
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            body: Email body content
            
        Returns:
            Boolean indicating success/failure
        """
        if not self.smtp_conn:
            self.connect_to_smtp()

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_address
            msg['Subject'] = f"Re: {subject}"

            msg.attach(MIMEText(body, 'plain'))

            self.smtp_conn.send_message(msg)
            logger.info(f"Successfully sent reply to {to_address}")
            return True

        except Exception as e:
            logger.error(f"Failed to send reply: {str(e)}")
            return False

    def _get_email_content(self, email_message: email.message.Message) -> str:
        """Extract email content from email message."""
        content = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        content += part.get_payload(decode=True).decode()
                    except:
                        continue
        else:
            try:
                content = email_message.get_payload(decode=True).decode()
            except:
                content = "Could not decode email body"
        return content

    def close_connections(self) -> None:
        """Close IMAP and SMTP connections."""
        if self.imap_conn:
            try:
                self.imap_conn.close()
                self.imap_conn.logout()
            except:
                pass
        
        if self.smtp_conn:
            try:
                self.smtp_conn.quit()
            except:
                pass
