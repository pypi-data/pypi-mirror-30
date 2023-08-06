'''
Emailer class
Author: Steve Brownfield
Created: 4/15/2018
'''

import smtplib
import pypandoc
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

class Emailer:
    def send_mail(self, send_from, send_to, subject, message, attach_filename,
                  server_address="localhost", port=587, username='', password='',
                  use_tls=True):
        ''' Convert markdown file to pdf and send it as an email attachment.

        :param send_from: from email address
        :param send_to: to email address
        :param subject: email subject
        :param message: email message body
        :param attach_filename: markdown filename to be converted and attached to email
        :param server_address: smtp mail server host name
        :param port: smtp mail server port number
        :param username: server auth username
        :param password: server auth password
        :param use_tls: use TLS mode
        :return: the recipients of the email
        '''

        try:
            pypandoc.convert(attach_filename, 'pdf', 'md', outputfile="attachment.pdf",
                             extra_args=['-V', 'geometry:margin=1.5cm'])
        except ImportError:
            print("warning: pypandoc module not found, could not convert Markdown to pdf")

        fromaddr = send_from
        toaddr = send_to

        msg = MIMEMultipart()

        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject

        body = message
        msg.attach(MIMEText(body, 'plain'))

        filename = "attachment.pdf"
        attachment = open(filename, "rb")

        # it is important to encode_base64 the attachment
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(part)

        server = smtplib.SMTP(server_address, port)
        if use_tls:
            server.starttls()
        server.login(username, password)
        text = msg.as_string()
        recipient = server.sendmail(fromaddr, toaddr, text)
        server.quit()

        return recipient

