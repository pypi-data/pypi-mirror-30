import datetime
import logging
import copy
from email.mime.text import MIMEText
import smtplib
import traceback

from pi_watchdog import periodic_task


class NotifierTask(periodic_task.PeriodicTaskLoop):
    def __init__(self, config):
        self.config = config
        self.norifier_conf = config['notification']
        self.interval = 60 * int(self.norifier_conf['interval'].rstrip('m'))
        self.messages = []
        super(NotifierTask, self).__init__()

    def execute_periodic_task(self):
        try:
            if self.messages:
                self.send()
        except Exception as e:
            logging.exception("Notifier exception")

    def send(self):
        messages = copy.copy(self.messages)
        self.messages = []
        try:
            self._send_mail(
                messages,
                'RIG notification',
                sender=self.norifier_conf['from_email'],
                sender_password=self.norifier_conf['from_email_pass'],
                recipient=self.norifier_conf['email'],
                smtp_server=self.norifier_conf['smtp_server']
            )
        except Exception as e:
            logging.exception('Failed to send email.')
            messages.extend(self.messages)
            self.messages = messages

    @staticmethod
    def _send_mail(messages, subject, sender, sender_password, recipient, smtp_server):
        data = '\n----------------\n'.join(messages)
        msg = MIMEText(data)

        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        server = smtplib.SMTP(smtp_server)
        server.ehlo()
        server.starttls()
        server.login(sender, sender_password)
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()

    def add_message(self, message):
        last_traceback = traceback.format_exc()
        formatted_msg = ' - '.join([str(datetime.datetime.now()), message, last_traceback])
        self.messages.append(formatted_msg)

    def get_interval(self):
        return self.interval

    def stop(self):
        self.send()
        super(NotifierTask, self).stop()