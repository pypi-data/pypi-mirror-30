from applauncher.kernel import Configuration
import inject
from smtplib import SMTP

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender(object):
    @inject.param("config", Configuration)
    def __init__(self, config):
        self.conf = config.email

    def send_raw_email(self, email_from, email_to, body):
        conf = self.conf
        server = SMTP(conf.smtp_host, conf.smtp_port)

        if conf.use_ttls:
            server.starttls()
        if conf.use_authentication:
            server.login(conf.username, conf.password)
        server.sendmail(email_from, email_to, body)
        server.quit()

    def send_email(self, subject, email_from, email_to, body, mime='plain', codification='utf-8'):
        outer = MIMEMultipart()
        outer.preamble = 'You are not using a MIME-aware mail reader.\n'
        outer['Subject'] = subject
        outer['From'] = email_from

        if isinstance(email_to, list):
            email_to = ",".join(email_to)

        outer['To'] = email_to
        msg = MIMEText(body, mime, codification)
        outer.attach(msg)
        composed = outer.as_string()
        return self.send_raw_email(email_from, email_to, composed)


class EmailBundle(object):
    def __init__(self):
        # The configuration of this bundle. Just an schema about the data required. The kernel will use it to read
        # configuration files, check that everything is fine and provide it to your application.
        self.config_mapping = {
            "email": {
                "smtp_host": None,
                "smtp_port": 587,
                "use_ttls": True,
                "use_authentication": True,
                "username": "",
                "password": ""

            }
        }


