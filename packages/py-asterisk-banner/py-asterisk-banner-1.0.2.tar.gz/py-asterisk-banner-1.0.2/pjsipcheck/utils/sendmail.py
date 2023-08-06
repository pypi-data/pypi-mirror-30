from jinja2 import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pjsipcheck import settings

import smtplib
import logging


class SendMail:
    def __init__(self):
        self.log = logging.getLogger(settings.LOGGER_NAME)

        self.from_email = settings.CONFIG.get_email('from')
        self.to_email = settings.CONFIG.get_email('to')

    @staticmethod
    def get_template(template, args):
        file = open(settings.TEMPLATES_DIR + template, 'r').read()
        return Template(file).render(args)

    def send(self, ip_address, line):

        self.log.debug("Enviado email a %s" % self.to_email)

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Bloqueada la IP " + ip_address
            msg['From'] = self.from_email
            msg['To'] = self.to_email

            # Create the body of the message (a plain-text and an HTML version).
            args_render = {
                'ip_address': ip_address,
                'line': line
            }

            text = self.get_template("block_email.txt", args_render)
            html = self.get_template("block_email.html", args_render)

            # Record the MIME types of both parts - text/plain and text/html.
            text_mail = MIMEText(text, 'plain')
            html_mail = MIMEText(html, 'html')

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            msg.attach(text_mail)
            msg.attach(html_mail)

            # Send the message via local SMTP server.
            s = smtplib.SMTP('localhost')
            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            s.sendmail(self.from_email, self.to_email, msg.as_string())
            s.quit()

        except Exception as ex:
            self.log.error(str(ex))
            raise
