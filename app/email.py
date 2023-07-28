from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from jinja2 import Environment, select_autoescape, PackageLoader

from app.config import config

env = Environment(
    loader=PackageLoader('app', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

conf = ConnectionConfig(
    MAIL_USERNAME=config.EMAIL_USERNAME,
    MAIL_PASSWORD=config.EMAIL_PASSWORD,
    MAIL_FROM=config.EMAIL_FROM,
    MAIL_PORT=config.EMAIL_PORT,
    MAIL_SERVER=config.EMAIL_HOST,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


class Email:
    def __init__(self, user: str, url: str, emails: list[EmailStr]):
        self.name = user
        self.sender = 'Auth system <FastAPI>'
        self.emails = emails
        self.url = url

    async def send_verification_code(self):
        data = {
            'verification_url': self.url,
            'name': self.name,
            'emails': self.emails
        }
        return await self.send_mail(data, 'Verify your email', 'verification')

    @staticmethod
    async def send_mail(data, subject, template):
        # Generate the HTML template base on the template name
        template = env.get_template(f'{template}.html')
        emails = data.pop('emails', [])
        html = template.render(
            **data,
            subject=subject
        )
        # Define the message options
        message = MessageSchema(
            subject=subject,
            recipients=emails,
            body=html,
            subtype="html"
        )
        # Send the email
        fm = FastMail(conf)
        await fm.send_message(message)
