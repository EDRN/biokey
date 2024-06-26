# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: asynchronous tasks.'''

from celery import shared_task
from django.core.mail.message import EmailMessage
import logging, time, base64


_logger = logging.getLogger(__name__)


@shared_task
def _send_email_asynchronously(from_addr, to, subject, body, attachment, delay):
    _logger.info('Sending email to "%s" from "%s" with delay %d', to, from_addr, delay)
    time.sleep(delay)
    if attachment:
        a = [(attachment['name'], base64.b64decode(attachment['data']), attachment['content_type'])]
        _logger.info('Making EmailMessage, subject = %s', subject)
        _logger.info('from_email = %s', from_addr)
        _logger.info('to = %r', to)
        _logger.info('attachments = %r', a)
        _logger.info('body = %s', body)
        message = EmailMessage(subject=subject, from_email=from_addr, to=to, attachments=a, body=body)
    else:
        message = EmailMessage(subject=subject, from_email=from_addr, to=to, body=body)
    message.send()


def send_email(from_addr, to, subject, body, attachment, delay):
    if attachment:
        for field in ('name', 'data', 'content_type'):
            assert field in attachment
        attachment['data'] = base64.b64encode(attachment['data']).decode('utf-8')
    _send_email_asynchronously.delay(from_addr, to, subject, body, attachment, delay)
