# encoding: utf-8

'''🧬🔑 BioKey: email tester.'''


from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Site
from jpl.edrn.biokey.usermgmt.models import EmailSettings
from jpl.edrn.biokey.usermgmt.tasks import send_email
from django.core.mail.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import argparse, smtplib


class Command(BaseCommand):
    help = 'Test email sending'
    _to = 'sean.kelly@jpl.nasa.gov'
    _subject = 'Biokey Email Test'
    _methods = ('smtp', 'django', 'worker')

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('--to', help='Comma-separated list of recipients (default: %(default)s)', default=self._to)
        parser.add_argument('--subject', help='Email subject line (default: %(default)s)', default=self._subject)
        parser.add_argument('--from', help='From address; defaults to whatever is in EmailSettings')
        parser.add_argument(
            '--method', help='How to send the email (default: %(default)s)', default='django', choices=self._methods
        )
        parser.add_argument('message', nargs='+', help='The message body to send')

    def send_worker(self, from_address: str, to: list[str], subject: str, message: str):
        self.stdout.write(f'Calling on worker to send from {from_address} to {to} with zero delay')
        send_email(from_address, to, subject, message, attachment=None, delay=0)

    def send_django(self, from_address: str, to: list[str], subject: str, message: str):
        self.stdout.write(f'Using Django `EmailMessage` to send from {from_address} to {to}')
        message = EmailMessage(subject=subject, from_email=from_address, to=to, body=message)
        self.stdout.write('Sending')
        message.send()

    def send_smtp(self, from_address: str, to: list[str], subject: str, message: str):
        uid, pw = settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD
        host, port = settings.EMAIL_HOST, settings.EMAIL_PORT
        for recipient in to:
            self.stdout.write(f'Using smtplib to send to {recipient}')

            email = MIMEMultipart()
            email['From'] = from_address
            email['To'] = recipient
            email['Subject'] = subject
            email.attach(MIMEText(message, 'plain'))

            smtp_class = smtplib.SMTP_SSL if settings.EMAIL_USE_SSL else smtplib.SMTP

            self.stdout.write(f'Connecting to {host}:{port} using {smtp_class.__name__}')
            with smtp_class(host=host, port=port) as server:
                server.set_debuglevel(True)
                if settings.EMAIL_USE_TLS and not settings.EMAIL_USE_SSL:
                    self.stdout.write('Starting TLS')
                    server.starttls()
                if uid and pw:
                    self.stdout.write(f'Logging in with username {uid}')
                    server.login(uid, pw)
                self.stdout.write(f'Sending message from {from_address}')
                server.sendmail(from_address, recipient, email.as_string())
                server.quit()

    def print_email_configuration(self):
        self.stdout.write('Using the following settings (regardless of method):')
        for attr in ('EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_HOST_USER', 'EMAIL_USE_TLS', 'EMAIL_USE_SSL'):
            setting = getattr(settings, attr, None)
            if setting is not None:
                self.stdout.write(f'{attr}: {setting}')
            else:
                self.stdout.write(f'{attr} not set in Django configuration')
        self.stdout.write('Note that changing the configuration requires restarting the "worker" for it to notice')

    def handle(self, *args, **options):
        message = ' '.join(options['message'])

        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            raise CommandError('No default site found, aborting')
        email_settings = EmailSettings.for_site(site)
        if not email_settings:
            raise CommandError('No EmailSettings found, aborting')

        from_address = options['from'] if options['from'] else email_settings.from_address
        to = [i.strip() for i in options['to'].split(',')]
        subject = options['subject']
        method = options['method']
        self.stdout.write(
            f'Sending from {from_address} to {to} with subject "{subject}" with {method}'
        )
        self.print_email_configuration()

        func = getattr(self, f'send_{method}')
        func(from_address, to, subject, message)
